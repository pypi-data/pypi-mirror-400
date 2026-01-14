import bisect
from pathlib import Path
from typing import Dict
import astropy.units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord, match_coordinates_sky
import numpy as np

from matplotlib import pyplot as plt

from hwo_disra.EAC import EAC
from hwo_disra.Yieldinator import Yieldinator
from hwo_disra.Types import ScienceValue, ScienceYield, Time
from hwo_disra.Timeinator import Timeinator
from hwo_disra.Plotinator import Plotinator
from hwo_disra.DRMinator import EACResults
from syotools.models import Telescope, Spectrograph, Source, SourceSpectrographicExposure

DRM_DATA_DIR = "/".join(__file__.split("/")[:-1]) + "/../data"


class QSOYieldinator(Yieldinator):


    def __init__(self, iterations=None, inner_angle=0.05 * u.arcsec):
        super().__init__('unknown')

        self.plots = False
        self.inner_angle = inner_angle

        # load the target table
        self.catalog = self.load_table()

        # catch-all for operations on the table
        self.catalog_operations()

    def thresholds(self):
        """Thresholds and yield are numbers of targets"""
        return {ScienceValue.ENABLING: (50, 5),
                ScienceValue.ENHANCING: (100, 10)}
    
    def independent_variables(self):
        """
        This particular case has none
        """
        variables = {}
        return variables

    def load_table(self):
        """
        Load the catalog of candidate QSOs
        Clean the table
        """
        qsocat = Table.read(f'{DRM_DATA_DIR}/dr7qso_galex.fits')
        qsocat = qsocat['SDSSNAME', 'RA', 'DEC', 'Z', 'PSFMAG_G', 'PSFMAGERR_G', 'FUV_MAG', 'NUV_MAG']
        qsocat['gal_pathlength'] = qsocat['Z'] - 0.5 - 0.1
        qsocat['gal_pathlength'][qsocat['gal_pathlength'] < 0.] = 0.

        return qsocat
    
    def catalog_operations(self):
        # sort the stars into bins (store their indices) and by RPmag.
        self.catalog = self.catalog[self.catalog['FUV_MAG'] > 0.]
        self.catalog = self.catalog[self.catalog['FUV_MAG'] < 20.]
        self.catalog = self.catalog[self.catalog['Z'] < 2.]
        self.catalog = self.catalog[self.catalog['Z'] > 0.51]
        #plt.scatter(self.catalog['Z'], self.catalog['FUV_MAG'], marker='o', s=0.1, color='red')

        self.catalog["_pathlength_sort"] = self._normalize(self.catalog['gal_pathlength']) / self._normalize(self._mag_to_linear(self.catalog['FUV_MAG']))
        self.catalog.sort('_pathlength_sort')

        print(self.catalog.keys())
        print(self.catalog)

        # get all closest distances, to sort later.
        #self.resolved = Resolvinator(self.catalog)
        catalogcoord = SkyCoord(ra=self.catalog["RA"], dec=self.catalog["DEC"], unit=(u.deg, u.deg))

        # When matching a catalog against itself, the 2nd neighbor is what you want. 
        closest, self.sep2d, dist3d = match_coordinates_sky(catalogcoord, catalogcoord, nthneighbor=2, storekdtree='kdtree_sky')


    def plot(self, filename="QSO_Yield.png"):
        from matplotlib import pyplot as plt
        plt.scatter(self.catalog['Z'], self.catalog['FUV_MAG'], marker='o', s=0.1, color='red')
        plt.ylim(17,21)
        plt.xlim(0, 2.)
        plt.xlabel('Redshift z')
        _ = plt.ylabel('QSO FUV Mag')

        plt.savefig(filename)


    def yieldinator(self, iwa, *args) -> ScienceYield:
        """
        The path length of the top (targets) targets.

        Parameters
        ----------
        iwa: float
            Inner Working Angle (in arcseconds)

        Returns
        -------
        ScienceYield
            The scientific yield in the chosen units
        """

        # Without an EAC to process calculation times, the only thing we can do is figure out the complete path length of the entire table.
        # # process times
        # mag_list = (np.arange(11)*0.5 + 15.)
        # exptime_list = []
        # for mag in mag_list:
        #     wave, exp, uvi = self.exposure_time_at_eac(eac, mag, snr_goal, silent=True)
        #     exptime_list.append(exp[8425].to_value("hour"))   #<---- picked 1150 A somewhat arbitrarily, 3600 converts sec to hours

        # self.catalog["exptime"] = np.interp(self.catalog['FUV_MAG'], mag_list, exptime_list)

        # self.catalog["path_per_exptime"] = self.catalog["pathlength"]/self.catalog["exptime"]

        # self.catalog.sort("path_per_exptime", reverse=True)

        self.observed_catalog = self.catalog[self.sep2d > iwa]

        print(self.observed_catalog)

        return np.sum(self.observed_catalog["pathlength"])

    def _normalize(self, column):
        # standard datascience normalization
        return (column - np.mean(column))/ np.std(column)

    def _mag_to_linear(self,column):
        # assumes column is a magnitude, so it can be normalized and handled like other quantities
        return np.exp(column/-2.5)

