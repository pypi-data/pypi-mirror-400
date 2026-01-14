import dataclasses
from typing import Mapping


@dataclasses.dataclass
class YieldSample(Mapping):
  yield_result: float
  time: float = None
  variable_values: Mapping[str, float] = dataclasses.field(default_factory=dict)

  # @override
  def __len__(self):
    return 2 + len(self.variable_values)

  def __iter__(self):
    """Iterate over all available keys like a dictionary."""
    yield 'yield'
    yield 'time'
    yield from self.variable_values.keys()

  # @override
  def __getitem__(self, key: str) -> float:
    """Allow dictionary-like access to yield_result, time, and variable_values."""
    if key == 'yield_result' or key == 'yield':
      return self.yield_result
    elif key == 'time':
      return self.time
    elif key in self.variable_values:
      return self.variable_values[key]
    else:
      raise KeyError(f"Key '{key}' not found in YieldSample")
