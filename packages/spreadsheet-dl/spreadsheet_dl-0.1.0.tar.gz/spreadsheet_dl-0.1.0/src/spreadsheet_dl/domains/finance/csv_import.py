"""CSV Import - Import transactions from bank CSV exports.

Provides parsing and categorization of bank transaction exports
from common financial institutions.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory, ExpenseEntry
from spreadsheet_dl.progress import BatchProgress

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class BankFormat:
    """Configuration for a bank's CSV format."""

    name: str
    date_column: str
    amount_column: str
    description_column: str
    date_format: str = "%m/%d/%Y"
    # Some banks have separate debit/credit columns
    debit_column: str | None = None
    credit_column: str | None = None
    # Column for memo/notes
    memo_column: str | None = None
    # Skip header rows
    skip_rows: int = 0
    # Amount sign convention (negative = expense for most banks)
    expense_is_negative: bool = True
    # Optional preprocessing for amount
    amount_preprocessor: Callable[[str], str] | None = None


# Pre-configured bank formats
BANK_FORMATS: dict[str, BankFormat] = {
    "chase": BankFormat(
        name="Chase",
        date_column="Posting Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=True,
    ),
    "chase_credit": BankFormat(
        name="Chase Credit Card",
        date_column="Transaction Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=True,
    ),
    "bank_of_america": BankFormat(
        name="Bank of America",
        date_column="Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=True,
    ),
    "wells_fargo": BankFormat(
        name="Wells Fargo",
        date_column="Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=True,
    ),
    "capital_one": BankFormat(
        name="Capital One",
        date_column="Transaction Date",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",  # Primary for expenses
        description_column="Description",
        date_format="%Y-%m-%d",
        expense_is_negative=False,
    ),
    "discover": BankFormat(
        name="Discover",
        date_column="Trans. Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=True,
    ),
    "amex": BankFormat(
        name="American Express",
        date_column="Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%m/%d/%Y",
        expense_is_negative=False,  # Amex shows positive for charges
    ),
    "usaa": BankFormat(
        name="USAA",
        date_column="Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%Y-%m-%d",
        expense_is_negative=True,
    ),
    "generic": BankFormat(
        name="Generic CSV",
        date_column="Date",
        amount_column="Amount",
        description_column="Description",
        date_format="%Y-%m-%d",
        expense_is_negative=True,
    ),
}


@dataclass
class CategoryRule:
    """Rule for automatic transaction categorization."""

    pattern: str  # Regex pattern to match description
    category: ExpenseCategory
    case_sensitive: bool = False
    # Priority (higher = checked first)
    priority: int = 0


