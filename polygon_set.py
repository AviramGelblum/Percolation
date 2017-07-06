from misc import *
from point import P
from polygon import Polygon
from region import Region
from general_region import GRegion
from circle import Circle
from segment import S
from circle_set import CircleSet
from rectangle import Rectangle


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

    def random_squares(self, num, size):
        while len(self.polys) < num:
            self.add(Polygon.square(P(misc.rand(), misc.rand()), size, rand() * np.pi / 2))

    def contains(self, p):
        return any(poly.contains(p) for poly in self.polys)

    def _relevant_segments(self, point, dist):
        box = Rectangle.bounding_circle(Circle(point, dist))
        for poly in self.polys:
            if poly.bounding.intersects(box):
                for s in poly.segments:
                    # note that the polygon itself is always on the counter-clockwise direction of s.dir
                    # We have to only consider this side.
                    #if  s.dir.alt_angle(point - s.p) >= 2:
                    yield s

    # a circle wanting to take a step
    def open_direction_for_circle(self, center, radius, step):
        allowable = GRegion(center=center)
        for s in self._relevant_segments(center, radius + step):
            allowable.intersect(
                GRegion.open_directions_for_circle_avoiding_segment(
                    Circle(center, radius), s, step))
        return allowable


    def box_density(self, radius, box: Rectangle):
        bigger_box = Rectangle(box.px - radius, box.py - radius, box.qx + radius, box.qy + radius)
        my_polys = PolygonSet()
        for s in self.polys:
            for p in s.points:
                if bigger_box.contains(p):
                    my_polys.add(s, allow_intersecting=True)
        times = 2000
        bad = 0
        for i in range(times):
            p = box.rand_point()
            if my_polys.intersect_with_circle(p, radius):
                bad += 1
        return bad / times
