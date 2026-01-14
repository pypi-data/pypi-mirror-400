import os
import syotools
import hwo_sci_eng


def setup_environment():
    """
    Set up PYSYN_CDBS and SCI_ENG_DIR environment variables.
    
    This function configures the environment variables required by hwo_disra
    by finding the correct paths to syotools and hwo_sci_eng packages.
    """
    syotools_loc = os.path.dirname(syotools.__file__)
    os.environ['PYSYN_CDBS'] = (
        os.path.join(syotools_loc, 'reference_data', 'pysynphot_data'))
    
    for p in hwo_sci_eng.__path__:
        root = os.path.join(os.path.dirname(hwo_sci_eng.__path__[0]), 'hwo_sci_eng')
        if os.path.isdir(os.path.join(root, "obs_config")):
            os.environ['SCI_ENG_DIR'] = root
            break


setup_environment()