"""Optics formulas for physics.

Physics optics formulas (6 formulas)
BATCH-5: Physics domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class SnellsLawFormula(BaseFormula):
    """Calculate refraction using Snell's law.

        SNELLS_LAW formula (n1*sin(θ1) = n2*sin(θ2))
        BATCH-5: Physics optics

    Example:
        >>> formula = SnellsLawFormula()
        >>> result = formula.build("1.0", "30", "1.5")
        >>> # Returns: "of:=DEGREES(ASIN(1.0*SIN(RADIANS(30))/1.5))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SNELLS_LAW
        """
        return FormulaMetadata(
            name="SNELLS_LAW",
            category="optics",
            description="Calculate refraction angle (n1*sin(θ1) = n2*sin(θ2))",
            arguments=(
                FormulaArgument(
                    "n1",
                    "number",
                    required=True,
                    description="Refractive index of first medium",
                ),
                FormulaArgument(
                    "theta1",
                    "number",
                    required=True,
                    description="Incident angle (degrees)",
                ),
                FormulaArgument(
                    "n2",
                    "number",
                    required=True,
                    description="Refractive index of second medium",
                ),
            ),
            return_type="number",
            examples=(
                "=SNELLS_LAW(1.0;30;1.5)",
                "=SNELLS_LAW(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SNELLS_LAW formula string.

        Args:
            *args: n1, theta1, n2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns theta2 in degrees)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        n1 = args[0]
        theta1 = args[1]
        n2 = args[2]

        # θ2 = arcsin(n1*sin(θ1)/n2)
        return f"of:=DEGREES(ASIN({n1}*SIN(RADIANS({theta1}))/{n2}))"


@dataclass(slots=True, frozen=True)
class LensMakerEquationFormula(BaseFormula):
    """Calculate lens focal length using lensmaker's equation.

        LENS_MAKER_EQUATION formula (1/f = (n-1)*(1/R1 - 1/R2))
        BATCH-5: Physics optics

    Example:
        >>> formula = LensMakerEquationFormula()
        >>> result = formula.build("1.5", "10", "-10")
        >>> # Returns: "of:=1/((1.5-1)*(1/10-1/-10))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LENS_MAKER_EQUATION
        """
        return FormulaMetadata(
            name="LENS_MAKER_EQUATION",
            category="optics",
            description="Calculate focal length (1/f = (n-1)*(1/R1 - 1/R2))",
            arguments=(
                FormulaArgument(
                    "refractive_index",
                    "number",
                    required=True,
                    description="Refractive index of lens material",
                ),
                FormulaArgument(
                    "radius1",
                    "number",
                    required=True,
                    description="Radius of curvature 1 (cm)",
                ),
                FormulaArgument(
                    "radius2",
                    "number",
                    required=True,
                    description="Radius of curvature 2 (cm)",
                ),
            ),
            return_type="number",
            examples=(
                "=LENS_MAKER_EQUATION(1.5;10;-10)",
                "=LENS_MAKER_EQUATION(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LENS_MAKER_EQUATION formula string.

        Args:
            *args: refractive_index, radius1, radius2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns focal length)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        refractive_index = args[0]
        radius1 = args[1]
        radius2 = args[2]

        # f = 1/((n-1)*(1/R1 - 1/R2))
        return f"of:=1/(({refractive_index}-1)*(1/{radius1}-1/{radius2}))"


@dataclass(slots=True, frozen=True)
class MagnificationLensFormula(BaseFormula):
    """Calculate lens magnification.

        MAGNIFICATION_LENS formula (M = -di/do)
        BATCH-5: Physics optics

    Example:
        >>> formula = MagnificationLensFormula()
        >>> result = formula.build("20", "10")
        >>> # Returns: "of:=-20/10"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MAGNIFICATION_LENS
        """
        return FormulaMetadata(
            name="MAGNIFICATION_LENS",
            category="optics",
            description="Calculate lens magnification (M = -di/do)",
            arguments=(
                FormulaArgument(
                    "image_distance",
                    "number",
                    required=True,
                    description="Image distance (cm)",
                ),
                FormulaArgument(
                    "object_distance",
                    "number",
                    required=True,
                    description="Object distance (cm)",
                ),
            ),
            return_type="number",
            examples=(
                "=MAGNIFICATION_LENS(20;10)",
                "=MAGNIFICATION_LENS(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MAGNIFICATION_LENS formula string.

        Args:
            *args: image_distance, object_distance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        image_distance = args[0]
        object_distance = args[1]

        # M = -di/do
        return f"of:=-{image_distance}/{object_distance}"


@dataclass(slots=True, frozen=True)
class BraggLawFormula(BaseFormula):
    """Calculate Bragg diffraction condition.

        BRAGG_LAW formula (nλ = 2d*sin(θ))
        BATCH-5: Physics optics

    Example:
        >>> formula = BraggLawFormula()
        >>> result = formula.build("1", "0.154", "30")
        >>> # Returns: "of:=1*0.154/(2*SIN(RADIANS(30)))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BRAGG_LAW
        """
        return FormulaMetadata(
            name="BRAGG_LAW",
            category="optics",
            description="Calculate lattice spacing (nλ = 2d*sin(θ))",
            arguments=(
                FormulaArgument(
                    "order",
                    "number",
                    required=True,
                    description="Order of diffraction (n)",
                ),
                FormulaArgument(
                    "wavelength",
                    "number",
                    required=True,
                    description="Wavelength (nm)",
                ),
                FormulaArgument(
                    "angle",
                    "number",
                    required=True,
                    description="Diffraction angle (degrees)",
                ),
            ),
            return_type="number",
            examples=(
                "=BRAGG_LAW(1;0.154;30)",
                "=BRAGG_LAW(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BRAGG_LAW formula string.

        Args:
            *args: order, wavelength, angle
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns d)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        order = args[0]
        wavelength = args[1]
        angle = args[2]

        # d = nλ/(2*sin(θ))
        return f"of:={order}*{wavelength}/(2*SIN(RADIANS({angle})))"


@dataclass(slots=True, frozen=True)
class ThinFilmInterferenceFormula(BaseFormula):
    """Calculate thin film interference condition.

        THIN_FILM_INTERFERENCE formula (2nt*cos(θ) = mλ)
        BATCH-5: Physics optics

    Example:
        >>> formula = ThinFilmInterferenceFormula()
        >>> result = formula.build("1.5", "100", "0", "1")
        >>> # Returns: "of:=2*1.5*100*COS(RADIANS(0))/1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for THIN_FILM_INTERFERENCE
        """
        return FormulaMetadata(
            name="THIN_FILM_INTERFERENCE",
            category="optics",
            description="Calculate wavelength for interference (2nt*cos(θ) = mλ)",
            arguments=(
                FormulaArgument(
                    "refractive_index",
                    "number",
                    required=True,
                    description="Refractive index of film",
                ),
                FormulaArgument(
                    "thickness",
                    "number",
                    required=True,
                    description="Film thickness (nm)",
                ),
                FormulaArgument(
                    "angle",
                    "number",
                    required=False,
                    description="Angle of incidence (degrees)",
                    default=0,
                ),
                FormulaArgument(
                    "order",
                    "number",
                    required=False,
                    description="Order of interference (m)",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=THIN_FILM_INTERFERENCE(1.5;100;0;1)",
                "=THIN_FILM_INTERFERENCE(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build THIN_FILM_INTERFERENCE formula string.

        Args:
            *args: refractive_index, thickness, [angle], [order]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns wavelength)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        refractive_index = args[0]
        thickness = args[1]
        angle = args[2] if len(args) > 2 else 0
        order = args[3] if len(args) > 3 else 1

        # λ = 2nt*cos(θ)/m
        return f"of:=2*{refractive_index}*{thickness}*COS(RADIANS({angle}))/{order}"


@dataclass(slots=True, frozen=True)
class DiffractionGratingFormula(BaseFormula):
    """Calculate diffraction grating equation.

        DIFFRACTION_GRATING formula (d*sin(θ) = mλ)
        BATCH-5: Physics optics

    Example:
        >>> formula = DiffractionGratingFormula()
        >>> result = formula.build("1000", "30", "1")
        >>> # Returns: "of:=1000*SIN(RADIANS(30))/1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DIFFRACTION_GRATING
        """
        return FormulaMetadata(
            name="DIFFRACTION_GRATING",
            category="optics",
            description="Calculate wavelength from grating (d*sin(θ) = mλ)",
            arguments=(
                FormulaArgument(
                    "grating_spacing",
                    "number",
                    required=True,
                    description="Grating spacing (nm)",
                ),
                FormulaArgument(
                    "angle",
                    "number",
                    required=True,
                    description="Diffraction angle (degrees)",
                ),
                FormulaArgument(
                    "order",
                    "number",
                    required=False,
                    description="Order of diffraction (m)",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=DIFFRACTION_GRATING(1000;30;1)",
                "=DIFFRACTION_GRATING(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DIFFRACTION_GRATING formula string.

        Args:
            *args: grating_spacing, angle, [order]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns wavelength)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grating_spacing = args[0]
        angle = args[1]
        order = args[2] if len(args) > 2 else 1

        # λ = d*sin(θ)/m
        return f"of:={grating_spacing}*SIN(RADIANS({angle}))/{order}"


__all__ = [
    "BraggLawFormula",
    "DiffractionGratingFormula",
    "LensMakerEquationFormula",
    "MagnificationLensFormula",
    "SnellsLawFormula",
    "ThinFilmInterferenceFormula",
]
