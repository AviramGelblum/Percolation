from misc import *
from point import P
from segment import S

#############################################################################
# Describes the region between two rays.
# second one is counter-clockwise from the first


class Region:
    def __init__(self, p1=None, p2=None):
        try:
            self.p1 = p1.copy()
            self.p2 = p2.copy()
        except AttributeError:
            self.p1 = None
            self.p2 = None

    def __bool__(self):
        if not self.p1:
            return False
        else:
            return True

    def __iter__(self):
        yield self.p1
        yield self.p2

    def __str__(self):
        return "{" +  str(self.p1) +  str(self.p2) + "}"

    def copy(self):
        return Region(self.p1, self.p2)

    @remember
    def alt_angle(self):
        return self.p1.alt_angle(self.p2)

    @remember
    def angle(self):
        return self.p1.angle_with(self.p2)

    def contains(self, p):
        return self.p1.alt_angle(p) <= self.alt_angle()

    # can actually return two regions.
    def intersect(self, other):
        other_angle1 = self.p1.alt_angle(other.p1)
        other_angle2 = self.p1.alt_angle(other.p2)
        res = []
        if other_angle1 <= other_angle2:
            if self.alt_angle() <= other_angle1:
                res = []
            elif self.alt_angle() >= other_angle2:
                res = [other.copy()]
            else:
                res = [Region(other.p1, self.p2)]
        else:
            if self.alt_angle() <= other_angle2:
                res = [self.copy()]
            elif self.alt_angle() > other_angle1:
                if self.p1 == other.p2:
                    res = [Region(other.p1, self.p2)]
                elif other.p1 == self.p2:
                    res = [Region(self.p1, other.p2)]
                else:
                    res = [Region(self.p1, other.p2), Region(other.p1, self.p2)]
            else:
                res = [Region(self.p1, other.p2)]
        return res

    def draw(self, ax, center=P.zero(), color="black", size=0.5):
        a1 = S(center, center + self.p1.resize(size)).draw_arrow(ax, color)
        a2 = S(center, center + self.p2.resize(size)).draw_arrow(ax, color)
        a3 = patches.Arc((center.x, center.y), size, size, 0, self.p1.angle_degrees(), self.p2.angle_degrees(),color=color)
        ax.add_patch(a3)
        return a1 + a2 + [a3]

    def point_at_angle(self, angle, size=1.0):
        return P.polar(size, self.p1.angle() + angle)

    def rand_point(self, size):
        return self.point_at_angle(rand() * self.angle(), size)



