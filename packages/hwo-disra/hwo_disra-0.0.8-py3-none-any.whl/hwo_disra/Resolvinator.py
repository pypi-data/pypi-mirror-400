
from dataclasses import dataclass
from typing import Collection, Protocol, Set, TypeVar, Generic
import numpy as np
import astropy.coordinates.angles.utils as utils

class Source(Protocol):
    @property
    def ra(self) -> float: return 0
    @property
    def dec(self) -> float: return 0
    def separation(self, other: 'Source') -> float:
        raise NotImplementedError()

T = TypeVar('T', bound=Source)

@dataclass(eq=True, frozen=True)
class SimpleSource:
    ra: float
    dec: float
    def separation(self, other: 'SimpleSource') -> float:
        return np.degrees(utils.angular_separation(np.radians(self.ra), np.radians(self.dec),
                                                   np.radians(other.ra), np.radians(other.dec)))


class Resolvinator(Generic[T]):
    def __init__(self, catalog: Collection[T]) -> None:
        """
        A catalog $C$ of source objects which each have an RA/Dec coordinate defining it's position.

        The distance measure used in nearest_source is given by distance_function.
        """
        self.catalog = set(catalog)

        # all (s1, dist, s2) in self.distance :
        #     dist = angular_separation(s1, s2) and
        #     all source in C - {s1} :
        #         angular_separation(s1, s2) <= angular_separation(s1, source)
        # Currently this is a naive implementation that is O(n^2)
        # Tested using scipy distances computations and it doesn't save
        # much time for 1000 sources.  We estimate our catalogs will be "100's"
        # so this should be fine.
        self.distances = sorted([(source, *self.compute_nearest_source(source))
                                  for source in catalog],
                                key = lambda s: s[1])

    def resolved_by(self, angle: float) -> Set[T]:
        """
        all s1 in resolved_by(angle) :
            all s2 in C - {s1} : angular_separation(s1, s2) > angle

        Return a set of sources that are resolved by the given angle.

        A source is considered resolved if its angular distance to the nearest source is greater than the given angle.

        Parameters
        ----------
        angle : float
            The angle in degrees to check against.

        Returns
        -------
        resolved : set[T]
            The set of sources that are resolved by the given angle.
        """
        resolved = set()
        for (source, distance, _) in self.distances:
            if distance > angle:
                resolved.add(source)
        return resolved

    def lookup_nearest_source(self, source: T) -> tuple[float, T | None]:
        """
        Return the tuple (distance, nearest_source) for the given source.
        """
        for (s, distance, nearest_source) in self.distances:
            if s == source:
                return distance, nearest_source
        return float('inf'), None

    def compute_nearest_source(self, source: T) -> tuple[float, T | None]:
        """
        distance, s2 = compute_nearest_source(s1) =>
            all s3 in C - {s1, s2} :
                distance <= angular_distance(s1, s3)

        Find the nearest source in the catalog to the given source.

        Parameters
        ----------
        source : Source
            The source to find the nearest source to.

        Returns
        -------
        distance : Angle
            The angular distance in degrees to the nearest source.
        nearest_source : Source | None
            The nearest source in the catalog. If the input source has no nearest source in the catalog, this is None.
        """
        min_distance = float('inf')
        nearest_source = None
        for s in self.catalog:
            if s == source:
                continue
            distance = source.separation(s)
            if distance < min_distance:
                min_distance = distance
                nearest_source = s
        return min_distance, nearest_source

    @staticmethod
    def random_sources_around(center: T, radius: float, size: int) -> list[SimpleSource]:
        """
        Generate a list of random SimpleSource objects within a given radius of a given point.

        Parameters
        ----------
        center : Source
            The central source.
        radius : float
            The radius in degrees.
        size : int
            The number of sources to generate.

        Returns
        -------
        sources : list[SimpleSource]
            A list of random SimpleSource objects within the given radius of the given point.
        """
        sources = []
        for _ in range(size):
            ra_offset = np.random.uniform(-radius, radius)
            dec_offset = np.random.uniform(-radius, radius)
            sources.append(SimpleSource(ra=center.ra + ra_offset,
                                        dec=center.dec + dec_offset))
        return sources
