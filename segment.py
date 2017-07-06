from misc import *
from point import P

#############################################################
# segments


class S:
    def __init__(self, p, q):
        self.p = p
        self.q = q
        self.dir = q - p

    def __iter__(self):
        yield self.p
        yield self.q

    def __repr__(self):
        return '[{},{}]'.format(self.p, self.q)

    def length(self):
        return (self.p - self.q).norm()

    def rotate(self, angle):
        return S(self.p.rotate(angle), self.q.rotate(angle))

    def draw(self, ax, color="black", marker=None):
        if marker:
            marker = "."
        l = lines.Line2D((self.p.x, self.q.x), (self.p.y, self.q.y), color=color, ms=12,
                         marker=marker)
        ax.add_line(l)
        return [l]

    def draw_arrow(self, ax, color="black"):
        l = patches.FancyArrowPatch(self.p.to_tuple(), self.q.to_tuple(), color=color, arrowstyle="->",
                                    mutation_scale=10)
        ax.add_patch(l)
        return [l]

    # returns the a,b solution of:
    # self.p + a*(self.dir) = other.p + b*(self.dir)
    def intersection_params(self, other):
        a, neg_b = P.solve(self.dir, other.dir, other.p - self.p)
        if not a:
            return None, None
        return a, -neg_b

    def intersects(self, other):
        a, b = self.intersection_params(other)
        if not a:
            return False
        return 0 <= a <= 1 and 0 <= b <= 1

    def intersection(self, other):
        a, b = self.intersection_params(other)
        return self.p + self.dir * a

    # returns the point on the segment that is closest to p, and the distance to it.
    def closest_point(self, p):
        a, b = P.solve(self.dir, self.dir.perp(), p - self.p)
        if 0 < a < 1:
            return self.p + self.dir * a, self.dir.norm() * abs(b)
        p_dist, q_dist = p.dist(self.p), p.dist(self.q)
        if p_dist < q_dist:
            return self.p, p_dist
        else:
            return self.q, q_dist

    # returns a segment
    def intersect_with_circle(self, p, radius):
        # First Find the closest point on the line.
        dir = self.dir
        norm = dir.norm()
        perp = dir.perp()
        a, b = P.solve(dir, perp, p - self.p)
        height = abs(b) * norm
        if height > radius:
            return None
        base_size = np.sqrt(radius * radius - height * height) / norm
        left = a - base_size
        right = a + base_size
        if right < 0 or left > 1:
            return None
        return S(self.p + dir * max(0, left), self.p + dir * min(1, right))

    # Checks if self separates p from all points
    def separates(self, p, points):
        sign = self.dir.perp() * (p - self.p) > 0
        for q in points:
            if sign == (self.dir.perp() * (q - self.p) > 0):
                return False
        return True


#######################################################################
