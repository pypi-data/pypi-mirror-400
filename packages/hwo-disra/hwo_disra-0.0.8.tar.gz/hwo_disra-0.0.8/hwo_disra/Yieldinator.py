import dataclasses
from itertools import product
from typing import Mapping, NewType
import astropy.units as u

from hwo_disra.Types import Range, ScienceYield, DiscretePoints, SinglePoint
from hwo_disra.yield_sample import YieldSample

Thresholds = NewType('Thresholds', Mapping[str, float])
VariableMap = NewType('VariableMap', Mapping[str, float | Range])

@dataclasses.dataclass
class YieldEvaluation:
    sample_points: list[YieldSample]
    units: dict[str, u.UnitBase | str]
    # Only present for Timeinator evaluations, name of EAC model.
    eac: str = None

class Yieldinator(object):
    """
    This class defines what is needed to support analysis for "Panel 1"
    when exploring the trade space.  What is needed to achieve different
    levels of science value returns, independent of any given
    observatory.

    The Timeinator defines the necessary extensions to support analysis
    to panel 2, what can a specific observatory achieve and how much
    would that cost in time.
    """

    def __init__(self, yield_units: u.UnitBase | str) -> None:
        """
        yield_units: The astropy.units of the values returned by the yieldinator method.
        """
        self._yield_units = yield_units

    def thresholds(self) -> Thresholds:
        """
        This defines what science yields are required to meet the mapped
        science value thresholds.  Not all science values need be mapped,
        only the values relevant to the science case.
        """
        return {}

    def levels(self) -> list[float]:
        return sorted([level for level in self.thresholds().values()])

    def independent_variables(self) -> VariableMap:
        """
        Return a dictionary of additional variables needed to compute the
        yield. e.g.
        {'magnitude': (26, 33), 'sky_coverage': (0, 0.2)}

        The DRMinator will draw from these ranges when analyzing the
        yield.  e.g. a call may then be:
        self.yieldinator(eac1, magnitude=27, sky_coverage=0.15)

        NOTE: 'time' and 'yield' may _not_ be variable names in the
              dictionary.
        """
        return {}

    def units(self) -> dict[str, u.UnitBase | str]:
        """
        Return a dictionary mapping each variable name to the unit declared
        for that variable, along with 'yield' mapped to the unit of the yields
        returned by this yieldinator.
        """
        variables = self.independent_variables()
        return {k : variables[k].units for k in variables} | {'yield': self._yield_units}

    def yieldinator(self, *args: float, **kwargs) -> ScienceYield:
        """"
        Compute the yield from the parameters, which are drawn from
        the independent_variables method values.
        """
        return ScienceYield(0)

    def eval(self, steps = 11) -> YieldEvaluation:
        """

        """
        idv = self.independent_variables()
        if not idv or len(idv) == 0:
            yield_result = self.yieldinator()
            return YieldEvaluation([YieldSample(yield_result = yield_result)],
                                   units = self.units())
        else:
            sample_points = self.generate_variable_combinations(idv, steps)
            results = []
            for combo in product(*sample_points):
                var_dict = dict(combo)
                yield_result = self.yieldinator(**var_dict)
                results.append(YieldSample(
                    yield_result = yield_result,
                    variable_values = var_dict.copy()
                ))
            return YieldEvaluation(results, units = self.units())

    @staticmethod
    def generate_variable_combinations(variables, steps):
        var_combinations = []
        for var_name, var_range in variables.items():
            if isinstance(var_range, Range):
                start, end = var_range.min, var_range.max
                # Use 10 steps by default, can be made configurable
                step = (end - start) / float(steps - 1)
                values = [start + i * step for i in range(steps)]
                var_combinations.append([(var_name, v) for v in values])
            elif isinstance(var_range, DiscretePoints):
                var_combinations.append([(var_name, val) for val in  var_range.items])
            elif isinstance(var_range, SinglePoint):
                var_combinations.append([(var_name, var_range.value)])
            else:
                var_combinations.append([(var_name, var_range)])

        return var_combinations