class QSOTimeinator(Timeinator):

    def __init__(self, yieldinator: Yieldinator, snr=10.0) -> None:
        #super().__init__(yieldinator)

        self._yieldinator = yieldinator
        self.silent = True

        self._SNR_GOAL = snr
        self._TEMPLATE = "Flat (AB)"
        self._ELEMENT = "G120M"

    def timeinate(self, eac: EAC) -> tuple[ScienceYield, Time]:

        #To match the yieldinator, we only process the entire catalog.
        # process times
        mag_list = (np.arange(11)*0.5 + 15.)
        exptime_list = []
        for mag in mag_list:
            wave, exp = self.exposure_time_at_eac(eac, mag, self._SNR_GOAL, silent=True)
            waveidx = bisect.bisect(wave, 1150 * u.angstrom)
            exptime_list.append(exp[waveidx].to_value("hour"))   #<---- picked 1150 A somewhat arbitrarily, 3600 converts sec to hours

        times = np.interp(self._yieldinator.catalog['FUV_MAG'], mag_list, exptime_list)

        if not self.silent:
            print("Base Times", exptime_list)
            print("Show times", times)

        self._yieldinator.catalog[f"{eac}_total_exposure_time_sn{self._SNR_GOAL}"] = times

        return len(self._yieldinator.catalog), np.sum(times)


    def exposure_time_at_eac(self, eac: EAC, magnitude: float, snr: float, silent=True) -> Time:
        # Create the basic objects
        uvi = eac.spectrograph()
        uvi.mode = self._ELEMENT
        #eac.telescope.add_spectrograph(uvi)
        uvi_exp = SourceSpectrographicExposure()

        source = Source()
        source.set_sed(self._TEMPLATE, magnitude=magnitude, redshift=0, extinction=0, bandpass="v")

        # Exposures need a source, telescope, and spectrograph.
        uvi_exp.source = source
        uvi_exp.telescope = eac.telescope
        uvi_exp.spectrograph = uvi
        uvi_exp.camera = None

        uvi_exp.unknown = 'exptime' # call this before setting the SNR, so that the change is accepted
        uvi_exp._snr_goal = snr
        uvi_exp.verbose=False

        uvi_exp.calculate()
        uvi_exptime = uvi_exp.recover('exptime')
        #uvi_exptime = np.nanmax(uvi_exptime)
        return uvi.wave, uvi_exptime

    def uvspec_exptime(telescope, mode, template, fuvmag, snr_goal, silent=False):

        ''' Run a basic SNR calculation that takes in a telescope,
        spectral template, normalization magnitude, and SNR goal
        to compute exposure time. For converting magnitude, template,
        and exptime to SNR, use uvspec_snr.py

            usage:
            wave, exptime, uvi = uvspec_exptime(telescope, mode, template, uvmag, snr_goal)

            positional arguments:

            1-telescope = 'EAC1', 'EAC2', or 'EAC3'. This argument is a string.
                EAC1 = 6 m inner diameter, 7.2 outer diameter hex pattern, off-axis
                EAC2 = 6 m diameter off-axis
                EAC3 = 8 m diameter on-axis

            2-mode = your choice of UVI grating, a string:
                    ['G120M', 'G150M', 'G180M', 'G155L', 'G145LL', 'G300M']

            3-template = your choice of spectral template:
                    ['flam', 'qso', 's99', 'o5v', 'g2v', 'g191b2b', 'gd71', 'gd153', 'ctts',
                            'mdwarf', 'orion', 'nodust', 'ebv6', 'hi1hei1', 'hi0hei1']

            4-fuvmag = FUV magnitude to normalize the template spectrum, a float.

            5-snr_goal = desired SNR, per pixel

            outputs are two arrays of floats for wavelength and exptime and the Spectrograph
                object in case it is needed by other code.
        '''

        from syotools.models import Source, SourceSpectrographicExposure
        import astropy.units as u

        # create the basic objects
        uvi, tel = Spectrograph(), Telescope()
        tel.set_from_json(telescope)
        tel.add_spectrograph(uvi)
        uvi.mode = mode

        source = Source()
        redshift = 0.0
        extinction = 0.0
        source.set_sed(template, fuvmag, redshift, extinction, bandpass="galex,fuv")

        uvi_exp = SourceSpectrographicExposure()
        uvi_exp.source = source
        uvi_exp.verbose = not silent
        uvi.add_exposure(uvi_exp)

        if not silent:
            print("Current SED template: {}".format(source.sed.name))
            print("Current grating mode: {}".format(uvi.descriptions[uvi.mode]))
            print("Current exposure time: {} hours\n".format(uvi_exp.exptime))

        uvi_exp._snr_goal= snr_goal * (u.ct)**0.5 / (u.pix)**0.5

        uvi_exp.recover('exptime')
        uvi_exp.unknown = 'exptime' #< --- this triggers the _update_exptime function in the SpectrographicExposure exposure object

        uvi_exp.recover('exptime')

        wave, exptime =  uvi.wave, uvi_exp.exptime

        return wave, exptime, uvi

