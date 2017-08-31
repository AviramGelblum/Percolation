import misc
import math
import numpy as np
import matplotlib.patches
###########################################################
# Points


class P:

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    @classmethod
    def A(cls, p):
        return cls(p[0], p[1])

    def copy(self):
        return P(self.x, self.y)

    @classmethod
    def random(cls):
        """class method/static method creating a random point."""
        return cls(misc.rand(), misc.rand())

    @classmethod
    def polar(cls, size, angle):
        """class method/static method creating point given polar coordinates (size,angle)."""
        return cls(size * np.cos(angle), size * np.sin(angle))

    def __add__(self, other):
        return P(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return P(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return P(-self.x, -self.y)

    def __mul__(self, other):
        try:
            return self.x * other.x + self.y * other.y
        except AttributeError:  # for the case where other is a constant
            return P(other * self.x, other * self.y)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_tuple(self):
        return self.x, self.y

    @classmethod
    @misc.remember
    def zero(cls):
        return P(0, 0)

    @misc.remember
    def perp(self):
        """Compute anticlockwise perpendicular vector."""
        return P(-self.y, self.x)

    def is_parallel(self, other):
        return self * other.perp() == 0

    def __repr__(self):
        #return '({:.0f},{:.0f})'.format(self.x * 1000,self.y * 1000)
        return '({},{})'.format(self.x, self.y)

    def to_grid(self, granularity):
        return P(math.floor(self.x / granularity), math.floor(self.y/granularity))

    @misc.remember
    def norm(self):
        return np.sqrt(self * self)

    def dist(self, other):
        return np.sqrt(self.dist_squared(other))

    def dist_squared(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    # returns a new vector with the new size.
    def resize(self, size):
        norm = self.norm()
        if norm == size:
            return self.copy()
        if norm == 0:
            return P(0, 0)
        return P(self.x * (size/norm), self.y * (size/norm))

    @misc.remember
    def angle(self):
        """calculate angle for the (x,y) vector.
        Generally just arctan2 with support for special cases.
        """
        if self.y == 0:
            if self.x > 0:
                return 0  # going in the x-direction
            else:
                return -np.pi  # = np.pi, going in the -x-direction
        return np.arctan2(self.y, self.x)

    @misc.remember
    def angle_degrees(self):
        return np.rad2deg(self.angle())

    def angle_with(self, other):
        """
        Calculate the clockwise angle between two vectors (vector 2 "other" - vector 1 "self").
        :param other: second vector
        :return: angle computed (int)
        """
        ang1 = self.angle()
        ang2 = other.angle()
        if ang2 >= ang1:
            return ang2 - ang1
        return 2 * np.pi + ang2 - ang1

    def cos(self, other):
        return self * other / (other.norm() * self.norm())

    # will return something that behaves like the counter-clockwise angle.
    # Just faster to calculate. It ranges from 0 to 4.
    def alt_angle(self, other):
        if self == other:
            return 0
        if self.perp() * other > 0:
            return 1 - self.cos(other)
        else:
            val = 3 + self.cos(other)
            return val

    def rotate(self, angle):
        """Rotate vector with angle=angle."""
        return P.polar(self.norm(), self.angle() + angle)

    @staticmethod
    def solve(p1, p2, q):
        """
        Solve the equation a*p1 + b*p2 = q. Returns the coefficients a and b for the vectors
        p1 and p2, so that q is decomposed in the p1 and p2 basis with these coefficients for the
        basis vectors.
        """
        if p1.is_parallel(p2):
            return None, None
        if abs(p1.x) > abs(p1.y):  # this has to do with accuracy
            b = (q.y*p1.x - q.x*p1.y) / (p2.y*p1.x - p2.x*p1.y)
            a = (q.x - b*p2.x) / p1.x
        else:
            b = (q.x * p1.y - q.y * p1.x) / (p2.x * p1.y - p2.y * p1.x)
            a = (q.y - b * p2.y) / p1.y
        return a, b

    def closest_point(self, points):
        return misc.most(points, lambda x: -self.dist(x))[0]

    def furthest_point(self, points):
        return misc.most(points, lambda x: self.dist(x))[0]

    def draw(self, ax, radius=0.001, color='black', alpha=1):
        c = matplotlib.patches.Circle((self.x, self.y), radius, lw=0, fc=color, alpha=alpha)
        ax.add_patch(c)
        return [c]


