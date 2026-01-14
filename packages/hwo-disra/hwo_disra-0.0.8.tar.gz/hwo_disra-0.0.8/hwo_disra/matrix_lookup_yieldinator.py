import numpy as np
from scipy.interpolate import RegularGridInterpolator
import astropy.units as u

from hwo_disra.Types import ScienceYield, Range
from hwo_disra.Yieldinator import Yieldinator, VariableMap, Thresholds


class MatrixLookupYieldinator(Yieldinator):
  def __init__(self, x_values: np.ndarray, y_values: np.ndarray,
               matrix: np.ndarray,
               thresholds: Thresholds,
               yield_units: u.UnitBase | str,
               variable_x: str = 'x',
               variable_y: str = 'y') -> None :
    super().__init__(yield_units)
    self.variable_y = variable_y
    self.variable_x = variable_x
    self._thresholds = thresholds
    self._x_values = x_values
    self._y_values = y_values
    self._matrix = matrix
    self._interp = RegularGridInterpolator((self._x_values, self._y_values),
                                           matrix, method='linear')

  def thresholds(self) -> Thresholds:
    return self._thresholds

  def independent_variables(self) -> VariableMap:
    return {
      self.variable_x: Range(self._x_values.min(),  self._x_values.max()),
      self.variable_y: Range(self._y_values.min(),  self._y_values.max())
    }

  def yieldinator(self, **kwargs) -> ScienceYield:
    x = kwargs[self.variable_x]
    y = kwargs[self.variable_y]
    return ScienceYield(self._interp((x, y)).item())

