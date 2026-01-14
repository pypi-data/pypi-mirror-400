import bisect
import os
from itertools import zip_longest
import astropy.units as u
from astropy.io import ascii

from syotools import source_exposure
from hwo_disra.EAC import EAC
from hwo_disra.Yieldinator import Yieldinator
from hwo_disra.Types import ScienceYield, Time, ScienceValue

#os.environ['PYSYN_CDBS'] = f"{[p for p in sys.path if 'site-packages' in p][0]}/syotools/pysynphot_data/"
#os.environ['SCI_ENG_DIR'] = f"{[p for p in sys.path if 'site-packages' in p][0]}/syotools/sci_eng_interface/"

class CatalogYieldinator(Yieldinator):


    def __init__(self):
        super().__init__('unknown')

        self._SNR_GOAL = 50.0

        self.catalog = self.load_table()

        self.exposure = source_exposure.SourcePhotometricExposure()
        # All of this is to only need to load these spectra once.
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_2500_5.0_2011.fits'), "M8")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_2400_5.0_2011.fits'), "M9.5")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_2200_5.0_2011.fits'), "L0")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_2100_5.0_2011.fits'), "L1")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_2000_5.0_2011.fits'), "L2")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_1600_5.0_2011.fits'), "L5")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_1400_5.0_2011.fits'), "L7")
        self.exposure.load_spec_from_file(os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'phoenixBTS11_15', 'phoenixm0.0_1300_5.0_2011.fits'), "L9")


    def thresholds(self):
        """Thresholds and yield are numbers of targets"""
        return {ScienceValue.ENABLING: (50, 5),
                ScienceValue.ENHANCING: (100, 10)}

    def independent_variables(self):
        return {}

    def yieldinator(self, eac: EAC, number_targets: int) -> tuple[ScienceYield, Time]:
        
        # This will trigger the exposure to be connected to this EAC and its camera
        eac.cameras[0].add_exposure(self.exposure)

        total_time = 0
        for target in self.table_select(number_targets):
            # Create the basic objects
            snr_list = []


            self.exposure.sed_id = target["template"]
            self.exposure.renorm_sed(target["RPmag"] * u.ABmag, bandpass='gaia,rp')
            for i in eac.cameras[0].bandnames: 
                snr_list.append(self._SNR_GOAL)
            self.exposure._snr[1]['value'] = snr_list

            self.exposure.unknown = 'exptime'
            total_time += self.exposure.recover('exptime')
            

        return (number_targets, total_time)
    
    def load_table(self):
        """
        Load the catalog of brown dwarfs and organize by # and bin
        """

        colorbins = [4, 4.5, 5, 5.7, 6.3, 7, 7.5]
        self.containers = {4: [], 4.5: [], 5: [], 5.7: [], 6.3: [], 6.5: [], 7:[], 7.5: [], 10: []}
        self._TEMPLATES = {4: "M8", 4.5: "M9.5", 5: "L0", 5.7: "L1", 6.3: "L2", 7: "L5", 7.5: "L7", 10: "L9"}

        with ascii.read("Brown_Dwarfs_Smart_2019.csv") as catalog:
            # Add a new column for the template
            catalog.add_column("L0", name="template")
            catalog.add_column(catalog["RPmag"] - catalog["W3mag"], name="RP-W3")
            # Sort the table by magnitude, brightest first.
            catalog.sort("RPmag")
            # sift_table actually just creates a sorted index into self.catalog
            self.sift_table(catalog, colorbins)

        return catalog
    
    def sift_table(self, catalog, colorbins):
        """
        Sift the stars into bins by RPMag. To do this without actually modifying the input table, 
        we store sorted indicies in the "containers" structure.

        Parameters
        ----------
        catalog : Astropy Table
            Input brown dwarf catalog
        colorbins: list
            List of the color bins to sort into
        """
        # sort the stars into bins (store their indices) and by RPmag.
        for targetidx in range(len(catalog)):
            color = catalog["RP-W3"][targetidx]
            # which color bin does this target go into?
            key = bisect.bisect(colorbins, color)
            # update its spectral template
            catalog["template"][targetidx] = self._TEMPLATES[key]
            # file it in the appropriate container
            self.containers[key].append(targetidx)

        # now use zip to interleave the lists
        self.index_interleaved = [target for star in zip_longest(**self.containers) for target in star]

    def table_select(self, n_results):
        """
        Get the top (n_results) targets, by just reading the interleaved catalog entries.
        """
        return self.catalog[self.catalog_interleaved[:n_results]]

    def exposure_time_at_eac(self, eac: EAC, magnitude) -> Time:
        # Create the basic objects
        hri_exp = eac.create_exposure()
        hri = eac.camera()

        hri_exp.sed_id = self._TEMPLATE
        hri_exp.renorm_sed(magnitude * u.ABmag, bandpass='v')
        snr_list = []
        for i in hri.bandnames:
            snr_list.append(self._SNR_GOAL)
        hri_exp._snr[1]['value'] = snr_list

        hri_exp.unknown = 'exptime'
        hri_exptime = hri_exp.recover('exptime')
        return hri_exptime[self.Rband_index]
