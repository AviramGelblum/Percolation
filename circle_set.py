from misc import *
from point import P

# Keeps a set of circles.
# purpose is a fast way to check which ones of many circles intersects a given one.
class CircleSet:

    def __init__(self, gran=0.02):
        self.table = {}
        self.gran = gran

    def _to_grid(self, x):
        return math.floor(x / self.gran)

    def add(self, circle, pointer):
        minx, miny, maxx, maxy = [self._to_grid(v) for v in circle.bounding_box()]
        # can be improved..
        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                t = self.table.get((i, j), None)
                if not t:
                    t = []
                    self.table[(i, j)] = t
                t.append((circle, pointer))

    def intersecting(self, c):
        res = []
        mapij = self.table.get((self._to_grid(c.center.x), self._to_grid(c.center.y)), [])
        for (c1, pointer) in mapij:
            if c.intersects(c1):
                res.append(pointer)
        return res