class QSOPlotinator(Plotinator):
    def __init__(self, file_prefix: str | None = None,
                 output_dir: Path | None = None,
                 show_plots: bool = False, qsocat: Table | None = None, eac: EAC | None = None):
        super().__init__(file_prefix=file_prefix,
                 output_dir=output_dir,
                 show_plots=show_plots)

        if qsocat is not None:
            qsocat[eac+'_pathlength_per_hour_sn10'] = qsocat['gal_pathlength'] / qsocat[eac+'_exptime_snr_10']
            qsocat[eac+'_pathlength_per_hour_sn20'] = qsocat['gal_pathlength'] / qsocat[eac+'_exptime_snr_20']
            qsocat[eac+'_total_exposure_time_sn10'] = qsocat['Z'] * 0.0
            qsocat[eac+'_total_exposure_time_sn20'] = qsocat['Z'] * 0.0
            qsocat[eac+'_total_pathlength_sn10'] = qsocat['Z'] * 0.0
            qsocat[eac+'_total_pathlength_sn20'] = qsocat['Z'] * 0.0

            self.catalog = qsocat

    def figure1(self, eac):

        plt.scatter(self.catalog['Z'], self.catalog['EAC1_pathlength_per_hour_sn10'], linestyle='solid', label='SNR = 10')
        plt.scatter(self.catalog['Z'], self.catalog['EAC1_pathlength_per_hour_sn20'], color='orange', label='SNR = 20')
        plt.legend()
        plt.xlabel('QSO Redshift')
        plt.ylabel('Pathlength per Hour')
        _ = plt.title('Pathlength per Hour, EAC1 only')

        self.write_plot("qso_figure1.png")

    def figure2(self):

        plt.plot(self.catalog['EAC1_total_exposure_time_sn10'], self.catalog['EAC1_total_pathlength_sn10'], label='EAC1, SNR = 10', color='blue')
        plt.plot(self.catalog['EAC2_total_exposure_time_sn10'], self.catalog['EAC2_total_pathlength_sn10'], linestyle='dotted', label='EAC2, SNR = 10', color='blue')
        plt.plot(self.catalog['EAC3_total_exposure_time_sn10'], self.catalog['EAC3_total_pathlength_sn10'], linestyle = 'dashed', label='EAC3, SNR = 10', color='blue')

        plt.xlabel('Total Hours')
        plt.legend()
        plt.xlim(-10,500)
        plt.ylim(-20,1000)
        plt.title('Total Pathlength vs. Exposure Time, SNR = 10')
        _ = plt.ylabel('Total Pathlength')

        self.write_plot("qso_figure2.png")

    def barchart(self, timeinator: Timeinator, eac_results: list[EACResults],
                    x_key: str, y_key: str, z_key: str,
                    title='', filename="qso_bar.png",
                    transforms: Dict[str, callable] = {},
                    axis_labels: Dict[str, str] = {},
                    file_prefix: str = "qso"):
        names = []
        exptimes = []
        for res in eac_results:
            eac, result = res.eac, res.sample_points
            print(result)
            names.append(str(eac))
            exptimes.append(np.median([x["time"] for x in result]))

        super().barplot(names, exptimes, [],
                    x_key, y_key, z_key,
                    title=title, filename=filename,
                    transforms = transforms,
                    axis_labels = axis_labels,
                    file_prefix = file_prefix)

            
