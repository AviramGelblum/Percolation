import misc
from point import P
from polygon import Polygon
from region import Region
from general_region import GRegion
from circle import Circle
from segment import S
from circle_set import CircleSet
from rectangle import Rectangle
import numpy as np


class PolygonSet:

    def __init__(self):
        self.polys = []

    def __iter__(self):
        for p in self.polys:
            yield p

    def __getitem__(self, i):
        return self.polys[i]

    def intersects(self, poly: Polygon) -> bool:
        return any(poly2.intersects(poly) for poly2 in self.polys)

    def add(self, poly: Polygon, allow_intersecting=False):
        """Add polygon object to list of polygons."""
        if allow_intersecting or not self.intersects(poly):
            self.polys.append(poly)
            return True
        return False

    def intersect_with_circle(self, p, radius):
        for poly in self.polys:
            if poly.contains(p):
                return True
            for s in poly.segments:
                if s.intersect_with_circle(p, radius):
                    return True
        return False

    def random_squares(self, num, size, xy_lim):
        while len(self.polys) < num:
            self.add(Polygon.square(P(misc.rand()*xy_lim[0], misc.rand()*xy_lim[1]), size,
                                    misc.rand() * np.pi / 2))

    def contains(self, p):
        return any(poly.contains(p) for poly in self.polys)

    def _relevant_segments(self, point, dist):
        """
        Find which of all possible cube segments are relevant (increases efficiency
        dramatically).
        """
        box = Rectangle.bounding_circle(Circle(point, dist))  # Calculate the rectangle bounding
        # the circle (supposed to be called with dist=load_radius+step)

        # iterate over all cubes (polys in the configuration polygon_set)
        for poly in self:
            if poly.bounding.intersects(box):  # if rectangle bounding the cube (poly) intersects
                # with the rectangle bounding the load (circle) -> yield all of its segments

                for s in poly.segments:  # poly.segments - list
                    yield s

                    # note that the polygon itself is always on the counter-clockwise direction
                    # of s.dir We have to only consider this side. if  s.dir.alt_angle(point -
                    # s.p) >= 2:  # this was taken out because it is not that important in terms
                    # of efficiency

    def open_direction_for_circle(self, center, radius, step):
        """
        Given the stone configuration within the polygon_set object, calculate the allowed
        directions of motion for the next step of the load.
        """
        allowable = GRegion(center=center)  # empty general region
        for s in self._relevant_segments(center, radius + step):
            # iterate over all segments which have a chance to be close enough to the load so as
            # to pose a possible obstacle within the next step. Find the allowed motion given
            # each segment (and intersect all)
            allowable.intersect(
                GRegion.open_directions_for_circle_avoiding_segment(
                    Circle(center, radius), s, step))
        return allowable

    def box_density(self, radius, box: Rectangle):
        """ Calculate density of cubes within a box"""
        # Create a bigger box to include areas of enlarged cubes outside of the box (intersection
        # with the load body)
        bigger_box = Rectangle(box.px - radius, box.py - radius, box.qx + radius, box.qy + radius)
        my_polys = PolygonSet()
        for s in self.polys:
            for p in s.points:
                if bigger_box.contains(p):
                    my_polys.add(s, allow_intersecting=True)  # Add all cubes which have any
                    # intersection with the load inside the box
                    break
        # Simulate random points within the box to estimate the density
        times = 2000
        bad = 0
        for i in range(times):
            p = box.rand_point()
            if my_polys.intersect_with_circle(p, radius):
                bad += 1
        return bad / times
