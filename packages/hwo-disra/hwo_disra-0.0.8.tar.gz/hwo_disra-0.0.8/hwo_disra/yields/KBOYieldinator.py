import numpy as np
import scipy
import pickle

from hwo_disra.EAC import EAC
from hwo_disra.Timeinator import Timeinator
from hwo_disra.Types import Time, ScienceYield, Range, ScienceValue
from hwo_disra.Yieldinator import Yieldinator
import astropy.units as u

from syotools.models.source import Source
from syotools.models.source_exposure import SourcePhotometricExposure

class KBOYieldinator(Yieldinator):

    def __init__(self, iterations = 50):
        super().__init__(yield_units='p-value')
        # Ranges of depth and sky coverage to test
        self.survey_depth = np.arange(36)*0.20 + 26.0    # R band apparent magnitude
        self.survey_omega = np.arange(41)*0.0005         # Survey area in sq. deg.
        self.m = np.arange(1101)*0.01 + 22.0  # R band apparent magnitude
        self.sigma_taper = taper(self.m)
        self.sigma_roll = rolling(self.m)

        self._ITERATIONS = iterations
        # try_load = self.try_load_ks_matrix()
        # self.ks_matrix = try_load if try_load is not None else self.compute_ks_matrix()
        self.ks_matrix = self.compute_ks_matrix()

    def compute_ks_matrix(self):
        # Simulate datasets and compare with K-S test. Repeat to smooth out stochastic
        # behavior.
        ks_matrix = np.zeros(shape=(len(self.survey_depth),len(self.survey_omega)))
        tests = self._ITERATIONS  # Should actually iterate to convergence
        for k in range(tests):
          for i in range(len(self.survey_depth)):
            a = np.nonzero(self.m <= self.survey_depth[i])[0]
            for j in range(len(self.survey_omega)):
              self.points_taper = add_noise(self.sigma_taper[a]*self.survey_omega[j])
              self.points_roll = add_noise(self.sigma_roll[a]*self.survey_omega[j])
              res = scipy.stats.ks_2samp(self.points_taper, self.points_roll, alternative='two-sided')
              ks_matrix[i,j] = ks_matrix[i,j] + res[1]
        ks_matrix = ks_matrix/tests
        # with open("ks_matrix.pickle", "wb") as f:
        #   pickle.dump(ks_matrix, f)
        return ks_matrix

    def try_load_ks_matrix(self):
      try:
        with open("ks_matrix.pickle", "rb") as f:
          return pickle.load(f)
      except Exception:
         return None

    def thresholds(self):
        """Thresholds and yield are p-values"""
        return {ScienceValue.ENHANCING: ScienceYield(1 - 0.95),
                ScienceValue.ENABLING: ScienceYield(1 - 0.9973)}

    def independent_variables(self):
        return {'magnitude': Range(26,  33), 'sky_coverage': Range(0,  0.02)}

    def yieldinator(self, magnitude: float, sky_coverage: float) -> ScienceYield:
      # print(f"mag: {magnitude}, sky_cov: {sky_coverage}")
      mag_ix = np.searchsorted(self.survey_depth, magnitude)
      cov_ix = np.searchsorted(self.survey_omega, sky_coverage)

      # Get bracketing values
      d1 = self.survey_depth[mag_ix-1]
      d2 = self.survey_depth[mag_ix]
      c1 = self.survey_omega[cov_ix-1]
      c2 = self.survey_omega[cov_ix]

      # Calculate weights based on relative position
      wi = (magnitude - d1) / (d2 - d1)
      wj = (sky_coverage - c1) / (c2 - c1)

      i0 = mag_ix - 1
      i1 = mag_ix
      j0 = cov_ix - 1
      j1 = cov_ix

      # Bilinear interpolation
      interp_yield = (1-wi)*(1-wj)*self.ks_matrix[i0,j0] + \
              (1-wi)*wj*self.ks_matrix[i0,j1] + \
              wi*(1-wj)*self.ks_matrix[i1,j0] + \
              wi*wj*self.ks_matrix[i1,j1]

      return ScienceYield(interp_yield)

