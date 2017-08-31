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

    def draw(self, ax, color="black", alpha=1, marker=None):
        if marker:
            marker = "."
        l = lines.Line2D((self.p.x, self.q.x), (self.p.y, self.q.y), color=color, ms=12, lw=2,
                         marker=marker, alpha=alpha)
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

    def closest_point(self, p):
        """Return the point on the segment that is closest to p, and the distance to it"""
        a, b = P.solve(self.dir, self.dir.perp(), p - self.p)
        if 0 < a < 1:
            return self.p + self.dir * a, self.dir.norm() * abs(b)
        p_dist, q_dist = p.dist(self.p), p.dist(self.q)
        if p_dist < q_dist:
            return self.p, p_dist
        else:
            return self.q, q_dist

    def intersect_with_circle(self, center_point, radius):
        """Intersection of segment object with circle. Returns a segment holding either the two
        points intersecting the circle, the point intersecting and the endpoint contained within
        the circle, or None (if no intersection exists)"""

        # First find the closest point on the line.
        # work in the frame of reference where self.p is zero
        segment_direction = self.dir
        segment_norm = segment_direction.norm()
        perp = segment_direction.perp()

        # solve the equation a*segment_direction+b*perp=center_point-self.p, where a and b are
        # the coefficients of the vectors we are looking for. segment_direction and perp are
        # perpendicular and so represent a basis in which we can define a linear combination of
        # them to get center_point-self.p.
        a, b = P.solve(segment_direction, perp, center_point - self.p)
        height = abs(b) * segment_norm  # the height of the triangle created by the intersection
        #  points and the center_point

        if height > radius:
            # no intersections
            return None
        base_size = np.sqrt(radius * radius - height * height) / segment_norm # base_size is normalized
        # to the size of segment_direction

        # locations of intersections on the vector segment_direction
        left = a - base_size
        right = a + base_size
        if right < 0 or left > 1:
            # entire segment is outside of the circle
            return None

        # Return segment in absolute frame of reference, max and min used for cases where there
        # is only one intersection
        return S(self.p + segment_direction * max(0, left), self.p + segment_direction * min(1, right))

    # Checks if self separates p from all points
    def separates(self, p, points):
        sign = self.dir.perp() * (p - self.p) > 0
        for q in points:
            if sign == (self.dir.perp() * (q - self.p) > 0):
                return False
        return True


#######################################################################
