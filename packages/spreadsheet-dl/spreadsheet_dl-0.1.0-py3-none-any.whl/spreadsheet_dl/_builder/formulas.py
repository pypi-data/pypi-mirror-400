"""Formula builder and dependency tracking.

Provides type-safe formula construction with 100+ spreadsheet functions
and circular reference detection.

Security:
    - Cell reference validation to prevent formula injection
    - Strict regex patterns for cell/range references
    - Protection against ODF formula syntax escape
"""

from __future__ import annotations

import re

from spreadsheet_dl._builder.exceptions import CircularReferenceError, FormulaError
from spreadsheet_dl._builder.references import CellRef, RangeRef, SheetRef

# Security: Strict cell reference patterns
_CELL_REF_PATTERN = re.compile(r"^(\$?[A-Z]+\$?\d+)$")
_RANGE_REF_PATTERN = re.compile(r"^(\$?[A-Z]+\$?\d+):(\$?[A-Z]+\$?\d+)$")
_COLUMN_REF_PATTERN = re.compile(r"^(\$?[A-Z]+):(\$?[A-Z]+)$")
_SHEET_REF_PATTERN = re.compile(r"^[A-Za-z0-9_][\w\s]*$")


def sanitize_cell_ref(ref: str) -> str:
    """Sanitize and validate cell reference to prevent formula injection.

    Validates that the reference matches expected patterns:
    - A1, $A$1, AB123 (cell reference)
    - A1:B10, $A$1:$B$10 (range reference)
    - A:Z, $A:$Z (column reference)

    Args:
        ref: Cell or range reference string

    Returns:
        Validated reference string

    Raises:
        FormulaError: If reference contains invalid characters or patterns

    Examples:
        >>> sanitize_cell_ref("A1")
        'A1'
        >>> sanitize_cell_ref("A1:B10")
        'A1:B10'
        >>> sanitize_cell_ref('A1];WEBSERVICE("http://evil.com")')  # doctest: +SKIP
        FormulaError: Invalid cell reference
    """
    ref = ref.strip()

    # Handle sheet references (Sheet!A1 or 'Sheet Name'!A1)
    cell_part = ref
    if "!" in ref:
        parts = ref.rsplit("!", 1)
        if len(parts) == 2:
            # Validate only the cell part after the !
            cell_part = parts[1]

    # Check for formula injection patterns in cell part
    if any(char in cell_part for char in [";", "(", ")"]):
        raise FormulaError(
            f"Invalid characters in cell reference: {ref}. "
            "Cell references cannot contain: ; ( )"
        )

    # Validate against known patterns
    if _CELL_REF_PATTERN.match(cell_part):
        return ref
    if _RANGE_REF_PATTERN.match(cell_part):
        return ref
    if _COLUMN_REF_PATTERN.match(cell_part):
        return ref

    raise FormulaError(
        f"Invalid cell reference: {ref}. Valid formats: A1, $A$1, A1:B10, A:Z, Sheet!A1"
    )


def sanitize_sheet_name(name: str) -> str:
    """Sanitize sheet name to prevent injection attacks.

    Args:
        name: Sheet name

    Returns:
        Validated sheet name

    Raises:
        FormulaError: If sheet name contains invalid characters
    """
    name = name.strip()

    if not _SHEET_REF_PATTERN.match(name):
        raise FormulaError(
            f"Invalid sheet name: {name}. "
            "Sheet names must start with letter/number and contain only "
            "alphanumeric characters, underscores, and spaces."
        )

    return name


