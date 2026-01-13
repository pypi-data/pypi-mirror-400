"""Civil Engineering formulas for SpreadsheetDL.

    Civil Engineering domain formulas

Provides domain-specific formulas for:
- Beam calculations (deflection, shear stress, moment)
- Soil mechanics (bearing capacity, settlement, pressure)
- Concrete design (strength, reinforcement ratio, crack width)
- Load calculations (dead, live, wind, seismic)
- Foundation design (Terzaghi bearing capacity, elastic settlement, consolidation)
- Transportation (stopping distance, traffic flow)
"""

from spreadsheet_dl.domains.civil_engineering.formulas.beam import (
    BeamDeflectionFormula,
    MomentFormula,
    ShearStressFormula,
)
from spreadsheet_dl.domains.civil_engineering.formulas.concrete import (
    ConcreteStrengthFormula,
    CrackWidthFormula,
    ReinforcementRatioFormula,
)
from spreadsheet_dl.domains.civil_engineering.formulas.foundation import (
    BearingCapacityTerzaghi,
    ConsolidationSettlement,
    SettlementElastic,
)
from spreadsheet_dl.domains.civil_engineering.formulas.hydrology import (
    ManningEquation,
    RationalMethod,
    RunoffCoefficient,
    TimeOfConcentration,
)
from spreadsheet_dl.domains.civil_engineering.formulas.loads import (
    DeadLoadFormula,
    LiveLoadFormula,
    SeismicLoadFormula,
    WindLoadFormula,
)
from spreadsheet_dl.domains.civil_engineering.formulas.soil import (
    BearingCapacityFormula,
    SettlementFormula,
    SoilPressureFormula,
)
from spreadsheet_dl.domains.civil_engineering.formulas.transportation import (
    StoppingDistance,
    TrafficFlow,
)

__all__ = [
    # Beam formulas
    "BeamDeflectionFormula",
    # Soil formulas
    "BearingCapacityFormula",
    # Foundation formulas
    "BearingCapacityTerzaghi",
    # Concrete formulas
    "ConcreteStrengthFormula",
    "ConsolidationSettlement",
    "CrackWidthFormula",
    # Load formulas
    "DeadLoadFormula",
    "LiveLoadFormula",
    "ManningEquation",
    "MomentFormula",
    "RationalMethod",
    "ReinforcementRatioFormula",
    "RunoffCoefficient",
    "SeismicLoadFormula",
    "SettlementElastic",
    "SettlementFormula",
    "ShearStressFormula",
    "SoilPressureFormula",
    # Transportation formulas
    "StoppingDistance",
    "TimeOfConcentration",
    "TrafficFlow",
    "WindLoadFormula",
]
