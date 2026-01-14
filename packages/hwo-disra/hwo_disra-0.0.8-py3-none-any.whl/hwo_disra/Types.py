from dataclasses import dataclass
from enum import Enum
from typing import NewType, Optional, Any
import astropy.units as u


@dataclass
class Range:
    min: float
    max: float
    units: u.Unit = u.dimensionless_unscaled

@dataclass
class SinglePoint:
    value: Any
    units: u.Unit | str = u.dimensionless_unscaled

@dataclass
class DiscretePoints:
    items: list
    units: u.Unit | str = u.dimensionless_unscaled

    @staticmethod
    def from_dict(d: dict, units: u.Unit | str) -> 'DiscretePoints':
        return DiscretePoints(list(d.values()), units)

ScienceYield = NewType('ScienceYield', float)
Time = NewType('Time', float)

class ScienceValue(Enum):
    STATE_OF_THE_ART = 0 # Best that is currently achievable.
    ENHANCING = 1, # Minimum threshold, if we can't achieve this, project isn't worth doing.
    ENABLING = 2,  # Baseline goal for the observatory.
    BREAKTHROUGH = 3 # Major advancement over current state of the art.


@dataclass
class STMData:
    """Data structure for Science Traceability Matrix (STM) content.

    This class holds the extracted STM data from notebook cells using
    bolded markdown keys (e.g., **GOAL:**, **OBJECTIVE:**).
    """
    goal: Optional[str] = None
    objective: Optional[str] = None
    code_purpose: Optional[str] = None
    physical_parameters: Optional[str] = None
    observations: Optional[str] = None
    instrument_requirements: Optional[str] = None
    mission_requirements: Optional[str] = None
    expected_performance: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if all required STM fields are populated.

        Returns:
            True if goal, objective, physical_parameters, and observations are all set
        """
        required_fields = [self.goal, self.objective, self.physical_parameters, self.observations]
        return all(field is not None and field.strip() for field in required_fields)

    def get_missing_fields(self) -> list[str]:
        """Get list of missing required STM fields.

        Returns:
            List of field names that are None or empty
        """
        missing = []
        required = {
            'goal': self.goal,
            'objective': self.objective,
            'physical_parameters': self.physical_parameters,
            'observations': self.observations
        }

        for field_name, value in required.items():
            if not value or not value.strip():
                missing.append(field_name)

        return missing

    def to_dict(self) -> dict[str, Optional[str]]:
        """Convert STMData to dictionary format.

        Returns:
            Dictionary with field names as keys and content as values
        """
        return {
            'goal': self.goal,
            'objective': self.objective,
            'code_purpose': self.code_purpose,
            'physical_parameters': self.physical_parameters,
            'observations': self.observations,
            'instrument_requirements': self.instrument_requirements,
            'mission_requirements': self.mission_requirements,
            'expected_performance': self.expected_performance
        }
