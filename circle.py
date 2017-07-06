from misc import *
from point import P


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def intersects(self, other):
        return self.center.dist_squared(other.center) <= (self.radius + other.radius) ** 2

    def contains(self, p):
        return self.center.dist_squared(p) <= self.radius ** 2

    def draw(self, ax, color):
        return self.center.draw(ax, color, radius=self.radius)

    def __repr__(self):
        return "Circle(" +  str(self.center) + "," + str(self.radius) + ")"