# Default categorization rules
DEFAULT_CATEGORY_RULES: list[CategoryRule] = [
    # Groceries
    CategoryRule(
        r"whole foods|trader joe|safeway|kroger|publix|wegmans|aldi|costco|walmart.*grocery|target.*grocery|instacart|grocery|supermarket|fresh market",
        ExpenseCategory.GROCERIES,
        priority=10,
    ),
    # Restaurants/Dining
    CategoryRule(
        r"mcdonald|burger king|wendy|chick-fil-a|chipotle|starbucks|dunkin|panera|subway|pizza|doordash|uber eats|grubhub|restaurant|cafe|diner|grill|kitchen|tavern|bistro",
        ExpenseCategory.DINING_OUT,
        priority=10,
    ),
    # Transportation
    CategoryRule(
        r"shell|exxon|chevron|bp|speedway|wawa|circle k|gas|fuel|uber|lyft|parking|toll|transit|metro|subway fare|bus fare|amtrak|car wash",
        ExpenseCategory.TRANSPORTATION,
        priority=10,
    ),
    # Utilities
    CategoryRule(
        r"electric|water|gas bill|utility|power|energy|sewage|waste management|internet|comcast|verizon fios|at&t.*internet|spectrum",
        ExpenseCategory.UTILITIES,
        priority=10,
    ),
    # Healthcare
    CategoryRule(
        r"pharmacy|cvs|walgreens|rite aid|doctor|hospital|medical|health|dental|vision|optom|urgent care|clinic|lab|prescription",
        ExpenseCategory.HEALTHCARE,
        priority=10,
    ),
    # Entertainment
    CategoryRule(
        r"netflix|hulu|disney\+|amazon prime video|hbo|spotify|apple music|youtube|movie|cinema|theater|concert|ticketmaster|stubhub|bowling|arcade|golf|gym|fitness",
        ExpenseCategory.ENTERTAINMENT,
        priority=10,
    ),
    # Subscriptions
    CategoryRule(
        r"netflix|hulu|disney|spotify|apple.*music|amazon prime|youtube premium|subscription|monthly fee|membership",
        ExpenseCategory.SUBSCRIPTIONS,
        priority=5,
    ),
    # Housing (payments/rent)
    CategoryRule(
        r"rent|mortgage|hoa|property tax|home insurance|landlord",
        ExpenseCategory.HOUSING,
        priority=10,
    ),
    # Insurance
    CategoryRule(
        r"insurance|geico|progressive|state farm|allstate|liberty mutual|usaa.*insurance",
        ExpenseCategory.INSURANCE,
        priority=10,
    ),
    # Clothing
    CategoryRule(
        r"target|walmart|amazon.*clothing|old navy|gap|h&m|zara|nordstrom|macy|tjx|marshalls|ross|kohls|clothing|apparel|shoes",
        ExpenseCategory.CLOTHING,
        priority=5,
    ),
    # Personal Care
    CategoryRule(
        r"haircut|salon|barber|spa|nail|beauty|cosmetic|ulta|sephora|bath.*body",
        ExpenseCategory.PERSONAL,
        priority=10,
    ),
    # Education
    CategoryRule(
        r"tuition|school|university|college|course|class|book|textbook|udemy|coursera|linkedin learning",
        ExpenseCategory.EDUCATION,
        priority=10,
    ),
    # Gifts
    CategoryRule(
        r"gift|present|hallmark|flower|1800flowers|edible arrangements",
        ExpenseCategory.GIFTS,
        priority=10,
    ),
    # Amazon (general shopping - lower priority)
    CategoryRule(r"amazon\.com|amzn", ExpenseCategory.MISCELLANEOUS, priority=1),
]


@dataclass
class TransactionCategorizer:
    """Automatic transaction categorizer using pattern matching.

    Uses regex patterns to categorize transactions based on
    merchant descriptions.
    """

    rules: list[CategoryRule] = field(
        default_factory=lambda: DEFAULT_CATEGORY_RULES.copy()
    )
    default_category: ExpenseCategory = ExpenseCategory.MISCELLANEOUS
    _compiled_rules: list[tuple[re.Pattern[str], ExpenseCategory, int]] = field(
        default_factory=list, init=False
    )

    def __post_init__(self) -> None:
        """Compile regex patterns."""
        self._compile_rules()

    def _compile_rules(self) -> None:
        """Compile all regex patterns and sort by priority."""
        self._compiled_rules = []
        for rule in self.rules:
            flags = 0 if rule.case_sensitive else re.IGNORECASE
            pattern = re.compile(rule.pattern, flags)
            self._compiled_rules.append((pattern, rule.category, rule.priority))
        # Sort by priority (highest first)
        self._compiled_rules.sort(key=lambda x: x[2], reverse=True)

    def add_rule(
        self,
        pattern: str,
        category: ExpenseCategory,
        priority: int = 0,
        case_sensitive: bool = False,
    ) -> None:
        """Add a custom categorization rule.

        Args:
            pattern: Regex pattern to match.
            category: Category to assign.
            priority: Rule priority (higher = checked first).
            case_sensitive: Whether pattern is case-sensitive.
        """
        self.rules.append(CategoryRule(pattern, category, case_sensitive, priority))
        self._compile_rules()

    def categorize(self, description: str) -> ExpenseCategory:
        """Categorize a transaction based on its description.

        Args:
            description: Transaction description/merchant name.

        Returns:
            Matched category or default category.
        """
        for pattern, category, _ in self._compiled_rules:
            if pattern.search(description):
                return category
        return self.default_category

    def categorize_with_confidence(
        self,
        description: str,
    ) -> tuple[ExpenseCategory, float]:
        """Categorize with confidence score.

        Args:
            description: Transaction description.

        Returns:
            Tuple of (category, confidence) where confidence is 0.0-1.0.
        """
        for pattern, category, priority in self._compiled_rules:
            if pattern.search(description):
                # Higher priority rules = higher confidence
                confidence = min(1.0, 0.5 + (priority / 20))
                return category, confidence
        return self.default_category, 0.3


