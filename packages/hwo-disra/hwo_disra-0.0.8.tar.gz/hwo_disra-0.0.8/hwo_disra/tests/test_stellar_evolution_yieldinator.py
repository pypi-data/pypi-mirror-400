
from hwo_disra.Resolvinator import Resolvinator, SimpleSource
from hwo_disra.yields.StellarEvolution import StellarEvolutionYieldinator
import astropy.units as u


def test_stellar_evolution_yieldinator():
    sources = Resolvinator.random_sources_around(SimpleSource(0, 0), 2, 10)
    stellar_evo = StellarEvolutionYieldinator(sources)

    separations = [0.1, 0.2, 0.5, 0.75, 1.0]
    counts = []
    for sep in separations:
        counts.append(stellar_evo.yieldinator(sep * u.deg))

    assert counts[::-1] == sorted(counts)