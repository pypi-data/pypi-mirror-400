"""Asset depreciation formulas.

Financial formulas for asset depreciation calculations
(StraightLine, DecliningBalance, SUMYearsDigits)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class StraightLineDepreciation(BaseFormula):
    """Calculate straight-line depreciation.

        SLN formula for linear depreciation over asset life

    Example:
        >>> formula = StraightLineDepreciation()
        >>> result = formula.build("100000", "10000", "10")
        >>> # Returns: "of:=SLN(100000;10000;10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SLN

            Formula metadata
        """
        return FormulaMetadata(
            name="SLN",
            category="depreciation",
            description="Calculate straight-line depreciation",
            arguments=(
                FormulaArgument(
                    "cost",
                    "number",
                    required=True,
                    description="Initial cost of the asset",
                ),
                FormulaArgument(
                    "salvage",
                    "number",
                    required=True,
                    description="Salvage value at end of life",
                ),
                FormulaArgument(
                    "life",
                    "number",
                    required=True,
                    description="Number of periods over which asset depreciates",
                ),
            ),
            return_type="number",
            examples=(
                "=SLN(100000;10000;10)",
                "=SLN(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SLN formula string.

        Args:
            *args: cost, salvage, life
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SLN formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        cost = args[0]
        salvage = args[1]
        life = args[2]

        return f"of:=SLN({cost};{salvage};{life})"


@dataclass(slots=True, frozen=True)
class DecliningBalanceDepreciation(BaseFormula):
    """Calculate declining balance depreciation.

        DB formula for accelerated depreciation method

    Example:
        >>> formula = DecliningBalanceDepreciation()
        >>> result = formula.build("100000", "10000", "10", "1")
        >>> # Returns: "of:=DB(100000;10000;10;1;12)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DB

            Formula metadata
        """
        return FormulaMetadata(
            name="DB",
            category="depreciation",
            description="Calculate declining balance depreciation",
            arguments=(
                FormulaArgument(
                    "cost",
                    "number",
                    required=True,
                    description="Initial cost of the asset",
                ),
                FormulaArgument(
                    "salvage",
                    "number",
                    required=True,
                    description="Salvage value at end of life",
                ),
                FormulaArgument(
                    "life",
                    "number",
                    required=True,
                    description="Number of periods over which asset depreciates",
                ),
                FormulaArgument(
                    "period",
                    "number",
                    required=True,
                    description="Period for which to calculate depreciation",
                ),
                FormulaArgument(
                    "month",
                    "number",
                    required=False,
                    description="Number of months in first year",
                    default=12,
                ),
            ),
            return_type="number",
            examples=(
                "=DB(100000;10000;10;1;12)",
                "=DB(A1;A2;A3;A4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DB formula string.

        Args:
            *args: cost, salvage, life, period, [month]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            DB formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        cost = args[0]
        salvage = args[1]
        life = args[2]
        period = args[3]
        month = args[4] if len(args) > 4 else 12

        return f"of:=DB({cost};{salvage};{life};{period};{month})"


@dataclass(slots=True, frozen=True)
class SUMYearsDigitsDepreciation(BaseFormula):
    """Calculate sum-of-years digits depreciation.

        SYD formula for accelerated depreciation using sum-of-years method

    Example:
        >>> formula = SUMYearsDigitsDepreciation()
        >>> result = formula.build("100000", "10000", "10", "1")
        >>> # Returns: "of:=SYD(100000;10000;10;1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SYD

            Formula metadata
        """
        return FormulaMetadata(
            name="SYD",
            category="depreciation",
            description="Calculate sum-of-years digits depreciation",
            arguments=(
                FormulaArgument(
                    "cost",
                    "number",
                    required=True,
                    description="Initial cost of the asset",
                ),
                FormulaArgument(
                    "salvage",
                    "number",
                    required=True,
                    description="Salvage value at end of life",
                ),
                FormulaArgument(
                    "life",
                    "number",
                    required=True,
                    description="Number of periods over which asset depreciates",
                ),
                FormulaArgument(
                    "period",
                    "number",
                    required=True,
                    description="Period for which to calculate depreciation",
                ),
            ),
            return_type="number",
            examples=(
                "=SYD(100000;10000;10;1)",
                "=SYD(A1;A2;A3;A4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SYD formula string.

        Args:
            *args: cost, salvage, life, period
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SYD formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        cost = args[0]
        salvage = args[1]
        life = args[2]
        period = args[3]

        return f"of:=SYD({cost};{salvage};{life};{period})"
