from syotools.models.telescope import Telescope
from syotools.models.camera import Camera
from syotools.models.source_exposure import SourceExposure
from syotools.models import Spectrograph, Source
import astropy.units as u



# Model from SEI interface YAML files used to check SNR
# or needed exposure time to reach a given level of significance.
class EAC:
    def create_exposure(self) -> SourceExposure:
        pass

    @property
    def telescope(self) -> Telescope:
        pass

    def camera(self) -> Camera:
        pass

    @property
    def name(self) -> str:
        pass

class SyotoolsEAC(EAC):
    def __init__(self, telescope: Telescope):
        super().__init__()
        self._telescope = telescope

    @property
    def telescope(self):
        return self._telescope

    def create_exposure(self):
        return self.camera().create_exposure()

    def camera(self):
        camera = self._telescope.cameras[0]
        return camera

    def spectrograph(self):
        spectrograph = self._telescope.spectrographs[0]
        return spectrograph

    def exposure_time_for_magnitude(self, magnitude,
        snr_goal = 50,
        rband_index = 5,
        template = 'G2V Star'):
        # Create the basic objects
        exp = self.create_exposure()
        source = Source()
        redshift = 0. # changes to these are not implemented yet
        extinction = 0.

        source.set_sed(template, magnitude, redshift, extinction, bandpass="johnson,v")

        exp.source = source
        exp._snr = [snr_goal] * u.Unit('electron(1/2)')
        exp.unknown = 'exptime'
        hri_exptime = exp.recover('exptime')
        return hri_exptime[rband_index].value

    @property
    def name(self):
        return self._telescope.name
    
    def __repr__(self):
        return f"<{self._telescope.name}> object"

def create_syo_eac(name: str) -> EAC:
    telescope = Telescope()
    telescope.set_from_sei(name)
    spec = Spectrograph()
    telescope.add_spectrograph(spec)
    hri = Camera()
    hri.set_from_sei('HRI')
    telescope.add_camera(hri)
    return SyotoolsEAC(telescope)