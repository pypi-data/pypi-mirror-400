import dataclasses
from typing import Sequence

from hwo_disra.EAC import EAC
from hwo_disra.Timeinator import Timeinator
from hwo_disra.Yieldinator import Yieldinator
from hwo_disra.Types import Range
from hwo_disra.yield_sample import YieldSample


# Represents the resulting Yield values from evaluating the
# Yieldinator at the given variable values and with the given EAC.
@dataclasses.dataclass
class EACResults:
    eac: EAC
    sample_points: list[YieldSample]

@dataclasses.dataclass
class YieldResult:
    timeinator: Timeinator
    eac_results: list[EACResults]

class DummyTimeinator(Timeinator):
   def independent_variables(self):
       return {'mag': Range(26, 33),
               'sky_coverage': Range(0, 0.2)}

   def timeinate(self, eac, mag, sky_coverage):
       return (mag * sky_coverage, sky_coverage)

class DRMinator(object):
    def __init__(self,
                 science_cases: Sequence[Timeinator] | Sequence[Yieldinator],
                 eacs: Sequence[EAC],
                 steps = 11):
        assert eacs != []
        assert science_cases != []
        self.science_cases: Sequence[Timeinator] | Sequence[Yieldinator] = science_cases
        self.eacs = eacs
        self._STEPS = steps

    def compute_yields(self) -> list[YieldResult]:
        """
        Evaluate each science case at each EAC.  If a science case
        Yieldinator defines variable ranges sample the range at a
        configurable step resolution.
        """
        results = []

        for yieldinator in self.science_cases:
            yield_result_cases: list[EACResults] = []
            variables = yieldinator.independent_variables()
            assert 'time' not in variables, "Dictionary cannot contain 'time' as a key"
            assert 'yield' not in variables, "Dictionary cannot contain 'yield' as a key"

            # If no variables, evaluate directly for each EAC
            if not variables:
                for eac in self.eacs:
                    yield_result, result_time = yieldinator.timeinate(eac)
                    yield_result_cases.append(EACResults(eac, [YieldSample(
                        yield_result = yield_result,
                        time = result_time
                    )]))
                results.append(YieldResult(yieldinator, yield_result_cases))
                continue

            # Generate variable combinations
            var_combinations = []
            for var_name, var_range in variables.items():
                if isinstance(var_range, Range):
                    start, end = var_range.min, var_range.max
                    # Use 10 steps by default, can be made configurable
                    step = (end - start) / float(self._STEPS - 1)
                    values = [start + i * step for i in range(self._STEPS)]
                    var_combinations.append([(var_name, v) for v in values])
                else:
                    var_combinations.append([(var_name, var_range)])

            # for v in var_combinations:
                # print(v)

            # Calculate cartesian product of all variable combinations
            from itertools import product
            for eac in self.eacs:
                eac_results: list[YieldSample] = []
                for combo in product(*var_combinations):
                    var_dict = dict(combo)
                    yield_result, result_time = yieldinator.timeinate(eac, **var_dict)
                    eac_results.append(YieldSample(
                        yield_result = yield_result,
                        time = result_time,
                        variable_values = var_dict.copy()
                    ))
                yield_result_cases.append(EACResults(eac, eac_results))

            results.append(YieldResult(yieldinator, yield_result_cases))

        return results

if __name__ == '__main__':
    print(DRMinator([DummyTimeinator(None)], [10]).compute_yields())
