from pathlib import Path
import pytest

import hwo_disra.environment  # noqa: F401
from hwo_disra.DRMinator import DRMinator
from hwo_disra.yields.QSOYieldinator import QSOTimeinator, QSOYieldinator, QSOPlotinator
from hwo_disra.EAC import create_syo_eac

@pytest.mark.skip
def test_qso():

    eacs = [create_syo_eac(name) for name in ['EAC1', 'EAC2', 'EAC3']]
    qso10 = QSOTimeinator(QSOYieldinator(iterations=3), snr=10)
    qso20 = QSOTimeinator(QSOYieldinator(iterations=3), snr=20)
    print(qso10)
    drm = DRMinator(science_cases=[qso10, qso20], eacs=eacs, steps=3)

    drm_results = drm.compute_yields()
    print(drm_results)
    for result_set in drm_results:
        (timeinator, eac_results) = result_set.timeinator, result_set.eac_results
        print(eac_results)
        plotter = QSOPlotinator(output_dir=Path("tests/outputs"),
                             file_prefix="qso")
        plotter.barchart(timeinator, eac_results, x_key="EAC", y_key="Time (hr)", z_key=None)
        for x in eac_results:

            # print(results)
            # plotter.contour_plot(results, 'sky_coverage', 'magnitude', 'yield_result',
            #                    contour_levels=sorted(timeinator.thresholds().values()),
            #                    file_prefix=eac.name)

            camera_fov = (2.0*3.0)/(60*60.)   # HRI field-of-view in sq. deg. TO DO: Read from .yaml file

            def time_transform(time, sky_coverage, yield_result):
                if yield_result <= 1 - 0.95:
                    return (sky_coverage / camera_fov) * time / (24.0 * 60 * 60)
                else:
                    return float("nan")

            # plotter.contour_plot(results, 'sky_coverage', 'magnitude', 'time',
            #                    contour_levels=[0.1, 1.0, 2.0, 10.0, 30.0],
            #                    transforms={'time': time_transform },
            #                    axis_labels={'sky_coverage': "Survey Sky Coverage (deg$^{2}$)",
            #                                 'magnitude': "Survey Depth (R mag limit)",
            #                                 'time': "Total Survey Time (days)"},
            #                     title=f"{eac.name}({eac.telescope.aperture})",
            #                     file_prefix=eac.name)




if __name__ == "__main__":
    test_qso()
