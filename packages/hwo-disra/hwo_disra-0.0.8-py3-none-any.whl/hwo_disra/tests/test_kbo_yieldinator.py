from pathlib import Path
import os
import hwo_disra.environment  # noqa: F401
from hwo_disra.EAC import create_syo_eac
from hwo_disra.Plotinator import Plotinator
from hwo_disra.DRMinator import DRMinator
from hwo_disra.yields.KBOYieldinator import KBOTimeinator, KBOYieldinator

# noinspection PyUnresolvedReferences

assert os.environ['SCI_ENG_DIR']

def test_kbo():

    # Compute piece.
    eacs = [create_syo_eac(name) for name in ['EAC1', 'EAC2', 'EAC3']]
    kbo = KBOTimeinator(KBOYieldinator(iterations=11))
    drm = DRMinator([kbo], eacs, steps=11)

    drm_results = drm.compute_yields()

    # Plot matrix generation piece.
    for result_set in drm_results:
        (timeinator, eac_results) = result_set.timeinator, result_set.eac_results
        output_dir = Path(os.path.join(os.path.dirname(__file__), 'outputs'))
        plotter = Plotinator(output_dir=output_dir,
                             file_prefix="kbo")
        for x in eac_results:
            eac, results = x.eac, x.sample_points
            # print(results)
            plotter.contour_plot([results], 'sky_coverage', 'magnitude', 'yield_result',
                               contour_levels=sorted(timeinator.thresholds().values()),
                               file_prefix=eac.name)

            def time_transform(time, yield_result):
                if yield_result <= 1 - 0.95:
                    return time / (24.0 * 60 * 60)
                else:
                    return float("nan")

            plotter.contour_plot([results], 'sky_coverage', 'magnitude', 'time',
                               contour_levels=[0.1, 1.0, 2.0, 10.0, 30.0],
                               transforms={'time': time_transform },
                               axis_labels={'sky_coverage': "Survey Sky Coverage (deg$^{2}$)",
                                            'magnitude': "Survey Depth (R mag limit)",
                                            'time': "Total Survey Time (days)"},
                                titles=[f"{eac.name}({eac.telescope.effective_aperture})"],
                                file_prefix=eac.name)