class CSVImporter:
    """Import transactions from bank CSV files.

    Parses CSV exports from various banks and converts them
    to ExpenseEntry objects with automatic categorization.
    """

    def __init__(
        self,
        bank_format: BankFormat | str = "generic",
        categorizer: TransactionCategorizer | None = None,
    ) -> None:
        """Initialize CSV importer.

        Args:
            bank_format: Bank format configuration or name of preset.
            categorizer: Transaction categorizer (uses default if None).
        """
        if isinstance(bank_format, str):
            if bank_format not in BANK_FORMATS:
                raise ValueError(
                    f"Unknown bank format: {bank_format}. "
                    f"Available: {list(BANK_FORMATS.keys())}"
                )
            self.format = BANK_FORMATS[bank_format]
        else:
            self.format = bank_format

        self.categorizer = categorizer or TransactionCategorizer()

    def import_file(
        self,
        csv_path: Path | str,
        filter_expenses_only: bool = True,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ExpenseEntry]:
        """Import transactions from a CSV file.

        Args:
            csv_path: Path to CSV file.
            filter_expenses_only: Only import expenses (not income).
            start_date: Filter transactions from this date.
            end_date: Filter transactions until this date.

        Returns:
            List of ExpenseEntry objects.
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        entries = []

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            # Skip header rows if configured
            for _ in range(self.format.skip_rows):
                next(f)

            reader = csv.DictReader(f)

            # Convert reader to list to get row count for progress
            rows = list(reader)
            total_rows = len(rows)
            use_progress = total_rows > 100

            if use_progress:
                with BatchProgress(total_rows, "Importing transactions") as progress:
                    for row in rows:
                        entry = self._process_import_row(
                            row, filter_expenses_only, start_date, end_date
                        )
                        if entry:
                            entries.append(entry)
                        progress.update()
            else:
                for row in rows:
                    entry = self._process_import_row(
                        row, filter_expenses_only, start_date, end_date
                    )
                    if entry:
                        entries.append(entry)

        return entries

    def _process_import_row(
        self,
        row: dict[str, str],
        filter_expenses_only: bool,
        start_date: date | None,
        end_date: date | None,
    ) -> ExpenseEntry | None:
        """Process a single import row with filtering."""
        entry = self._parse_row(row)
        if entry is None:
            return None

        # Filter by date range
        if start_date and entry.date < start_date:
            return None
        if end_date and entry.date > end_date:
            return None

        # Filter expenses only
        # For expense_is_negative format: negative = expense, positive = income
        # For expense_is_positive format: positive = expense, negative = income
        if filter_expenses_only:
            if self.format.expense_is_negative and entry.amount > 0:
                return None  # Skip income (positive in expense_is_negative format)
            elif not self.format.expense_is_negative and entry.amount < 0:
                return None  # Skip income (negative in expense_is_positive format)

        # Always store amounts as positive in ExpenseEntry
        return ExpenseEntry(
            date=entry.date,
            category=entry.category,
            description=entry.description,
            amount=abs(entry.amount),
            notes=entry.notes,
        )

    def _parse_row(self, row: dict[str, str]) -> ExpenseEntry | None:
        """Parse a CSV row into an ExpenseEntry."""
        try:
            # Parse date
            date_str = row.get(self.format.date_column, "").strip()
            if not date_str:
                return None
            trans_date = datetime.strptime(date_str, self.format.date_format).date()

            # Parse amount
            amount = self._parse_amount(row)
            if amount is None or amount == 0:
                return None

            # Get description
            description = row.get(self.format.description_column, "").strip()
            if not description:
                description = "Unknown transaction"

            # Get memo/notes if available
            notes = ""
            if self.format.memo_column:
                notes = row.get(self.format.memo_column, "").strip()

            # Categorize
            category = self.categorizer.categorize(description)

            return ExpenseEntry(
                date=trans_date,
                category=category,
                description=description[:100],  # Limit length
                amount=Decimal(str(amount)),  # Preserve sign for filtering
                notes=notes[:200] if notes else "",
            )
        except (ValueError, KeyError):
            # Skip invalid rows
            return None

    def _parse_amount(self, row: dict[str, str]) -> float | None:
        """Parse amount from row, handling various formats."""
        # Try debit/credit columns first
        if self.format.debit_column and self.format.credit_column:
            debit = self._clean_amount(row.get(self.format.debit_column, ""))
            credit = self._clean_amount(row.get(self.format.credit_column, ""))
            # Return debit as expense (positive), credit as income (negative)
            if debit:
                return debit
            elif credit:
                return -credit
            return None

        # Single amount column
        amount_str = row.get(self.format.amount_column, "").strip()
        if not amount_str:
            return None

        # Apply preprocessor if configured
        if self.format.amount_preprocessor:
            amount_str = self.format.amount_preprocessor(amount_str)

        amount = self._clean_amount(amount_str)
        if amount is None:
            return None

        # Apply sign convention
        if self.format.expense_is_negative:
            # Negative amounts are expenses, positive are income
            # Return as-is to preserve sign for filtering
            return amount
        else:
            # Positive amounts are expenses, need to negate income
            # Return as-is to preserve sign for filtering
            return amount

    def _clean_amount(self, amount_str: str) -> float | None:
        """Clean and parse amount string."""
        if not amount_str:
            return None
        # Remove currency symbols, commas, whitespace
        cleaned = re.sub(r"[$,\s]", "", amount_str)
        # Handle parentheses for negative (accounting format)
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def detect_format(csv_path: Path | str) -> str | None:
        """Attempt to detect the bank format from CSV headers.

        Args:
            csv_path: Path to CSV file.

        Returns:
            Bank format name or None if unknown.
        """
        csv_path = Path(csv_path)
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
                headers_lower = [h.lower().strip() for h in headers]
            except StopIteration:
                return None

        # Check for known formats (order matters - more specific first)
        header_patterns = {
            "chase": ["posting date", "description", "amount"],
            "chase_credit": ["transaction date", "description", "amount", "type"],
            "capital_one": ["transaction date", "debit", "credit"],
            "amex": ["date", "description", "amount", "card member"],
            # Don't auto-detect bank_of_america as it's too generic and has specific date format
            # "bank_of_america": ["date", "description", "amount"],
        }

        for format_name, required in header_patterns.items():
            if all(r in headers_lower for r in required):
                return format_name

        return "generic"


def import_bank_csv(
    csv_path: Path | str,
    bank: str = "auto",
    filter_expenses: bool = True,
) -> list[ExpenseEntry]:
    """Convenience function to import bank CSV.

    Args:
        csv_path: Path to CSV file.
        bank: Bank name or "auto" for auto-detection.
        filter_expenses: Only import expenses.

    Returns:
        List of ExpenseEntry objects.
    """
    csv_path = Path(csv_path)

    if bank == "auto":
        detected = CSVImporter.detect_format(csv_path)
        bank = detected or "generic"

    importer = CSVImporter(bank)
    return importer.import_file(csv_path, filter_expenses_only=filter_expenses)
