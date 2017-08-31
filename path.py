import misc
from typing import List
from point import P
from segment import S
from polygon import Polygon
from polygon_set import PolygonSet


class MotionPath:

    def __init__(self, points: List[P]):
        self.points = points

    def last(self) -> P:
        return self.points[-1]

    def to_segment_list(self):
        segments = []
        last = None
        for p in self.points:
            if last:
                segments.append(S(last, p))
            last = p
        return segments

    def from_segment_list(self, segments):
        self.points = []
        for s in segments:
            self.points.append(s.p)
            self.points.append(s.q)

    def random_step(self, stones: PolygonSet, step_size: float, bias: P):
        last = self.last()
        directions = stones.open_directions_for_point(last, step_size)
        if not directions:
            print("walk stuck")
            exit(1)
        if misc.rand() < 0.5:
            random_directions = [directions.rand_point(step_size) for i in range(2)]
            direction = bias.resize(step_size).closest_point(random_directions)
        else:
            direction = directions.rand_point(step_size)
        self.points.append(last + direction)

    def length(self, gran=0.001):
        if not self.points:
            return 0
        sump = 0
        last = self.points[0]
        for p in self.points:
            d = p.dist(last)
            if d > gran:
                sump += d
                last = p
        return sump

    def simplify(self, stones: PolygonSet):
        stack = []
        for p in self.points:
            stack.append(p)
            while len(stack) >= 3:
                p3, p2, p1 = stack.pop(), stack.pop(), stack.pop()
                if stones.intersects(Polygon([p1, p2, p3])):
                    stack += [p1, p2, p3]
                    break
                else:
                    stack += [p1, p3]
        self.points = stack

    def remove_cycles(self):
        segments = self.to_segment_list()
        new_segments = segments[0:2]
        for i in range(2, len(segments)):
            current = segments[i]
            truncate = False
            for j in range(len(new_segments)-1):
                checked = new_segments[j]
                if current.intersects(checked):
                    middle = current.intersection(checked)
                    new_segments[j] = S(checked.p, middle)
                    del new_segments[j+1:]
                    new_segments.append(S(middle, current.q))
                    truncate = True
                    break
            if not truncate:
                new_segments.append(current)
        self.from_segment_list(new_segments)

    def draw(self, ax, kwargsdict=None):
        if kwargsdict is None:
            kwargsdict = {'color': 'green', 'alpha': 1}
        res = []
        for s in self.to_segment_list():
            res += s.draw(ax, **kwargsdict)
        return res