class FormulaBuilder:
    """Type-safe formula builder for ODF formulas with 100+ functions.

    Provides methods for common spreadsheet functions with
    proper ODF syntax generation, including:
    - Mathematical functions (SUM, AVERAGE, PRODUCT, SUMPRODUCT, trigonometry)
    - Statistical functions (STDEV, VAR, CORREL, FORECAST, regression)
    - Financial functions (PMT, PV, FV, NPV, IRR, depreciation)
    - Date/time functions (DATE, NOW, NETWORKDAYS, WORKDAY)
    - Lookup functions (VLOOKUP, HLOOKUP, INDEX, MATCH, OFFSET)
    - Text functions (CONCATENATE, LEFT, RIGHT, FIND, TEXTJOIN)
    - Logical functions (IF, AND, OR, NOT, XOR, CHOOSE)
    - Array formula support

    Features:
        - 100+ formula functions implemented
        - Type-safe formula construction
        - Circular reference detection (via FormulaDependencyGraph)
        - ODF-compliant formula syntax
        - Performance optimized

    Examples:
        f = FormulaBuilder()

        # Simple SUM
        formula = f.sum(f.range("A2", "A100"))
        # -> "of:=SUM([.A2:A100])"

        # Financial: Monthly payment
        formula = f.pmt(f.cell("B1"), f.cell("B2"), f.cell("B3"))
        # -> "of:=PMT([.B1];[.B2];[.B3])"

        # Lookup: INDEX/MATCH
        formula = f.index_match(
            f.range("B:B", "B:B"),
            f.match(f.cell("A2"), f.range("A:A", "A:A")),
        )

        # Statistical: Correlation
        formula = f.correl(f.range("A2", "A10"), f.range("B2", "B10"))
        # -> "of:=CORREL([.A2:A10];[.B2:B10])"
    """

    # ODF formula prefix
    PREFIX = "of:="

    def cell(self, ref: str) -> CellRef:
        """Create cell reference."""
        return CellRef(ref)

    def range(self, start: str, end: str) -> RangeRef:
        """Create range reference (same sheet)."""
        return RangeRef(start, end)

    def sheet(self, name: str) -> SheetRef:
        """Create sheet reference for cross-sheet formulas."""
        return SheetRef(name)

    def named_range(self, name: str) -> str:
        """Reference a named range in a formula.

        Args:
            name: Named range name

        Returns:
            ODF named range reference
        """
        return f"[{name}]"

    def _format_ref(self, ref: CellRef | RangeRef | str) -> str:
        """Format a reference for formula use with security validation."""
        if isinstance(ref, str):
            # Sanitize string references to prevent injection
            sanitized = sanitize_cell_ref(ref)
            return f"[.{sanitized}]"
        elif isinstance(ref, CellRef):
            return f"[.{ref}]"
        else:
            return str(ref)

    def _format_value(self, val: CellRef | RangeRef | str | float | int) -> str:
        """Format a value (reference or literal) for formula use."""
        if isinstance(val, (CellRef, RangeRef)):
            return self._format_ref(val)
        elif isinstance(val, str) and (val[0].isalpha() or val[0] == "$"):
            # Looks like a cell reference
            return f"[.{val}]"
        else:
            return str(val)

    # =========================================================================
    # Mathematical Functions
    # =========================================================================

    def sum(self, *refs: RangeRef | str) -> str:
        """Create SUM formula.

        Args:
            *refs: One or more cell references or ranges to sum

        Returns:
            SUM formula string

        Examples:
            formula().sum("A1:A10")  # Single range
            formula().sum("A1", "B1", "C1")  # Multiple cells
        """
        if len(refs) == 1:
            return f"{self.PREFIX}SUM({self._format_ref(refs[0])})"
        else:
            # Multiple references - join with semicolons
            parts = [self._format_ref(r) for r in refs]
            return f"{self.PREFIX}SUM({';'.join(parts)})"

    def sumif(
        self,
        criteria_range: RangeRef | str,
        criteria: CellRef | str,
        sum_range: RangeRef | str,
    ) -> str:
        """Create SUMIF formula."""
        cr = self._format_ref(criteria_range)
        crit = self._format_value(criteria)
        sr = self._format_ref(sum_range)
        return f"{self.PREFIX}SUMIF({cr};{crit};{sr})"

    def sumifs(
        self,
        sum_range: RangeRef | str,
        *criteria_pairs: tuple[RangeRef | str, CellRef | str],
    ) -> str:
        """Create SUMIFS formula (multiple criteria).

        Args:
            sum_range: Range to sum
            criteria_pairs: Pairs of (criteria_range, criteria)

        Returns:
            ODF formula string
        """
        sr = self._format_ref(sum_range)
        parts = [sr]
        for criteria_range, criteria in criteria_pairs:
            parts.append(self._format_ref(criteria_range))
            parts.append(self._format_value(criteria))
        return f"{self.PREFIX}SUMIFS({';'.join(parts)})"

    def subtract(self, cell1: str, cell2: str) -> str:
        """Create subtraction formula."""
        return f"{self.PREFIX}[.{cell1}]-[.{cell2}]"

    def multiply(self, cell1: str, cell2: str) -> str:
        """Create multiplication formula."""
        return f"{self.PREFIX}[.{cell1}]*[.{cell2}]"

    def divide(self, cell1: str, cell2: str, default: str = "0") -> str:
        """Create division formula with zero check."""
        return f"{self.PREFIX}IF([.{cell2}]<>0;[.{cell1}]/[.{cell2}];{default})"

    def abs(self, ref: CellRef | str) -> str:
        """Create ABS formula."""
        return f"{self.PREFIX}ABS({self._format_value(ref)})"

    def round(self, ref: CellRef | str, decimals: int = 0) -> str:
        """Create ROUND formula."""
        return f"{self.PREFIX}ROUND({self._format_value(ref)};{decimals})"

    def roundup(self, ref: CellRef | str, decimals: int = 0) -> str:
        """Create ROUNDUP formula."""
        return f"{self.PREFIX}ROUNDUP({self._format_value(ref)};{decimals})"

    def rounddown(self, ref: CellRef | str, decimals: int = 0) -> str:
        """Create ROUNDDOWN formula."""
        return f"{self.PREFIX}ROUNDDOWN({self._format_value(ref)};{decimals})"

    def mod(self, number: CellRef | str, divisor: CellRef | str | int) -> str:
        """Create MOD formula."""
        return f"{self.PREFIX}MOD({self._format_value(number)};{self._format_value(divisor)})"

    def power(self, base: CellRef | str, exponent: CellRef | str | float) -> str:
        """Create POWER formula."""
        return f"{self.PREFIX}POWER({self._format_value(base)};{self._format_value(exponent)})"

    def sqrt(self, ref: CellRef | str) -> str:
        """Create SQRT formula."""
        return f"{self.PREFIX}SQRT({self._format_value(ref)})"

    def ceiling(
        self, number: CellRef | str, significance: CellRef | str | float = 1
    ) -> str:
        """Create CEILING formula (round up to nearest multiple)."""
        return f"{self.PREFIX}CEILING({self._format_value(number)};{self._format_value(significance)})"

    def floor(
        self, number: CellRef | str, significance: CellRef | str | float = 1
    ) -> str:
        """Create FLOOR formula (round down to nearest multiple)."""
        return f"{self.PREFIX}FLOOR({self._format_value(number)};{self._format_value(significance)})"

    def int_func(self, ref: CellRef | str) -> str:
        """Create INT formula (round down to nearest integer)."""
        return f"{self.PREFIX}INT({self._format_value(ref)})"

    def trunc(self, ref: CellRef | str, decimals: int = 0) -> str:
        """Create TRUNC formula (truncate to specified decimals)."""
        return f"{self.PREFIX}TRUNC({self._format_value(ref)};{decimals})"

    def sign(self, ref: CellRef | str) -> str:
        """Create SIGN formula (returns -1, 0, or 1)."""
        return f"{self.PREFIX}SIGN({self._format_value(ref)})"

    def gcd(self, *numbers: CellRef | str | int) -> str:
        """Create GCD formula (greatest common divisor)."""
        parts = [self._format_value(n) for n in numbers]
        return f"{self.PREFIX}GCD({';'.join(parts)})"

    def lcm(self, *numbers: CellRef | str | int) -> str:
        """Create LCM formula (least common multiple)."""
        parts = [self._format_value(n) for n in numbers]
        return f"{self.PREFIX}LCM({';'.join(parts)})"

    def product(self, *refs: RangeRef | str) -> str:
        """Create PRODUCT formula (multiply all values)."""
        parts = [self._format_ref(r) for r in refs]
        return f"{self.PREFIX}PRODUCT({';'.join(parts)})"

    def sumproduct(self, *arrays: RangeRef | str) -> str:
        """Create SUMPRODUCT formula (sum of products of corresponding ranges).

        - PHASE0-005: Complete FormulaBuilder with 100+ functions
        """
        parts = [self._format_ref(a) for a in arrays]
        return f"{self.PREFIX}SUMPRODUCT({';'.join(parts)})"

    def quotient(self, numerator: CellRef | str, denominator: CellRef | str) -> str:
        """Create QUOTIENT formula (integer portion of division)."""
        return f"{self.PREFIX}QUOTIENT({self._format_value(numerator)};{self._format_value(denominator)})"

    def exp(self, ref: CellRef | str) -> str:
        """Create EXP formula (e raised to power)."""
        return f"{self.PREFIX}EXP({self._format_value(ref)})"

    def ln(self, ref: CellRef | str) -> str:
        """Create LN formula (natural logarithm)."""
        return f"{self.PREFIX}LN({self._format_value(ref)})"

    def log(self, number: CellRef | str, base: CellRef | str | int = 10) -> str:
        """Create LOG formula (logarithm to specified base)."""
        return (
            f"{self.PREFIX}LOG({self._format_value(number)};{self._format_value(base)})"
        )

    def log10(self, ref: CellRef | str) -> str:
        """Create LOG10 formula (base 10 logarithm)."""
        return f"{self.PREFIX}LOG10({self._format_value(ref)})"

    def pi(self) -> str:
        """Create PI formula (value of pi)."""
        return f"{self.PREFIX}PI()"

    def radians(self, degrees: CellRef | str) -> str:
        """Create RADIANS formula (convert degrees to radians)."""
        return f"{self.PREFIX}RADIANS({self._format_value(degrees)})"

    def degrees(self, radians: CellRef | str) -> str:
        """Create DEGREES formula (convert radians to degrees)."""
        return f"{self.PREFIX}DEGREES({self._format_value(radians)})"

    def sin(self, ref: CellRef | str) -> str:
        """Create SIN formula."""
        return f"{self.PREFIX}SIN({self._format_value(ref)})"

    def cos(self, ref: CellRef | str) -> str:
        """Create COS formula."""
        return f"{self.PREFIX}COS({self._format_value(ref)})"

    def tan(self, ref: CellRef | str) -> str:
        """Create TAN formula."""
        return f"{self.PREFIX}TAN({self._format_value(ref)})"

    def asin(self, ref: CellRef | str) -> str:
        """Create ASIN formula (arcsine)."""
        return f"{self.PREFIX}ASIN({self._format_value(ref)})"

    def acos(self, ref: CellRef | str) -> str:
        """Create ACOS formula (arccosine)."""
        return f"{self.PREFIX}ACOS({self._format_value(ref)})"

    def atan(self, ref: CellRef | str) -> str:
        """Create ATAN formula (arctangent)."""
        return f"{self.PREFIX}ATAN({self._format_value(ref)})"

    def atan2(self, x: CellRef | str, y: CellRef | str) -> str:
        """Create ATAN2 formula (arctangent of x/y)."""
        return f"{self.PREFIX}ATAN2({self._format_value(x)};{self._format_value(y)})"

    # =========================================================================
    # Statistical Functions
    # =========================================================================

    def average(self, ref: RangeRef | str) -> str:
        """Create AVERAGE formula."""
        return f"{self.PREFIX}AVERAGE({self._format_ref(ref)})"

    def averageif(
        self,
        criteria_range: RangeRef | str,
        criteria: CellRef | str,
        average_range: RangeRef | str | None = None,
    ) -> str:
        """Create AVERAGEIF formula."""
        cr = self._format_ref(criteria_range)
        crit = self._format_value(criteria)
        if average_range:
            ar = self._format_ref(average_range)
            return f"{self.PREFIX}AVERAGEIF({cr};{crit};{ar})"
        return f"{self.PREFIX}AVERAGEIF({cr};{crit})"

    def count(self, ref: RangeRef | str) -> str:
        """Create COUNT formula (count numbers)."""
        return f"{self.PREFIX}COUNT({self._format_ref(ref)})"

    def counta(self, ref: RangeRef | str) -> str:
        """Create COUNTA formula (count non-empty)."""
        return f"{self.PREFIX}COUNTA({self._format_ref(ref)})"

    def countblank(self, ref: RangeRef | str) -> str:
        """Create COUNTBLANK formula."""
        return f"{self.PREFIX}COUNTBLANK({self._format_ref(ref)})"

    def countif(
        self,
        criteria_range: RangeRef | str,
        criteria: CellRef | str,
    ) -> str:
        """Create COUNTIF formula."""
        cr = self._format_ref(criteria_range)
        crit = self._format_value(criteria)
        return f"{self.PREFIX}COUNTIF({cr};{crit})"

    def countifs(
        self,
        *criteria_pairs: tuple[RangeRef | str, CellRef | str],
    ) -> str:
        """Create COUNTIFS formula (multiple criteria)."""
        parts = []
        for criteria_range, criteria in criteria_pairs:
            parts.append(self._format_ref(criteria_range))
            parts.append(self._format_value(criteria))
        return f"{self.PREFIX}COUNTIFS({';'.join(parts)})"

    def max(self, ref: RangeRef | str) -> str:
        """Create MAX formula."""
        return f"{self.PREFIX}MAX({self._format_ref(ref)})"

    def min(self, ref: RangeRef | str) -> str:
        """Create MIN formula."""
        return f"{self.PREFIX}MIN({self._format_ref(ref)})"

    def median(self, ref: RangeRef | str) -> str:
        """Create MEDIAN formula."""
        return f"{self.PREFIX}MEDIAN({self._format_ref(ref)})"

    def stdev(self, ref: RangeRef | str) -> str:
        """Create STDEV formula (sample standard deviation)."""
        return f"{self.PREFIX}STDEV({self._format_ref(ref)})"

    def stdevp(self, ref: RangeRef | str) -> str:
        """Create STDEVP formula (population standard deviation)."""
        return f"{self.PREFIX}STDEVP({self._format_ref(ref)})"

    def var(self, ref: RangeRef | str) -> str:
        """Create VAR formula (sample variance)."""
        return f"{self.PREFIX}VAR({self._format_ref(ref)})"

    def percentile(self, ref: RangeRef | str, k: float) -> str:
        """Create PERCENTILE formula."""
        return f"{self.PREFIX}PERCENTILE({self._format_ref(ref)};{k})"

    def mode(self, ref: RangeRef | str) -> str:
        """Create MODE formula (most frequently occurring value)."""
        return f"{self.PREFIX}MODE({self._format_ref(ref)})"

    def varp(self, ref: RangeRef | str) -> str:
        """Create VARP formula (population variance)."""
        return f"{self.PREFIX}VARP({self._format_ref(ref)})"

    def quartile(self, ref: RangeRef | str, quart: int) -> str:
        """Create QUARTILE formula.

        Args:
            ref: Range reference
            quart: Quartile to return (0=min, 1=Q1, 2=median, 3=Q3, 4=max)

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}QUARTILE({self._format_ref(ref)};{quart})"

    def rank(self, number: CellRef | str, ref: RangeRef | str, order: int = 0) -> str:
        """Create RANK formula.

        Args:
            number: Value to rank
            ref: Range containing values
            order: 0=descending, 1=ascending

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}RANK({self._format_value(number)};{self._format_ref(ref)};{order})"

    def large(self, ref: RangeRef | str, k: int) -> str:
        """Create LARGE formula (k-th largest value)."""
        return f"{self.PREFIX}LARGE({self._format_ref(ref)};{k})"

    def small(self, ref: RangeRef | str, k: int) -> str:
        """Create SMALL formula (k-th smallest value)."""
        return f"{self.PREFIX}SMALL({self._format_ref(ref)};{k})"

    def correl(self, array1: RangeRef | str, array2: RangeRef | str) -> str:
        """Create CORREL formula (correlation coefficient)."""
        return f"{self.PREFIX}CORREL({self._format_ref(array1)};{self._format_ref(array2)})"

    def covar(self, array1: RangeRef | str, array2: RangeRef | str) -> str:
        """Create COVAR formula (covariance)."""
        return (
            f"{self.PREFIX}COVAR({self._format_ref(array1)};{self._format_ref(array2)})"
        )

    def forecast(
        self, x: CellRef | str, known_y: RangeRef | str, known_x: RangeRef | str
    ) -> str:
        """Create FORECAST formula (linear regression forecast)."""
        return f"{self.PREFIX}FORECAST({self._format_value(x)};{self._format_ref(known_y)};{self._format_ref(known_x)})"

    def slope(self, known_y: RangeRef | str, known_x: RangeRef | str) -> str:
        """Create SLOPE formula (slope of linear regression)."""
        return f"{self.PREFIX}SLOPE({self._format_ref(known_y)};{self._format_ref(known_x)})"

    def intercept(self, known_y: RangeRef | str, known_x: RangeRef | str) -> str:
        """Create INTERCEPT formula (y-intercept of linear regression)."""
        return f"{self.PREFIX}INTERCEPT({self._format_ref(known_y)};{self._format_ref(known_x)})"

    def rsq(self, known_y: RangeRef | str, known_x: RangeRef | str) -> str:
        """Create RSQ formula (R-squared of linear regression)."""
        return (
            f"{self.PREFIX}RSQ({self._format_ref(known_y)};{self._format_ref(known_x)})"
        )

    # =========================================================================
    # Financial Functions
    # =========================================================================

    def pmt(
        self,
        rate: CellRef | str | float,
        nper: CellRef | str | int,
        pv: CellRef | str | float,
        fv: CellRef | str | float = 0,
        payment_type: int = 0,
    ) -> str:
        """Create PMT formula (periodic payment).

        Args:
            rate: Interest rate per period
            nper: Total number of payment periods
            pv: Present value (loan amount)
            fv: Future value (default 0)
            payment_type: 0=end of period, 1=beginning

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}PMT({self._format_value(rate)};{self._format_value(nper)};{self._format_value(pv)};{self._format_value(fv)};{payment_type})"

    def pv(
        self,
        rate: CellRef | str | float,
        nper: CellRef | str | int,
        pmt: CellRef | str | float,
        fv: CellRef | str | float = 0,
        payment_type: int = 0,
    ) -> str:
        """Create PV formula (present value).

        Args:
            rate: Interest rate per period
            nper: Total number of payment periods
            pmt: Payment per period
            fv: Future value (default 0)
            payment_type: 0=end of period, 1=beginning

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}PV({self._format_value(rate)};{self._format_value(nper)};{self._format_value(pmt)};{self._format_value(fv)};{payment_type})"

    def fv(
        self,
        rate: CellRef | str | float,
        nper: CellRef | str | int,
        pmt: CellRef | str | float,
        pv: CellRef | str | float = 0,
        payment_type: int = 0,
    ) -> str:
        """Create FV formula (future value).

        Args:
            rate: Interest rate per period
            nper: Total number of payment periods
            pmt: Payment per period
            pv: Present value (default 0)
            payment_type: 0=end of period, 1=beginning

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}FV({self._format_value(rate)};{self._format_value(nper)};{self._format_value(pmt)};{self._format_value(pv)};{payment_type})"

    def npv(
        self,
        rate: CellRef | str | float,
        values: RangeRef | str,
    ) -> str:
        """Create NPV formula (net present value).

        Args:
            rate: Discount rate
            values: Range of cash flow values

        Returns:
            ODF formula string
        """
        return (
            f"{self.PREFIX}NPV({self._format_value(rate)};{self._format_ref(values)})"
        )

    def irr(
        self,
        values: RangeRef | str,
        guess: float = 0.1,
    ) -> str:
        """Create IRR formula (internal rate of return).

        Args:
            values: Range of cash flow values
            guess: Initial guess (default 0.1 = 10%)

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}IRR({self._format_ref(values)};{guess})"

    def nper(
        self,
        rate: CellRef | str | float,
        pmt: CellRef | str | float,
        pv: CellRef | str | float,
        fv: CellRef | str | float = 0,
        payment_type: int = 0,
    ) -> str:
        """Create NPER formula (number of periods).

        Args:
            rate: Interest rate per period
            pmt: Payment per period
            pv: Present value
            fv: Future value (default 0)
            payment_type: 0=end of period, 1=beginning

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}NPER({self._format_value(rate)};{self._format_value(pmt)};{self._format_value(pv)};{self._format_value(fv)};{payment_type})"

    def rate(
        self,
        nper: CellRef | str | int,
        pmt: CellRef | str | float,
        pv: CellRef | str | float,
        fv: CellRef | str | float = 0,
        payment_type: int = 0,
        guess: float = 0.1,
    ) -> str:
        """Create RATE formula (interest rate per period).

        Args:
            nper: Number of periods
            pmt: Payment per period
            pv: Present value
            fv: Future value (default 0)
            payment_type: 0=end of period, 1=beginning
            guess: Initial guess (default 0.1)

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}RATE({self._format_value(nper)};{self._format_value(pmt)};{self._format_value(pv)};{self._format_value(fv)};{payment_type};{guess})"

    def sln(
        self,
        cost: CellRef | str | float,
        salvage: CellRef | str | float,
        life: CellRef | str | int,
    ) -> str:
        """Create SLN formula (straight-line depreciation).

            - PHASE0-005: Complete FormulaBuilder with 100+ functions

        Args:
            cost: Initial cost
            salvage: Salvage value
            life: Number of periods

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}SLN({self._format_value(cost)};{self._format_value(salvage)};{self._format_value(life)})"

    def db(
        self,
        cost: CellRef | str | float,
        salvage: CellRef | str | float,
        life: CellRef | str | int,
        period: CellRef | str | int,
        month: int = 12,
    ) -> str:
        """Create DB formula (declining balance depreciation).

        Args:
            cost: Initial cost
            salvage: Salvage value
            life: Number of periods
            period: Period to calculate
            month: Number of months in first year (default 12)

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}DB({self._format_value(cost)};{self._format_value(salvage)};{self._format_value(life)};{self._format_value(period)};{month})"

    def ddb(
        self,
        cost: CellRef | str | float,
        salvage: CellRef | str | float,
        life: CellRef | str | int,
        period: CellRef | str | int,
        factor: float = 2.0,
    ) -> str:
        """Create DDB formula (double-declining balance depreciation).

        Args:
            cost: Initial cost
            salvage: Salvage value
            life: Number of periods
            period: Period to calculate
            factor: Depreciation factor (default 2.0)

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}DDB({self._format_value(cost)};{self._format_value(salvage)};{self._format_value(life)};{self._format_value(period)};{factor})"

    def syd(
        self,
        cost: CellRef | str | float,
        salvage: CellRef | str | float,
        life: CellRef | str | int,
        period: CellRef | str | int,
    ) -> str:
        """Create SYD formula (sum-of-years digits depreciation).

        Args:
            cost: Initial cost
            salvage: Salvage value
            life: Number of periods
            period: Period to calculate

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}SYD({self._format_value(cost)};{self._format_value(salvage)};{self._format_value(life)};{self._format_value(period)})"

    # =========================================================================
    # Date/Time Functions
    # =========================================================================

    def today(self) -> str:
        """Create TODAY formula."""
        return f"{self.PREFIX}TODAY()"

    def now(self) -> str:
        """Create NOW formula."""
        return f"{self.PREFIX}NOW()"

    def date(
        self,
        year: CellRef | str | int,
        month: CellRef | str | int,
        day: CellRef | str | int,
    ) -> str:
        """Create DATE formula."""
        return f"{self.PREFIX}DATE({self._format_value(year)};{self._format_value(month)};{self._format_value(day)})"

    def year(self, ref: CellRef | str) -> str:
        """Create YEAR formula."""
        return f"{self.PREFIX}YEAR({self._format_value(ref)})"

    def month(self, ref: CellRef | str) -> str:
        """Create MONTH formula."""
        return f"{self.PREFIX}MONTH({self._format_value(ref)})"

    def day(self, ref: CellRef | str) -> str:
        """Create DAY formula."""
        return f"{self.PREFIX}DAY({self._format_value(ref)})"

    def weekday(self, ref: CellRef | str, type: int = 1) -> str:
        """Create WEEKDAY formula (1=Sunday-Saturday, 2=Monday-Sunday)."""
        return f"{self.PREFIX}WEEKDAY({self._format_value(ref)};{type})"

    def weeknum(self, ref: CellRef | str, type: int = 1) -> str:
        """Create WEEKNUM formula."""
        return f"{self.PREFIX}WEEKNUM({self._format_value(ref)};{type})"

    def eomonth(self, start_date: CellRef | str, months: CellRef | str | int) -> str:
        """Create EOMONTH formula (end of month)."""
        return f"{self.PREFIX}EOMONTH({self._format_value(start_date)};{self._format_value(months)})"

    def datedif(
        self,
        start_date: CellRef | str,
        end_date: CellRef | str,
        unit: str = "D",
    ) -> str:
        """Create DATEDIF formula.

        Args:
            start_date: Start date
            end_date: End date
            unit: "Y", "M", "D", "YM", "MD", "YD"

        Returns:
            ODF formula string
        """
        return f'{self.PREFIX}DATEDIF({self._format_value(start_date)};{self._format_value(end_date)};"{unit}")'

    def time(
        self,
        hour: CellRef | str | int,
        minute: CellRef | str | int,
        second: CellRef | str | int,
    ) -> str:
        """Create TIME formula."""
        return f"{self.PREFIX}TIME({self._format_value(hour)};{self._format_value(minute)};{self._format_value(second)})"

    def hour(self, ref: CellRef | str) -> str:
        """Create HOUR formula."""
        return f"{self.PREFIX}HOUR({self._format_value(ref)})"

    def minute(self, ref: CellRef | str) -> str:
        """Create MINUTE formula."""
        return f"{self.PREFIX}MINUTE({self._format_value(ref)})"

    def second(self, ref: CellRef | str) -> str:
        """Create SECOND formula."""
        return f"{self.PREFIX}SECOND({self._format_value(ref)})"

    def networkdays(
        self,
        start_date: CellRef | str,
        end_date: CellRef | str,
        holidays: RangeRef | str | None = None,
    ) -> str:
        """Create NETWORKDAYS formula (working days between dates).

            - PHASE0-005: Complete FormulaBuilder with 100+ functions

        Args:
            start_date: Start date
            end_date: End date
            holidays: Optional range of holiday dates

        Returns:
            ODF formula string
        """
        if holidays:
            return f"{self.PREFIX}NETWORKDAYS({self._format_value(start_date)};{self._format_value(end_date)};{self._format_ref(holidays)})"
        return f"{self.PREFIX}NETWORKDAYS({self._format_value(start_date)};{self._format_value(end_date)})"

    def workday(
        self,
        start_date: CellRef | str,
        days: CellRef | str | int,
        holidays: RangeRef | str | None = None,
    ) -> str:
        """Create WORKDAY formula (date after specified working days).

        Args:
            start_date: Start date
            days: Number of working days to add
            holidays: Optional range of holiday dates

        Returns:
            ODF formula string
        """
        if holidays:
            return f"{self.PREFIX}WORKDAY({self._format_value(start_date)};{self._format_value(days)};{self._format_ref(holidays)})"
        return f"{self.PREFIX}WORKDAY({self._format_value(start_date)};{self._format_value(days)})"

    def edate(self, start_date: CellRef | str, months: CellRef | str | int) -> str:
        """Create EDATE formula (date after specified months)."""
        return f"{self.PREFIX}EDATE({self._format_value(start_date)};{self._format_value(months)})"

    # =========================================================================
    # Lookup Functions
    # =========================================================================

    def vlookup(
        self,
        lookup_value: CellRef | str,
        table: RangeRef | str,
        col_index: int,
        *,
        exact: bool = True,
    ) -> str:
        """Create VLOOKUP formula."""
        val = self._format_value(lookup_value)
        tbl = self._format_ref(table)
        match = "0" if exact else "1"
        return f"{self.PREFIX}VLOOKUP({val};{tbl};{col_index};{match})"

    def hlookup(
        self,
        lookup_value: CellRef | str,
        table: RangeRef | str,
        row_index: int,
        *,
        exact: bool = True,
    ) -> str:
        """Create HLOOKUP formula."""
        val = self._format_value(lookup_value)
        tbl = self._format_ref(table)
        match = "0" if exact else "1"
        return f"{self.PREFIX}HLOOKUP({val};{tbl};{row_index};{match})"

    def index(
        self,
        array: RangeRef | str,
        row_num: CellRef | str | int,
        col_num: CellRef | str | int | None = None,
    ) -> str:
        """Create INDEX formula."""
        arr = self._format_ref(array)
        row = self._format_value(row_num)
        if col_num is not None:
            col = self._format_value(col_num)
            return f"{self.PREFIX}INDEX({arr};{row};{col})"
        return f"{self.PREFIX}INDEX({arr};{row})"

    def match(
        self,
        lookup_value: CellRef | str,
        lookup_array: RangeRef | str,
        match_type: int = 0,
    ) -> str:
        """Create MATCH formula.

        Args:
            lookup_value: Value to find
            lookup_array: Range to search
            match_type: 0=exact, 1=less than, -1=greater than

        Returns:
            ODF formula string
        """
        val = self._format_value(lookup_value)
        arr = self._format_ref(lookup_array)
        return f"{self.PREFIX}MATCH({val};{arr};{match_type})"

    def index_match(
        self,
        return_range: RangeRef | str,
        match_formula: str,
    ) -> str:
        """Create INDEX/MATCH combination.

        Args:
            return_range: Range to return value from
            match_formula: MATCH formula (without prefix)

        Returns:
            ODF formula string
        """
        # Strip prefix from match_formula if present
        if match_formula.startswith(self.PREFIX):
            match_formula = match_formula[len(self.PREFIX) :]
        return f"{self.PREFIX}INDEX({self._format_ref(return_range)};{match_formula})"

    def offset(
        self,
        reference: CellRef | str,
        rows: CellRef | str | int,
        cols: CellRef | str | int,
        height: CellRef | str | int | None = None,
        width: CellRef | str | int | None = None,
    ) -> str:
        """Create OFFSET formula."""
        ref = self._format_value(reference)
        r = self._format_value(rows)
        c = self._format_value(cols)
        parts = [ref, r, c]
        if height is not None:
            parts.append(self._format_value(height))
            if width is not None:
                parts.append(self._format_value(width))
        return f"{self.PREFIX}OFFSET({';'.join(parts)})"

    def indirect(self, ref_text: CellRef | str) -> str:
        """Create INDIRECT formula."""
        return f"{self.PREFIX}INDIRECT({self._format_value(ref_text)})"

    # =========================================================================
    # Text Functions
    # =========================================================================

    def concatenate(self, *values: CellRef | str) -> str:
        """Create CONCATENATE formula."""
        parts = [self._format_value(v) for v in values]
        return f"{self.PREFIX}CONCATENATE({';'.join(parts)})"

    def concat(self, *values: CellRef | str) -> str:
        """Create CONCAT formula (alias for CONCATENATE)."""
        return self.concatenate(*values)

    def text(self, value: CellRef | str, format_text: str) -> str:
        """Create TEXT formula."""
        return f'{self.PREFIX}TEXT({self._format_value(value)};"{format_text}")'

    def left(self, text: CellRef | str, num_chars: int = 1) -> str:
        """Create LEFT formula."""
        return f"{self.PREFIX}LEFT({self._format_value(text)};{num_chars})"

    def right(self, text: CellRef | str, num_chars: int = 1) -> str:
        """Create RIGHT formula."""
        return f"{self.PREFIX}RIGHT({self._format_value(text)};{num_chars})"

    def mid(self, text: CellRef | str, start_num: int, num_chars: int) -> str:
        """Create MID formula."""
        return f"{self.PREFIX}MID({self._format_value(text)};{start_num};{num_chars})"

    def len(self, text: CellRef | str) -> str:
        """Create LEN formula."""
        return f"{self.PREFIX}LEN({self._format_value(text)})"

    def trim(self, text: CellRef | str) -> str:
        """Create TRIM formula."""
        return f"{self.PREFIX}TRIM({self._format_value(text)})"

    def upper(self, text: CellRef | str) -> str:
        """Create UPPER formula."""
        return f"{self.PREFIX}UPPER({self._format_value(text)})"

    def lower(self, text: CellRef | str) -> str:
        """Create LOWER formula."""
        return f"{self.PREFIX}LOWER({self._format_value(text)})"

    def proper(self, text: CellRef | str) -> str:
        """Create PROPER formula (title case)."""
        return f"{self.PREFIX}PROPER({self._format_value(text)})"

    def find(
        self, find_text: str, within_text: CellRef | str, start_num: int = 1
    ) -> str:
        """Create FIND formula (case-sensitive)."""
        return f'{self.PREFIX}FIND("{find_text}";{self._format_value(within_text)};{start_num})'

    def search(
        self, find_text: str, within_text: CellRef | str, start_num: int = 1
    ) -> str:
        """Create SEARCH formula (case-insensitive)."""
        return f'{self.PREFIX}SEARCH("{find_text}";{self._format_value(within_text)};{start_num})'

    def substitute(
        self,
        text: CellRef | str,
        old_text: str,
        new_text: str,
        instance_num: int | None = None,
    ) -> str:
        """Create SUBSTITUTE formula."""
        parts = [self._format_value(text), f'"{old_text}"', f'"{new_text}"']
        if instance_num is not None:
            parts.append(str(instance_num))
        return f"{self.PREFIX}SUBSTITUTE({';'.join(parts)})"

    def rept(self, text: CellRef | str, number_times: CellRef | str | int) -> str:
        """Create REPT formula (repeat text)."""
        return f"{self.PREFIX}REPT({self._format_value(text)};{self._format_value(number_times)})"

    def replace(
        self,
        old_text: CellRef | str,
        start_num: int,
        num_chars: int,
        new_text: str,
    ) -> str:
        """Create REPLACE formula."""
        return f'{self.PREFIX}REPLACE({self._format_value(old_text)};{start_num};{num_chars};"{new_text}")'

    def value(self, text: CellRef | str) -> str:
        """Create VALUE formula (convert text to number)."""
        return f"{self.PREFIX}VALUE({self._format_value(text)})"

    def char(self, number: CellRef | str | int) -> str:
        """Create CHAR formula (character from code)."""
        return f"{self.PREFIX}CHAR({self._format_value(number)})"

    def code(self, text: CellRef | str) -> str:
        """Create CODE formula (code from character)."""
        return f"{self.PREFIX}CODE({self._format_value(text)})"

    def exact(self, text1: CellRef | str, text2: CellRef | str) -> str:
        """Create EXACT formula (case-sensitive text comparison)."""
        return f"{self.PREFIX}EXACT({self._format_value(text1)};{self._format_value(text2)})"

    def textjoin(
        self,
        delimiter: str,
        ignore_empty: bool,
        *text_values: CellRef | RangeRef | str,
    ) -> str:
        """Create TEXTJOIN formula (join text with delimiter).

            - PHASE0-005: Complete FormulaBuilder with 100+ functions

        Args:
            delimiter: Text to use between values
            ignore_empty: True to skip empty cells
            text_values: Values or ranges to join

        Returns:
            ODF formula string
        """
        ignore = "1" if ignore_empty else "0"
        parts = [self._format_value(v) for v in text_values]
        return f'{self.PREFIX}TEXTJOIN("{delimiter}";{ignore};{";".join(parts)})'

    # =========================================================================
    # Logical Functions
    # =========================================================================

    def if_expr(
        self,
        condition: str,
        true_value: str | CellRef,
        false_value: str | CellRef,
    ) -> str:
        """Create IF formula."""
        tv = str(true_value) if isinstance(true_value, CellRef) else true_value
        fv = str(false_value) if isinstance(false_value, CellRef) else false_value
        return f"{self.PREFIX}IF({condition};{tv};{fv})"

    def iferror(
        self,
        value: CellRef | str,
        value_if_error: CellRef | str | float | int,
    ) -> str:
        """Create IFERROR formula."""
        return f"{self.PREFIX}IFERROR({self._format_value(value)};{self._format_value(value_if_error)})"

    def ifna(
        self,
        value: CellRef | str,
        value_if_na: CellRef | str | float | int,
    ) -> str:
        """Create IFNA formula."""
        return f"{self.PREFIX}IFNA({self._format_value(value)};{self._format_value(value_if_na)})"

    def and_expr(self, *conditions: str) -> str:
        """Create AND formula."""
        return f"{self.PREFIX}AND({';'.join(conditions)})"

    def or_expr(self, *conditions: str) -> str:
        """Create OR formula."""
        return f"{self.PREFIX}OR({';'.join(conditions)})"

    def not_expr(self, condition: str) -> str:
        """Create NOT formula."""
        return f"{self.PREFIX}NOT({condition})"

    def isblank(self, ref: CellRef | str) -> str:
        """Create ISBLANK formula."""
        return f"{self.PREFIX}ISBLANK({self._format_value(ref)})"

    def iserror(self, ref: CellRef | str) -> str:
        """Create ISERROR formula."""
        return f"{self.PREFIX}ISERROR({self._format_value(ref)})"

    def isnumber(self, ref: CellRef | str) -> str:
        """Create ISNUMBER formula."""
        return f"{self.PREFIX}ISNUMBER({self._format_value(ref)})"

    def istext(self, ref: CellRef | str) -> str:
        """Create ISTEXT formula."""
        return f"{self.PREFIX}ISTEXT({self._format_value(ref)})"

    def xor(self, *conditions: str) -> str:
        """Create XOR formula (exclusive OR).

            - PHASE0-005: Complete FormulaBuilder with 100+ functions

        Args:
            conditions: Logical conditions to evaluate

        Returns:
            ODF formula string
        """
        return f"{self.PREFIX}XOR({';'.join(conditions)})"

    def choose(self, index: CellRef | str | int, *values: CellRef | str) -> str:
        """Create CHOOSE formula (select value by index).

        Args:
            index: Index number (1-based)
            values: Values to choose from

        Returns:
            ODF formula string
        """
        parts = [self._format_value(v) for v in values]
        return f"{self.PREFIX}CHOOSE({self._format_value(index)};{';'.join(parts)})"

    def isna(self, ref: CellRef | str) -> str:
        """Create ISNA formula (check for #N/A error)."""
        return f"{self.PREFIX}ISNA({self._format_value(ref)})"

    def iseven(self, ref: CellRef | str) -> str:
        """Create ISEVEN formula."""
        return f"{self.PREFIX}ISEVEN({self._format_value(ref)})"

    def isodd(self, ref: CellRef | str) -> str:
        """Create ISODD formula."""
        return f"{self.PREFIX}ISODD({self._format_value(ref)})"

    # =========================================================================
    # Array Formulas
    # =========================================================================

    def array(self, formula: str) -> str:
        """Wrap formula as array formula.

        Note: In ODF, array formulas need special handling during rendering.

        Args:
            formula: Formula to wrap

        Returns:
            Array formula string
        """
        # Remove existing prefix if present
        if formula.startswith(self.PREFIX):
            formula = formula[len(self.PREFIX) :]
        return f"{self.PREFIX}{{{formula}}}"


