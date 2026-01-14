from itertools import product
from typing import Mapping
from hwo_disra.EAC import EAC
from hwo_disra.Yieldinator import Yieldinator, Thresholds, YieldEvaluation
from hwo_disra.Types import Range, ScienceYield, Time
from hwo_disra.yield_sample import YieldSample
import astropy.units as u


class Timeinator(object):
    """
    This class wraps a Yieldinator, which supports Panel 1 analysis and
    extends it to support Panel 2 analysis.  e.g. for a specific
    observatory, what is the cost of achieving the yield, in exposure time.
    """

    def __init__(self, yieldinator: Yieldinator, time_units: u.UnitBase | str) -> None:
        """
        yieldinator: Yieldinator for which this will compute the exposure time for.
        time_units: The astropy.units for the times returned by this Timeinator.
        """
        self._yieldinator = yieldinator
        self._time_units = time_units

    def thresholds(self) -> Thresholds:
        return self._yieldinator.thresholds()

    def levels(self) -> list[float]:
        return self._yieldinator.levels()

    def independent_variables(self) -> Mapping[str, float | Range]:
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
        return self._yieldinator.independent_variables()

    def units(self) -> dict[str, u.UnitBase | str]:
        """
        Return the dictionary of units mapping variable names to their units,
        along with 'yield' and 'time' mapped to the units for yield and time.
        """
        return self._yieldinator.units() | {'time': self._time_units}

    def timeinate(self, eac: EAC, **kwargs) -> tuple[ScienceYield, Time]:
        """"
        Compute the yield from the parameters, which are drawn from
        the independent_variables method values.
        """
        return ScienceYield(0), Time(0)

    def eval(self, eac: EAC, steps = 11) -> YieldEvaluation:
        idv = self.independent_variables()
        if not idv or len(idv) == 0:
            yield_result, time = self.timeinate(eac)
            return YieldEvaluation([YieldSample(yield_result = yield_result,
                                                time = time)],
                                   units = self.units())
        else:
            sample_points = Yieldinator.generate_variable_combinations(idv, steps)
            results = []
            for combo in product(*sample_points):
                var_dict = dict(combo)
                yield_result, time = self.timeinate(eac, **var_dict)
                results.append(YieldSample(
                    yield_result = yield_result,
                    time = time,
                    variable_values = var_dict.copy()
                ))
            return YieldEvaluation(results, eac = eac.name, units = self.units())
