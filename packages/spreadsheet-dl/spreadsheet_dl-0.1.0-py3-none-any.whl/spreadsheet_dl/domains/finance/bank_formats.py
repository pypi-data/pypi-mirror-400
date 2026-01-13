"""Extended Bank Format Support.

Provides support for 50+ bank and credit card CSV formats with:
- YAML-based format definitions
- Format builder for custom banks
- Format validation
- Auto-detection improvements

"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class BankFormatDefinition:
    """Complete bank CSV format definition.

    Defines how to parse CSV exports from a specific bank or
    credit card provider.

    Attributes:
        id: Unique format identifier (e.g., "chase_checking").
        name: Display name (e.g., "Chase Bank - Checking").
        institution: Financial institution name.
        format_type: Type of account (checking, credit, etc.).
        date_column: Column name for transaction date.
        date_format: strptime format for dates.
        amount_column: Column name for amount.
        description_column: Column name for description.
        debit_column: Optional separate debit column.
        credit_column: Optional separate credit column.
        memo_column: Optional memo/notes column.
        category_column: Optional category column.
        reference_column: Optional reference/check number column.
        balance_column: Optional running balance column.
        skip_rows: Number of header rows to skip.
        encoding: File encoding.
        delimiter: CSV delimiter.
        expense_is_negative: Whether expenses are negative amounts.
        header_patterns: Patterns for auto-detection.
        notes: Additional notes about this format.
    """

    id: str
    name: str
    institution: str = ""
    format_type: str = "checking"  # checking, credit, savings, investment
    date_column: str = "Date"
    date_format: str = "%m/%d/%Y"
    amount_column: str = "Amount"
    description_column: str = "Description"
    debit_column: str | None = None
    credit_column: str | None = None
    memo_column: str | None = None
    category_column: str | None = None
    reference_column: str | None = None
    balance_column: str | None = None
    skip_rows: int = 0
    encoding: str = "utf-8-sig"
    delimiter: str = ","
    expense_is_negative: bool = True
    header_patterns: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "institution": self.institution,
            "format_type": self.format_type,
            "date_column": self.date_column,
            "date_format": self.date_format,
            "amount_column": self.amount_column,
            "description_column": self.description_column,
            "debit_column": self.debit_column,
            "credit_column": self.credit_column,
            "memo_column": self.memo_column,
            "category_column": self.category_column,
            "reference_column": self.reference_column,
            "balance_column": self.balance_column,
            "skip_rows": self.skip_rows,
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "expense_is_negative": self.expense_is_negative,
            "header_patterns": self.header_patterns,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BankFormatDefinition:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            institution=data.get("institution", ""),
            format_type=data.get("format_type", "checking"),
            date_column=data.get("date_column", "Date"),
            date_format=data.get("date_format", "%m/%d/%Y"),
            amount_column=data.get("amount_column", "Amount"),
            description_column=data.get("description_column", "Description"),
            debit_column=data.get("debit_column"),
            credit_column=data.get("credit_column"),
            memo_column=data.get("memo_column"),
            category_column=data.get("category_column"),
            reference_column=data.get("reference_column"),
            balance_column=data.get("balance_column"),
            skip_rows=data.get("skip_rows", 0),
            encoding=data.get("encoding", "utf-8-sig"),
            delimiter=data.get("delimiter", ","),
            expense_is_negative=data.get("expense_is_negative", True),
            header_patterns=data.get("header_patterns", []),
            notes=data.get("notes", ""),
        )

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        lines = [
            f"id: {self.id}",
            f"name: {self.name}",
            f"institution: {self.institution}",
            f"format_type: {self.format_type}",
            "",
            "# Column mappings",
            f"date_column: {self.date_column}",
            f"date_format: '{self.date_format}'",
            f"amount_column: {self.amount_column}",
            f"description_column: {self.description_column}",
        ]

        if self.debit_column:
            lines.append(f"debit_column: {self.debit_column}")
        if self.credit_column:
            lines.append(f"credit_column: {self.credit_column}")
        if self.memo_column:
            lines.append(f"memo_column: {self.memo_column}")
        if self.category_column:
            lines.append(f"category_column: {self.category_column}")
        if self.reference_column:
            lines.append(f"reference_column: {self.reference_column}")
        if self.balance_column:
            lines.append(f"balance_column: {self.balance_column}")

        lines.extend(
            [
                "",
                "# File settings",
                f"skip_rows: {self.skip_rows}",
                f"encoding: {self.encoding}",
                f"delimiter: '{self.delimiter}'",
                f"expense_is_negative: {str(self.expense_is_negative).lower()}",
            ]
        )

        if self.header_patterns:
            lines.append("")
            lines.append("# Auto-detection patterns")
            lines.append("header_patterns:")
            for pattern in self.header_patterns:
                lines.append(f"  - '{pattern}'")

        if self.notes:
            lines.append("")
            lines.append(f"notes: {self.notes}")

        return "\n".join(lines)


# Comprehensive bank format definitions (50+ formats)
BUILTIN_FORMATS: dict[str, BankFormatDefinition] = {
    # Major US Banks - Checking
    "chase_checking": BankFormatDefinition(
        id="chase_checking",
        name="Chase Bank - Checking",
        institution="Chase",
        format_type="checking",
        date_column="Posting Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        header_patterns=["posting date", "description", "amount", "type", "balance"],
    ),
    "chase_credit": BankFormatDefinition(
        id="chase_credit",
        name="Chase Credit Card",
        institution="Chase",
        format_type="credit",
        date_column="Transaction Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        category_column="Category",
        header_patterns=[
            "transaction date",
            "post date",
            "description",
            "category",
            "amount",
        ],
    ),
    "bank_of_america_checking": BankFormatDefinition(
        id="bank_of_america_checking",
        name="Bank of America - Checking",
        institution="Bank of America",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        reference_column="Reference Number",
        header_patterns=["date", "description", "amount", "running bal"],
    ),
    "bank_of_america_credit": BankFormatDefinition(
        id="bank_of_america_credit",
        name="Bank of America Credit Card",
        institution="Bank of America",
        format_type="credit",
        date_column="Posted Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Payee",
        reference_column="Reference Number",
        header_patterns=[
            "posted date",
            "reference number",
            "payee",
            "address",
            "amount",
        ],
    ),
    "wells_fargo_checking": BankFormatDefinition(
        id="wells_fargo_checking",
        name="Wells Fargo - Checking",
        institution="Wells Fargo",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        header_patterns=["date", "amount", "description"],
    ),
    "wells_fargo_credit": BankFormatDefinition(
        id="wells_fargo_credit",
        name="Wells Fargo Credit Card",
        institution="Wells Fargo",
        format_type="credit",
        date_column="Transaction Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "citi_checking": BankFormatDefinition(
        id="citi_checking",
        name="Citibank - Checking",
        institution="Citibank",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",
        description_column="Description",
        expense_is_negative=False,
        header_patterns=["date", "description", "debit", "credit"],
    ),
    "citi_credit": BankFormatDefinition(
        id="citi_credit",
        name="Citi Credit Card",
        institution="Citibank",
        format_type="credit",
        date_column="Date",
        date_format="%m/%d/%Y",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",
        description_column="Description",
        expense_is_negative=False,
    ),
    "capital_one_checking": BankFormatDefinition(
        id="capital_one_checking",
        name="Capital One - Checking",
        institution="Capital One",
        format_type="checking",
        date_column="Transaction Date",
        date_format="%Y-%m-%d",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",
        description_column="Description",
        expense_is_negative=False,
        header_patterns=[
            "transaction date",
            "transaction description",
            "debit",
            "credit",
        ],
    ),
    "capital_one_credit": BankFormatDefinition(
        id="capital_one_credit",
        name="Capital One Credit Card",
        institution="Capital One",
        format_type="credit",
        date_column="Transaction Date",
        date_format="%Y-%m-%d",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",
        description_column="Description",
        category_column="Category",
        expense_is_negative=False,
        header_patterns=[
            "transaction date",
            "posted date",
            "card no",
            "description",
            "category",
            "debit",
            "credit",
        ],
    ),
    "usaa_checking": BankFormatDefinition(
        id="usaa_checking",
        name="USAA - Checking",
        institution="USAA",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
        header_patterns=["date", "description", "original description", "amount"],
    ),
    "usaa_credit": BankFormatDefinition(
        id="usaa_credit",
        name="USAA Credit Card",
        institution="USAA",
        format_type="credit",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
    ),
    "pnc_checking": BankFormatDefinition(
        id="pnc_checking",
        name="PNC Bank - Checking",
        institution="PNC",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        reference_column="Reference Number",
    ),
    "td_bank_checking": BankFormatDefinition(
        id="td_bank_checking",
        name="TD Bank - Checking",
        institution="TD Bank",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        debit_column="Debit",
        credit_column="Credit",
        amount_column="Debit",
        description_column="Description",
        expense_is_negative=False,
    ),
    "us_bank_checking": BankFormatDefinition(
        id="us_bank_checking",
        name="US Bank - Checking",
        institution="US Bank",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Name",
        memo_column="Memo",
    ),
    "regions_checking": BankFormatDefinition(
        id="regions_checking",
        name="Regions Bank - Checking",
        institution="Regions",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "fifth_third_checking": BankFormatDefinition(
        id="fifth_third_checking",
        name="Fifth Third Bank - Checking",
        institution="Fifth Third",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "huntington_checking": BankFormatDefinition(
        id="huntington_checking",
        name="Huntington Bank - Checking",
        institution="Huntington",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "ally_bank": BankFormatDefinition(
        id="ally_bank",
        name="Ally Bank",
        institution="Ally",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
        header_patterns=["date", "time", "amount", "type", "description"],
    ),
    "discover_bank": BankFormatDefinition(
        id="discover_bank",
        name="Discover Bank - Savings",
        institution="Discover",
        format_type="savings",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Credit Cards
    "amex": BankFormatDefinition(
        id="amex",
        name="American Express",
        institution="American Express",
        format_type="credit",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        category_column="Category",
        expense_is_negative=False,  # Amex shows positive for charges
        header_patterns=["date", "description", "card member", "amount"],
    ),
    "amex_rewards": BankFormatDefinition(
        id="amex_rewards",
        name="American Express (Rewards Format)",
        institution="American Express",
        format_type="credit",
        date_column="Date",
        date_format="%m/%d/%y",
        amount_column="Amount",
        description_column="Description",
        expense_is_negative=False,
    ),
    "discover_credit": BankFormatDefinition(
        id="discover_credit",
        name="Discover Credit Card",
        institution="Discover",
        format_type="credit",
        date_column="Trans. Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        category_column="Category",
        header_patterns=[
            "trans. date",
            "post date",
            "description",
            "amount",
            "category",
        ],
    ),
    "barclays_credit": BankFormatDefinition(
        id="barclays_credit",
        name="Barclays Credit Card",
        institution="Barclays",
        format_type="credit",
        date_column="Transaction Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "synchrony_credit": BankFormatDefinition(
        id="synchrony_credit",
        name="Synchrony Credit Card",
        institution="Synchrony",
        format_type="credit",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Online Banks and Fintechs
    "simple_bank": BankFormatDefinition(
        id="simple_bank",
        name="Simple Bank",
        institution="Simple (closed)",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
        category_column="Category",
    ),
    "chime": BankFormatDefinition(
        id="chime",
        name="Chime",
        institution="Chime",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "sofi": BankFormatDefinition(
        id="sofi",
        name="SoFi Money",
        institution="SoFi",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "marcus": BankFormatDefinition(
        id="marcus",
        name="Marcus by Goldman Sachs",
        institution="Marcus",
        format_type="savings",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "wealthfront": BankFormatDefinition(
        id="wealthfront",
        name="Wealthfront Cash",
        institution="Wealthfront",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
    ),
    "betterment": BankFormatDefinition(
        id="betterment",
        name="Betterment Checking",
        institution="Betterment",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
    ),
    "varo": BankFormatDefinition(
        id="varo",
        name="Varo Bank",
        institution="Varo",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "current": BankFormatDefinition(
        id="current",
        name="Current Banking",
        institution="Current",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Credit Unions
    "navy_federal": BankFormatDefinition(
        id="navy_federal",
        name="Navy Federal Credit Union",
        institution="Navy Federal",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        balance_column="Balance",
    ),
    "penfed": BankFormatDefinition(
        id="penfed",
        name="PenFed Credit Union",
        institution="PenFed",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "alliant": BankFormatDefinition(
        id="alliant",
        name="Alliant Credit Union",
        institution="Alliant",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "becu": BankFormatDefinition(
        id="becu",
        name="BECU",
        institution="BECU",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "dcu": BankFormatDefinition(
        id="dcu",
        name="Digital Federal Credit Union",
        institution="DCU",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Investment Accounts
    "fidelity": BankFormatDefinition(
        id="fidelity",
        name="Fidelity Investments",
        institution="Fidelity",
        format_type="investment",
        date_column="Run Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Action",
    ),
    "vanguard": BankFormatDefinition(
        id="vanguard",
        name="Vanguard",
        institution="Vanguard",
        format_type="investment",
        date_column="Trade Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Transaction Description",
    ),
    "schwab": BankFormatDefinition(
        id="schwab",
        name="Charles Schwab",
        institution="Schwab",
        format_type="investment",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "etrade": BankFormatDefinition(
        id="etrade",
        name="E*TRADE",
        institution="E*TRADE",
        format_type="investment",
        date_column="TransactionDate",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "robinhood": BankFormatDefinition(
        id="robinhood",
        name="Robinhood",
        institution="Robinhood",
        format_type="investment",
        date_column="Activity Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Payment Services
    "paypal": BankFormatDefinition(
        id="paypal",
        name="PayPal",
        institution="PayPal",
        format_type="checking",
        date_column="Date",
        date_format='"%m/%d/%Y"',
        amount_column="Net",
        description_column="Name",
        header_patterns=[
            "date",
            "time",
            "name",
            "type",
            "status",
            "currency",
            "gross",
            "fee",
            "net",
        ],
    ),
    "venmo": BankFormatDefinition(
        id="venmo",
        name="Venmo",
        institution="Venmo",
        format_type="checking",
        date_column="Datetime",
        date_format="%Y-%m-%dT%H:%M:%S",
        amount_column="Amount (total)",
        description_column="Note",
        header_patterns=[
            "id",
            "datetime",
            "type",
            "status",
            "note",
            "from",
            "to",
            "amount",
        ],
    ),
    "zelle": BankFormatDefinition(
        id="zelle",
        name="Zelle",
        institution="Zelle",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Memo",
    ),
    "cashapp": BankFormatDefinition(
        id="cashapp",
        name="Cash App",
        institution="Cash App",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Notes",
    ),
    "apple_card": BankFormatDefinition(
        id="apple_card",
        name="Apple Card",
        institution="Apple",
        format_type="credit",
        date_column="Transaction Date",
        date_format="%m/%d/%Y",
        amount_column="Amount (USD)",
        description_column="Merchant",
        category_column="Category",
        header_patterns=[
            "transaction date",
            "clearing date",
            "description",
            "merchant",
            "category",
            "amount",
        ],
    ),
    # International Banks
    "hsbc": BankFormatDefinition(
        id="hsbc",
        name="HSBC",
        institution="HSBC",
        format_type="checking",
        date_column="Date",
        date_format="%d/%m/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "barclays_uk": BankFormatDefinition(
        id="barclays_uk",
        name="Barclays UK",
        institution="Barclays",
        format_type="checking",
        date_column="Date",
        date_format="%d/%m/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    "rbc": BankFormatDefinition(
        id="rbc",
        name="Royal Bank of Canada",
        institution="RBC",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
    ),
    "td_canada": BankFormatDefinition(
        id="td_canada",
        name="TD Canada Trust",
        institution="TD Canada",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
    ),
    # Generic formats
    "generic": BankFormatDefinition(
        id="generic",
        name="Generic CSV",
        institution="Generic",
        format_type="checking",
        date_column="Date",
        date_format="%Y-%m-%d",
        amount_column="Amount",
        description_column="Description",
    ),
    "mint": BankFormatDefinition(
        id="mint",
        name="Mint Export",
        institution="Mint",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Description",
        category_column="Category",
        header_patterns=[
            "date",
            "description",
            "original description",
            "amount",
            "transaction type",
            "category",
        ],
    ),
    "ynab": BankFormatDefinition(
        id="ynab",
        name="YNAB Export",
        institution="YNAB",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Payee",
        category_column="Category",
    ),
    "quicken": BankFormatDefinition(
        id="quicken",
        name="Quicken QIF Export",
        institution="Quicken",
        format_type="checking",
        date_column="Date",
        date_format="%m/%d/%Y",
        amount_column="Amount",
        description_column="Payee",
        category_column="Category",
    ),
}


class BankFormatRegistry:
    """Registry for bank format definitions.

    Manages both built-in and custom formats with persistence.

    Example:
        ```python
        registry = BankFormatRegistry()

        # List all formats
        for fmt in registry.list_formats():
            print(f"{fmt.id}: {fmt.name}")

        # Get specific format
        chase = registry.get_format("chase_checking")

        # Add custom format
        registry.add_custom_format(my_format)
        ```
    """

    def __init__(
        self,
        custom_dir: Path | str | None = None,
    ) -> None:
        """Initialize the registry.

        Args:
            custom_dir: Directory for custom format files.
        """
        self._builtin = BUILTIN_FORMATS.copy()
        self._custom: dict[str, BankFormatDefinition] = {}

        if custom_dir:
            self._custom_dir = Path(custom_dir)
        else:
            self._custom_dir = (
                Path.home() / ".config" / "spreadsheet-dl" / "bank-formats"
            )

        self._load_custom_formats()

    def _load_custom_formats(self) -> None:
        """Load custom formats from directory."""
        if not self._custom_dir.exists():
            return

        for file_path in self._custom_dir.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                fmt = BankFormatDefinition.from_dict(data)
                self._custom[fmt.id] = fmt
            except (json.JSONDecodeError, KeyError, ValueError):
                pass  # Skip invalid files

    def _save_custom_format(self, fmt: BankFormatDefinition) -> None:
        """Save a custom format to file."""
        self._custom_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._custom_dir / f"{fmt.id}.json"
        with open(file_path, "w") as f:
            json.dump(fmt.to_dict(), f, indent=2)

    def get_format(self, format_id: str) -> BankFormatDefinition | None:
        """Get a format by ID.

        Args:
            format_id: Format identifier.

        Returns:
            Format definition or None if not found.
        """
        # Check custom first (allows overriding built-in)
        if format_id in self._custom:
            return self._custom[format_id]
        return self._builtin.get(format_id)

    def list_formats(
        self,
        institution: str | None = None,
        format_type: str | None = None,
        include_custom: bool = True,
    ) -> list[BankFormatDefinition]:
        """List all available formats.

        Args:
            institution: Filter by institution.
            format_type: Filter by type (checking, credit, etc.).
            include_custom: Include custom formats.

        Returns:
            List of format definitions.
        """
        formats = list(self._builtin.values())
        if include_custom:
            formats.extend(self._custom.values())

        if institution:
            institution_lower = institution.lower()
            formats = [f for f in formats if institution_lower in f.institution.lower()]

        if format_type:
            formats = [f for f in formats if f.format_type == format_type]

        return sorted(formats, key=lambda f: f.name)

    def list_institutions(self) -> list[str]:
        """Get list of unique institutions."""
        institutions = set()
        for fmt in self._builtin.values():
            if fmt.institution:
                institutions.add(fmt.institution)
        for fmt in self._custom.values():
            if fmt.institution:
                institutions.add(fmt.institution)
        return sorted(institutions)

    def add_custom_format(self, fmt: BankFormatDefinition) -> None:
        """Add a custom format.

        Args:
            fmt: Format definition to add.
        """
        self._custom[fmt.id] = fmt
        self._save_custom_format(fmt)

    def remove_custom_format(self, format_id: str) -> bool:
        """Remove a custom format.

        Args:
            format_id: ID of format to remove.

        Returns:
            True if removed, False if not found.
        """
        if format_id not in self._custom:
            return False

        del self._custom[format_id]

        file_path = self._custom_dir / f"{format_id}.json"
        if file_path.exists():
            file_path.unlink()

        return True

    def detect_format(
        self,
        csv_path: Path | str,
        *,
        sample_rows: int = 5,
    ) -> BankFormatDefinition | None:
        """Auto-detect CSV format.

        Args:
            csv_path: Path to CSV file.
            sample_rows: Number of rows to sample for detection.

        Returns:
            Detected format or None.
        """
        csv_path = Path(csv_path)

        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                headers_lower = [h.lower().strip() for h in headers]
        except (OSError, UnicodeDecodeError, csv.Error):
            # File access errors, encoding issues, or CSV parsing errors
            return None

        # Score each format based on header matches
        best_score = 0
        best_format = None

        for fmt in self.list_formats():
            score = self._score_format(fmt, headers_lower)
            if score > best_score:
                best_score = score
                best_format = fmt

        # Require minimum score
        if best_score >= 2:
            return best_format

        return None

    def _score_format(
        self,
        fmt: BankFormatDefinition,
        headers_lower: list[str],
    ) -> int:
        """Score how well a format matches headers."""
        score = 0

        # Check header patterns
        if fmt.header_patterns:
            matches = sum(
                1 for pattern in fmt.header_patterns if pattern.lower() in headers_lower
            )
            score += matches * 2

        # Check column names
        columns_to_check = [
            fmt.date_column,
            fmt.amount_column,
            fmt.description_column,
        ]
        if fmt.debit_column:
            columns_to_check.append(fmt.debit_column)
        if fmt.credit_column:
            columns_to_check.append(fmt.credit_column)

        for col in columns_to_check:
            if col.lower() in headers_lower:
                score += 1

        return score

    def validate_format(
        self,
        fmt: BankFormatDefinition,
        csv_path: Path | str,
    ) -> list[str]:
        """Validate a format against a CSV file.

        Args:
            fmt: Format to validate.
            csv_path: Path to CSV file.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        csv_path = Path(csv_path)

        try:
            with open(csv_path, newline="", encoding=fmt.encoding) as f:
                for _ in range(fmt.skip_rows):
                    next(f, None)
                reader = csv.DictReader(f, delimiter=fmt.delimiter)
                headers = reader.fieldnames or []
                row = next(reader, None)
        except Exception as e:
            return [f"Failed to read file: {e}"]

        # Check required columns
        if fmt.date_column not in headers:
            errors.append(f"Missing date column: {fmt.date_column}")

        if fmt.debit_column and fmt.credit_column:
            if fmt.debit_column not in headers:
                errors.append(f"Missing debit column: {fmt.debit_column}")
            if fmt.credit_column not in headers:
                errors.append(f"Missing credit column: {fmt.credit_column}")
        else:
            if fmt.amount_column not in headers:
                errors.append(f"Missing amount column: {fmt.amount_column}")

        if fmt.description_column not in headers:
            errors.append(f"Missing description column: {fmt.description_column}")

        # Try to parse first row
        if row and not errors:
            try:
                date_str = row.get(fmt.date_column, "")
                datetime.strptime(date_str.strip('"'), fmt.date_format)
            except ValueError:
                errors.append(
                    f"Date format mismatch: '{date_str}' doesn't match '{fmt.date_format}'"
                )

        return errors

    def __iter__(self) -> Iterator[BankFormatDefinition]:
        """Iterate over all formats."""
        yield from self._builtin.values()
        yield from self._custom.values()

    def __len__(self) -> int:
        """Return total number of formats."""
        return len(self._builtin) + len(self._custom)