class KBOTimeinator(Timeinator):

    Rband_index = 5

    def __init__(self, yieldinator: Yieldinator) -> None:
       super().__init__(yieldinator, u.s)
       self._SNR_GOAL = 5.0
       self._TEMPLATE = 'G2V Star' # 'GV2'

    def timeinate(self, eac: EAC, magnitude: float, sky_coverage: float) -> tuple[ScienceYield, Time]:
       return (self._yieldinator.yieldinator(magnitude, sky_coverage),
               self.exposure_time_at_eac(eac, magnitude, sky_coverage))

    def exposure_time_at_eac(self, eac: EAC, magnitude, sky_coverage) -> Time:
      hri = eac.camera()
      # TODO: Once we're on the SEI yaml read this from there.
      camera_fov = (2.0*3.0)/(60*60.)   # HRI field-of-view in sq. deg.
      nvisits = np.ceil(sky_coverage/camera_fov)

      source = Source()
      redshift = 0. # changes to these are not implemented yet
      extinction = 0.

      source.set_sed(self._TEMPLATE, magnitude, redshift, extinction, bandpass="johnson,v")

      exp = SourcePhotometricExposure()
      exp.source = source

      exp._snr = [self._SNR_GOAL] * u.Unit('electron(1/2)')
      exp.unknown = 'exptime'
      hri.add_exposure(exp)
      return nvisits * exp.exptime[self.Rband_index].value
      # return camera_exptime(eac.telescope.name.replace('-', ''), self._TEMPLATE, magnitude,
      #                       self._SNR_GOAL, True)[0][self.Rband_index].value

def add_noise(y):
  """
  Simple routine to produce a noisy 1-D array (e.g., smooth function -> scattered points).

  Args:
    y: 1-D array

  Returns: 1-D array drawn from y assuming the uncertainty on each y value is normally distributed

  """
  rng = np.random.default_rng(seed=1346546)
  fake = [0]*len(y)
  for i in range(len(y)):
    fake[i] = y[i] + rng.normal()*np.sqrt(y[i])
  return fake

def rolling(m):
  """
  Rolling power law for the KBO luminosity function (Napier et al. 2024, Eq. 11).

  Args:
    m: array of R band apparent magnitudes

  Returns: number of KBOs per sq. degree as function of R band magnitude
  """
  sigma_23 = 0.28     # number of objects with m_r = 23 per sq. degree
  alpha1_roll = 0.89
  alpha2_roll = -0.07

  sigma_roll = sigma_23 * 10**( alpha1_roll*(m-23.0) + alpha2_roll*(m-23.0)**2.0 )
  return sigma_roll   # Number of KBOs per sq. degree as function of R band magnitude

def taper(m):
  """
  Exponentially Tapered power law for the KBO luminosity function (Napier et al. 2024, Eq. 13).

  Args:
    m: array of R band apparent magnitudes

  Returns: number of KBOs per sq. degree as function of R band magnitude
  """
  alpha_taper = 0.21	# faint-end power-law slope
  beta_taper = 0.14	  # strength of exponential taper
  m0_taper = 13.95    # normalization parameter
  mB_taper = 28.74    # magnitude at which exponential taper begins to dominate

  sigma_taper = np.exp( -10**( beta_taper*(mB_taper-m) ) ) * ( 10**( (alpha_taper-beta_taper)*m - (m0_taper*alpha_taper) ) ) * ( alpha_taper*10**(m*beta_taper) + beta_taper*10**(mB_taper*beta_taper) )
  return sigma_taper

def broken(m):
  """
  Broken power law for the KBO luminosity function (Napier et al. 2024, Eq. 12).

  Args:
    m: array of R band apparent magnitudes

  Returns: number of KBOs per sq. degree as function of R band magnitude
  """
  alpha1_broken = 0.90	# bright end slope
  alpha2_broken = 0.49	# faint end slope
  m0_broken = 23.59	    # normalization parameter
  mB_broken = 24.59	    # magnitude at which break occurs

  a = np.where(m < mB_broken)[0]
  b = np.where(m >= mB_broken)[0]

  sigma_brokenA = 10**( alpha1_broken*(m[a]-m0_broken) )
  sigma_brokenB = 10**( alpha2_broken*(m[b]-m0_broken) + (alpha1_broken-alpha2_broken)*(mB_broken-m0_broken) )

  sigma_broken = np.concatenate((sigma_brokenA, sigma_brokenB)) # should we concatenate these?
  return sigma_broken

def mag_to_km(m):
  """
  Convert R band magnitude to KBO diameter.

  Args:
    m: array of R band apparent magnitudes

  Returns: array of KBO diameters in km
  """
  dia_ref = 2.0 	# Reference diameter (km)
  ref_mag = 33.0 	# Reference R magnitude for 2-km body at 40 AU from Bekki Dawson
  KBO_dia = dia_ref * 10**(-0.2*(m - ref_mag))
  return KBO_dia    # KBO diameter in km

def km_to_mag(KBO_dia):
  """
  Convert KBO diameter to R band magnitude.

  Args:
    m: array of KBO diameters in km

  Returns: array of R band apparent magnitudes
  """
  dia_ref = 2.0 	# Reference diameter (km)
  ref_mag = 33.0 	# Reference R magnitude for 2-km body at 40 AU from Bekki Dawson
  m =  ref_mag - 5.0 * np.log10(KBO_dia/dia_ref)
  return m    # R band magnitude
