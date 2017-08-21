import matplotlib.patches as patches
from point import P
import misc


# p = upper left corner,
# q = lower right corner
class Rectangle:
    def __init__(self, px, py, qx, qy):
        if not (px < qx and py < qy):
            print("Problem in rectangle")
            exit(1)
        self.px, self.py = px, py
        self.qx, self.qy = qx, qy
        self.text = None

    def add_text(self, text):
        self.text = text

    def __iter__(self):
        yield P(self.px, self.py)
        yield P(self.px, self.qy)
        yield P(self.qx, self.qy)
        yield P(self.qx, self.py)

    @staticmethod
    def bounding(points):
        return Rectangle(min(p.x for p in points), min(p.y for p in points),
                         max(p.x for p in points), max(p.y for p in points))

    @staticmethod
    def bounding_circle(c):
        return Rectangle(c.center.x - c.radius, c.center.y - c.radius,
                         c.center.x + c.radius, c.center.y + c.radius)

    def contains(self, p):
        return self.px <= p.x <= self.qx and self.py <= p.y <= self.qy

    def intersects(self, other):
        return not (self.px > other.qx or other.px > self.qx or
                    self.py > other.qy or other.py > self.qy)

    def rand_point(self):
        x = self.px + misc.rand() * (self.qx - self.px)
        y = self.py + misc.rand() * (self.qy - self.py)
        return P(x, y)

    def __repr__(self):
        return "BOX[{},{},{},{}]".format(self.px, self.py, self.qx, self.qy)

    def draw(self, ax, color="black"):
        rect = patches.Polygon([p.to_tuple() for p in self], lw=2, fill=False, color=color, fc=color)
        ax.add_patch(rect)
        if self.text:
            ax.text(self.px, self.qy + 0.01, self.text)
        return [rect]

    def __eq__(self, other):
        return self.px == other.px and \
            self.py == other.py and \
            self.qx == other.qx and \
            self.qy == other.qy
