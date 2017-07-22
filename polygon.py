from misc import *
from point import P
from segment import S
from circle import Circle
from rectangle import Rectangle


class Polygon:

    @staticmethod
    def counter_clockwise(points):
        middle = sum(points, P(0, 0)) * (1/len(points))
        points.sort(key=lambda p: (p-middle).angle())

    def __init__(self, points):
        Polygon.counter_clockwise(points)
        self.points = points
        self.segments = [S(points[len(points)-1], points[0])]
        for i in range(len(points)-1):
            self.segments.append(S(points[i], points[i+1]))
        self.bounding = Rectangle.bounding(points)

    def __repr__(self):
        return str(self.points)

    @staticmethod
    def tilted_rectangle(p, size1, size2, angle):
        sq = [p]
        size = size1
        for i in range(3):
            p += P.polar(size, angle)
            sq.append(p)
            angle -= np.pi / 2
            if size == size1:
                size = size2
            else:
                size = size1

        return Polygon(sq)

    @staticmethod
    def square(p, size, angle):
        sq = [p]
        for i in range(3):
            p = p + P.polar(size, angle)
            sq.append(p)
            angle += np.pi / 2
        return Polygon(sq)


    @staticmethod
    def rectangle(corner, len_x, len_y):
        ps = [corner,
              corner + P(0, len_y),
              corner + P(len_x, len_y),
              corner + P(len_x, 0)]
        return Polygon(ps)

    def intersects(self, other):
        if not self.bounding.intersects(other.bounding):
            return False
        # If they don't then there is some segment of some polygon where all points of one are on one side
        # of it, and all points of the other on on the other side.
        for s in self.segments:
            for p in self.points:
                if p != s.p and p != s.q:
                    break
            if s.separates(p, other.points):
                return False
        for s in other.segments:
            for p in other.points:
                if p != s.p and p != s.q:
                    break
            if s.separates(p, self.points):
                return False
        return True

    # Checks if p is in the polygon. Works only for convex polygons, ordered counter clockwise.
    def contains(self, p):
        if not self.bounding.contains(p):
            return False
        for s in self.segments:
            if s.dir.perp() * (p-s.p) < 0:
                return False
        return True

    def rotate(self, center, angle):
        ps = [center + (p - center).rotate(angle) for p in self.points]
        return Polygon(ps)

    def shift(self, offset):
        ps = [p + offset for p in self.points]
        return Polygon(ps)

    # Super primitive.. not correct for most shapes...
    def center(self):
        s = P(0,0)
        for p in self.points:
            s += p
        s *= (1/len(self.points))
        return s

    def circumference(self):
        return sum((s.length() for s in self.segments))

    def draw(self, ax, color="red"):
        poly = patches.Polygon([p.to_tuple() for p in self.points], lw=0, fc=color)
        ax.add_patch(poly)
        return [poly]


