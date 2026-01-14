import time
from hypothesis import given
from hypothesis.strategies import sets, floats, tuples
import pytest
from hwo_disra.Resolvinator import Resolvinator
from hwo_disra.Resolvinator import SimpleSource

# Custom strategies
ra_strategy = floats(allow_nan=False, allow_infinity=False, min_value=-360, max_value=360)
dec_strategy = floats(allow_nan=False, allow_infinity=False, min_value=-90, max_value=90)
source_tuple_strategy = tuples(ra_strategy, dec_strategy)
catalog_strategy = sets(source_tuple_strategy, min_size=1)
catalog_min2_strategy = sets(source_tuple_strategy, min_size=2)

@given(catalog=catalog_strategy)
def test_resolvinator_constructor(catalog):
    sources = [SimpleSource(ra, dec) for ra, dec in catalog]
    resolvinator = Resolvinator(sources)
    # Check that the catalog is assigned to a field
    assert hasattr(resolvinator, 'catalog')
    assert resolvinator.catalog == set(sources)
    # Check that the dictionary is computed correctly
    for source in sources:
        distance, nearest_source = resolvinator.lookup_nearest_source(source)
        if nearest_source is None:
            continue
        assert nearest_source in sources
        assert nearest_source != source
        assert distance == min(source.separation(s) for s in sources if s != source)

@given(catalog=catalog_min2_strategy,
       angle=floats(allow_nan=False, allow_infinity=False))
def test_resolvinator_resolved_by(catalog, angle):
    sources = [SimpleSource(ra, dec) for ra, dec in catalog]
    resolvinator = Resolvinator(sources)
    resolved = resolvinator.resolved_by(angle)
    assert resolved == {source for source in sources if resolvinator.compute_nearest_source(source)[0] > angle}

@given(catalog=catalog_min2_strategy)
def test_resolvinator_nearest_source(catalog):
    sources = [SimpleSource(ra, dec) for ra, dec in catalog]
    resolvinator = Resolvinator(sources)
    for source in sources:
        nearest_distance, nearest_source = resolvinator.compute_nearest_source(source)
        if nearest_source is not None:
            assert nearest_source in sources
            assert nearest_source != source
            assert nearest_distance == min(source.separation(s) for s in sources if s != source)

@given(ra1=ra_strategy, dec1=dec_strategy, ra2=ra_strategy, dec2=dec_strategy)
def test_angular_separation(ra1, dec1, ra2, dec2):
    source1 = SimpleSource(ra1, dec1)
    source2 = SimpleSource(ra2, dec2)
    separation = source1.separation(source2)
    assert separation >= 0
    assert source1.separation(source1) == pytest.approx(0, abs=1e-6)
    assert source1.separation(source2) == pytest.approx(source2.separation(source1), abs=1e-6)

def test_larger_catalog():
    """
    Generate a 1000 source catalog and test resolved_by with different angles.
    Each call to resolved_by should be timed, print a report at the end.
    """
    angles = [x for x in [1, 2.5, 5, 7.5]]
    start = time.time()
    sources = Resolvinator.random_sources_around(SimpleSource(0, 0), 100, 1000)
    end = time.time()
    print(f"Generating {len(sources)} sources took {end-start:.2f} s")
    start = time.time()
    resolvinator = Resolvinator(sources)
    end = time.time()
    print(f"Creating Resolvinator took {end-start:.2f} s")
    results = []
    for angle in angles:
        start = time.time()
        resolved = resolvinator.resolved_by(angle)
        end = time.time()
        results.append((angle, end-start, len(resolved)))
    print("Results:")
    print("Angle\tTime (s)\tNumber of sources")
    for angle, time_taken, num_sources in results:
        print(f"{angle}\t{time_taken:.2f}\t{num_sources}")