# ============================================================================
# Circular Reference Detection
# ============================================================================


class FormulaDependencyGraph:
    """Tracks formula dependencies and detects circular references.

    Builds a directed graph of formula dependencies and can
    detect cycles (circular references).
    """

    # Pattern to find cell references in formulas
    # Matches same-sheet references like [.A1] and captures cell address (A1)
    CELL_REF_PATTERN = re.compile(r"\[\.([A-Z]+[0-9]+)\]")
    # Matches cross-sheet references like [Sheet1.A1] and captures both sheet name and cell address
    SHEET_REF_PATTERN = re.compile(r"\[([^.]+)\.([A-Z]+[0-9]+)\]")

    def __init__(self) -> None:
        """Initialize empty dependency graph."""
        self._dependencies: dict[str, set[str]] = {}
        self._formulas: dict[str, str] = {}

    def add_cell(
        self, cell_ref: str, formula: str | None, sheet: str = "Sheet1"
    ) -> None:
        """Add a cell and its formula to the dependency graph.

        Args:
            cell_ref: Cell reference (e.g., "A2")
            formula: Formula string (None if no formula)
            sheet: Sheet name
        """
        full_ref = f"{sheet}.{cell_ref}"

        # Initialize dependencies for this cell
        if full_ref not in self._dependencies:
            self._dependencies[full_ref] = set()

        if formula:
            self._formulas[full_ref] = formula
            # Extract cell references from formula
            deps = self._extract_dependencies(formula, sheet)
            self._dependencies[full_ref] = deps

    def _extract_dependencies(self, formula: str, current_sheet: str) -> set[str]:
        """Extract cell references from a formula.

        Args:
            formula: Formula string
            current_sheet: Current sheet name

        Returns:
            Set of cell references (with sheet prefix)
        """
        deps: set[str] = set()

        # Find same-sheet references like [.A2]
        for match in self.CELL_REF_PATTERN.finditer(formula):
            cell = match.group(1)
            deps.add(f"{current_sheet}.{cell}")

        # Find cross-sheet references like [Sheet2.A5]
        for match in self.SHEET_REF_PATTERN.finditer(formula):
            sheet = match.group(1).strip("'")  # Remove quotes if present
            cell = match.group(2)
            deps.add(f"{sheet}.{cell}")

        return deps

    def detect_circular_references(self) -> list[tuple[str, list[str]]]:
        """Detect all circular references in the dependency graph.

        Returns:
            List of (cell, cycle) tuples for each circular reference found
        """
        circular_refs: list[tuple[str, list[str]]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(cell: str) -> bool:
            """Depth-first search to detect cycles.

            Args:
                cell: Current cell being visited

            Returns:
                True if cycle detected, False otherwise
            """
            visited.add(cell)
            rec_stack.add(cell)
            path.append(cell)

            # Visit all dependencies
            for dep in self._dependencies.get(cell, set()):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    # Found a cycle - extract the circular path
                    cycle_start_idx = path.index(dep)
                    cycle = [*path[cycle_start_idx:], dep]
                    circular_refs.append((cell, cycle))
                    return True

            path.pop()
            rec_stack.remove(cell)
            return False

        # Check all cells for circular references
        for cell in self._dependencies:
            if cell not in visited:
                path.clear()
                dfs(cell)

        return circular_refs

    def validate(self) -> None:
        """Validate the dependency graph and raise error if circular references found.

        Raises:
            CircularReferenceError: If circular references are detected
        """
        circular_refs = self.detect_circular_references()
        if circular_refs:
            cell, cycle = circular_refs[0]  # Report first circular reference
            raise CircularReferenceError(cell, cycle)

    def get_dependencies(self, cell_ref: str, sheet: str = "Sheet1") -> set[str]:
        """Get all cells that the given cell depends on.

        Args:
            cell_ref: Cell reference
            sheet: Sheet name

        Returns:
            Set of cell references (with sheet prefix)
        """
        full_ref = f"{sheet}.{cell_ref}"
        return self._dependencies.get(full_ref, set())

    def get_dependents(self, cell_ref: str, sheet: str = "Sheet1") -> set[str]:
        """Get all cells that depend on the given cell.

        Args:
            cell_ref: Cell reference
            sheet: Sheet name

        Returns:
            Set of cell references (with sheet prefix)
        """
        full_ref = f"{sheet}.{cell_ref}"
        dependents: set[str] = set()

        for cell, deps in self._dependencies.items():
            if full_ref in deps:
                dependents.add(cell)

        return dependents