class FormatBuilder:
    """Interactive builder for creating custom bank formats.

    Example:
        ```python
        builder = FormatBuilder()
        builder.set_institution("My Bank")
        builder.set_date_column("Transaction Date", "%Y-%m-%d")
        builder.set_amount_column("Amount")
        builder.set_description_column("Details")

        format_def = builder.build("my_bank")
        ```
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self._data: dict[str, Any] = {
            "id": "",
            "name": "",
            "institution": "",
            "format_type": "checking",
            "date_column": "Date",
            "date_format": "%Y-%m-%d",
            "amount_column": "Amount",
            "description_column": "Description",
            "skip_rows": 0,
            "encoding": "utf-8-sig",
            "delimiter": ",",
            "expense_is_negative": True,
            "header_patterns": [],
        }

    def set_institution(self, name: str) -> FormatBuilder:
        """Set the financial institution name."""
        self._data["institution"] = name
        return self

    def set_name(self, name: str) -> FormatBuilder:
        """Set the format display name."""
        self._data["name"] = name
        return self

    def set_format_type(self, format_type: str) -> FormatBuilder:
        """Set the account type (checking, credit, savings, investment)."""
        self._data["format_type"] = format_type
        return self

    def set_date_column(
        self,
        column: str,
        date_format: str = "%Y-%m-%d",
    ) -> FormatBuilder:
        """Set the date column and format."""
        self._data["date_column"] = column
        self._data["date_format"] = date_format
        return self

    def set_amount_column(self, column: str) -> FormatBuilder:
        """Set the amount column."""
        self._data["amount_column"] = column
        return self

    def set_debit_credit_columns(
        self,
        debit: str,
        credit: str,
    ) -> FormatBuilder:
        """Set separate debit and credit columns."""
        self._data["debit_column"] = debit
        self._data["credit_column"] = credit
        self._data["expense_is_negative"] = False
        return self

    def set_description_column(self, column: str) -> FormatBuilder:
        """Set the description column."""
        self._data["description_column"] = column
        return self

    def set_memo_column(self, column: str) -> FormatBuilder:
        """Set the memo/notes column."""
        self._data["memo_column"] = column
        return self

    def set_category_column(self, column: str) -> FormatBuilder:
        """Set the category column."""
        self._data["category_column"] = column
        return self

    def set_reference_column(self, column: str) -> FormatBuilder:
        """Set the reference number column."""
        self._data["reference_column"] = column
        return self

    def set_balance_column(self, column: str) -> FormatBuilder:
        """Set the running balance column."""
        self._data["balance_column"] = column
        return self

    def set_skip_rows(self, count: int) -> FormatBuilder:
        """Set number of header rows to skip."""
        self._data["skip_rows"] = count
        return self

    def set_encoding(self, encoding: str) -> FormatBuilder:
        """Set file encoding."""
        self._data["encoding"] = encoding
        return self

    def set_delimiter(self, delimiter: str) -> FormatBuilder:
        """Set CSV delimiter."""
        self._data["delimiter"] = delimiter
        return self

    def set_expense_is_negative(self, value: bool) -> FormatBuilder:
        """Set whether expenses are negative amounts."""
        self._data["expense_is_negative"] = value
        return self

    def add_header_pattern(self, pattern: str) -> FormatBuilder:
        """Add a header pattern for auto-detection."""
        self._data["header_patterns"].append(pattern)
        return self

    def set_notes(self, notes: str) -> FormatBuilder:
        """Set notes about this format."""
        self._data["notes"] = notes
        return self

    def from_csv_headers(
        self,
        csv_path: Path | str,
    ) -> FormatBuilder:
        """Infer format from CSV headers.

        Args:
            csv_path: Path to sample CSV file.

        Returns:
            Self for chaining.
        """
        csv_path = Path(csv_path)

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, [])

        # Store headers as patterns
        self._data["header_patterns"] = [h.lower().strip() for h in headers if h]

        # Try to guess column mappings
        for header in headers:
            header_lower = header.lower().strip()

            if "date" in header_lower:
                self._data["date_column"] = header

            if header_lower in ("amount", "amt", "total"):
                self._data["amount_column"] = header

            if "debit" in header_lower:
                self._data["debit_column"] = header

            if "credit" in header_lower:
                self._data["credit_column"] = header

            if header_lower in (
                "description",
                "desc",
                "details",
                "payee",
                "name",
                "merchant",
            ):
                self._data["description_column"] = header

            if header_lower in ("memo", "notes", "note"):
                self._data["memo_column"] = header

            if header_lower in ("category", "type"):
                self._data["category_column"] = header

            if header_lower in (
                "reference",
                "ref",
                "check",
                "check #",
                "reference number",
            ):
                self._data["reference_column"] = header

            if header_lower in ("balance", "running balance", "available balance"):
                self._data["balance_column"] = header

        return self

    def build(self, format_id: str) -> BankFormatDefinition:
        """Build the format definition.

        Args:
            format_id: Unique identifier for the format.

        Returns:
            BankFormatDefinition instance.
        """
        self._data["id"] = format_id

        if not self._data["name"]:
            self._data["name"] = (
                f"{self._data['institution']} - {self._data['format_type'].title()}"
            )

        return BankFormatDefinition.from_dict(self._data)


# Convenience functions


def get_format(format_id: str) -> BankFormatDefinition | None:
    """Get a bank format by ID."""
    registry = BankFormatRegistry()
    return registry.get_format(format_id)


def list_formats(
    institution: str | None = None,
    format_type: str | None = None,
) -> list[BankFormatDefinition]:
    """List available bank formats."""
    registry = BankFormatRegistry()
    return registry.list_formats(institution=institution, format_type=format_type)


def detect_format(csv_path: Path | str) -> BankFormatDefinition | None:
    """Auto-detect CSV format."""
    registry = BankFormatRegistry()
    return registry.detect_format(csv_path)


def count_formats() -> int:
    """Get total number of supported formats."""
    return len(BUILTIN_FORMATS)
