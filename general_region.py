from misc import *
from point import P
from segment import S
from circle import Circle
from region import Region

################################################################################
# General Region - holds a union of regions, starts as the whole space and
# is slowly intersected.

class GRegion:
    def __init__(self, center=P(0, 0), size=0.5):
        self.regions = []
        self.full = True
        self.center = center
        self.size = size

    def is_empty(self):
        return not self.full and not self.regions

    def width(self):
        total = 0
        for r in self.regions:
            total += r.angle()
        return total

    def contains(self, v):
        if self.full:
            return True
        return any(r.contains(v) for r in self.regions)

    def intersect_with(self, region: Region):
        if self.full:
            self.full = False
            self.regions = [region]
        else:
            res = []
            for r in self.regions:
                res.extend(r.intersect(region))
            self.regions = res

    def intersect(self, other):
        if other.full:
            return
        for r in other.regions:
            self.intersect_with(r)

    def align_with_closest_side(self, v):
        if self.full:
            return v
        if not self.regions:
            return P.zero()
        sides = [p for r in self.regions for p in r]
        cos = [side.cos(v) for side in sides]
        maxcos = max(cos)
        closest = sides[cos.index(maxcos)]
        return closest.resize(v.norm())

    def draw(self, ax, color="black"):
        res = []
        if not self.full:
            for r in self.regions:
                res += r.draw(ax, self.center, color, self.size)
        return res

    def __str__(self):
        res = "<"
        for r in self.regions:
            res += r.__str__()
        res += ">"
        return res


    def rand_point(self, size):
        if self.full:
            return P(rand()-0.5, rand()-0.5).resize(size)
        t = rand() * self.width()
        total = 0
        for r in self.regions:
            total += r.angle()
            if total >= t:
                res = r.rand_point(size)
                return res
        print("Apparently stuck", self.width())
        exit(1)

    def rand_point_normal(self, direction, sigma):

        def cdf(x):
            return sct.norm.cdf(x, scale=sigma)

        def ppf(x): # the inverse
            return sct.norm.ppf(x, scale=sigma)

        intervals = []
        if self.full:
            intervals += [(cdf(-math.pi), cdf(math.pi))]
        else:
            for r in self.regions:
                a1 = r.p1.rotate(-(direction.angle())).angle()
                a2 = r.p2.rotate(-(direction.angle())).angle()
                if r.contains(-direction):
                    intervals += [(cdf(a1), cdf(math.pi))]
                    intervals += [(cdf(-math.pi), cdf(a2))]
                else:
                    intervals += [(cdf(a1), cdf(a2))]

        total = 0
        for x, y in intervals:
            total += y - x
        t = rand() * total
        for x, y in intervals:
            if t <= y - x:
                angle = ppf(x+t)
                if angle > 100:
                    return self.rand_point(direction.norm())
                return direction.rotate(angle)
            t -= y - x
        exit(1)

    @staticmethod
    def open_directions_for_circle_avoiding_point(circ: Circle, p: P, step) -> Region:
        radius = circ.radius
        center = circ.center
        a = center.dist(p)
        if a > step + radius:
            return None
        if a < radius:
            dir = center - p
            return Region(-dir.perp(), dir.perp())
            x = (radius ** 2 - step ** 2 - a ** 2) / (2 * a)
            if x < 0:
                print("wow")
                return None
            y = np.sqrt(step ** 2 - x ** 2)
            dir = (center - p).resize(a + x)
            perp = dir.perp().resize(y)
            return Region(dir - perp - p, dir + perp - p)

        # first find the optimal
        d = np.sqrt(a ** 2 - radius ** 2)
        if d < step:
            step = d

        b = radius ** 2 - step ** 2
        # now solve: x+y = a, y^2 - x^2 = b
        x = (a ** 2 - b) / (2 * a)
        if x >= step:
            return None
        h = np.sqrt(step ** 2 - x ** 2)
        dir = (p - center).resize(x)
        left = dir + dir.perp().resize(h)
        right = dir - dir.perp().resize(h)
        return Region(left, right)

    @staticmethod
    def open_directions_for_circle_avoiding_segment(circ: Circle, seg: S, step):
        center = circ.center
        radius = circ.radius
        closest, dist = seg.closest_point(center)
        open = GRegion(center=center)

        if dist <= radius:
            dir = center - closest
            r = Region(-dir.perp(), dir.perp())
            open.intersect_with(r)
        else:
            shift = seg.dir.perp().resize(radius)
            for sign in -1, 1:
                seg2 = S(seg.q + shift * sign, seg.p + shift * sign)
                cut = seg2.intersect_with_circle(center, step)
                if cut:
                    v1, v2 = cut.p - center, cut.q - center
                    x = v1.alt_angle(v2)
                    # This is a little strange but needed....
                    if x < 0.00000000001 or x > 3.9999999999:
                        continue
                    if x <= 2:
                        r = Region(v2, v1)
                    else:
                        r = Region(v1, v2)
                    open.intersect_with(r)

            for p in seg:
                r = GRegion.open_directions_for_circle_avoiding_point(circ, p, step)
                if r:
                    pass
                    open.intersect_with(r)

        return open

