"""
General Region - holds a union of regions, starts as the whole space and
is slowly intersected."""

import misc
import scipy.stats as sct
import math
import numpy as np
from point import P
from segment import S
from circle import Circle
from region import Region


class GRegion:

    def __init__(self, center=P(0, 0), size=0.5):
        self.regions = []  # list of region objects
        self.full = True   # This property is used to differentiate everything allowed (True) from
        # nothing allowed (False)
        self.center = center
        self.size = size

    def __bool__(self):
        # true if any regions are allowed
        return self.full or not not self.regions

    def width(self):
        """Compute total angle of all regions"""
        total = 0
        for r in self.regions:
            total += r.angle()
        return total

    def contains(self, v):
        """Determine whether direction v is contained within the GRegion angle set"""
        if self.full:
            return True
        return any(r.contains(v) for r in self.regions)

    def intersect_with(self, region: Region):
        """Intersect the Region set in the GRegion object with another Region"""
        if self.full:
            self.full = False
            self.regions = [region]
        else:
            res = []
            for r in self.regions:
                res.extend(r.intersect(region))
            self.regions = res  # list of Regions

    def intersect(self, other):
        """Intersect the GRegion object with another GRegion object."""
        if other.full:
            return
        for r in other.regions:
            self.intersect_with(r)

    def align_with_closest_side(self, v):
        """
        Find closest angle in GRegion object to the direction of v (Point object - defines a
        vector).
        """
        if self.full:
            return v
        if not self.regions:
            return P.zero()
        sides = [p for r in self.regions for p in r]  # List of points describing all angular
        # edges of regions in GRegion
        cos = [side.cos(v) for side in sides]
        maxcos = max(cos)
        closest = sides[cos.index(maxcos)]  # take the maximal cosine between the velocity
        # direction and the region edges - that is the closest edge.
        return closest.resize(v.norm())  # resize to speed magnitude (returns velocity direction)

    def draw(self, ax, color="black"):
        # Draw all Regions in black
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
        """
        Generate a random vector within the allowable region.
        :param size: norm of the vector to be generated
        :return:  a random vector within the allowable regions (class P)
        """
        if self.full:
            # if all motion is allowed, generate a completely random vector
            return P(misc.rand()-0.5, misc.rand()-0.5).resize(size)

        # else, generate a vector within the allowable regions

        # Draw a random angle within the accumulated allowed
        # regions total angle
        t = misc.rand() * self.width()
        total = 0

        # Find in which region this randomly generated angle falls
        for r in self.regions:
            total += r.angle()
            if total >= t:
                res = r.rand_point(size)  # Generate a random vector of norm=size within the
                # randomly chosen region
                return res
        print("Apparently stuck", self.width())
        exit(1)

    def rand_point_normal(self, direction, sigma):
        """
        Choose a random angle from a normal distribution with mean direction and standard
        deviation sigma. Rotate input direction by this angle, unless it is too large (above
        100). if so, draw a completely random direction. Note that since the normal distribution
        is not defined on an angular variable, the actual pdf we use is not truly normally
        distributed around the 0-direction (but it is close enough for our purposes).
        """
        def cdf(x_var):  # shorthand function for cumulative distribution function with SD=sigma
            return sct.norm.cdf(x_var, scale=sigma)

        def ppf(x_var):  # shorthand function for inverse of the cumulative distribution function
            # with SD=sigma
            return sct.norm.ppf(x_var, scale=sigma)

        intervals = []
        if self.full:
            # Truncating normal distribution cdf to fit angular variable
            intervals += [(cdf(-math.pi), cdf(math.pi))]
        else:

            for r in self.regions:
                # Rotating region sides to be centered around direction
                a1 = r.p1.rotate(-(direction.angle())).angle()
                a2 = r.p2.rotate(-(direction.angle())).angle()

                # Make sure interval boundaries are set up correctly
                if r.contains(-direction):
                    intervals += [(cdf(a1), cdf(math.pi))]
                    intervals += [(cdf(-math.pi), cdf(a2))]
                else:
                    intervals += [(cdf(a1), cdf(a2))]

        # Accumulate allowed cdf(angle) in all intervals to randomly draw from
        total = 0
        for x, y in intervals:
            total += y - x
        t = misc.rand() * total

        # Go over all intervals and translate random number t into the actual corresponding angle
        # in the accumulated cdf intervals
        for x, y in intervals:
            if t <= y - x:
                angle = ppf(x+t)  # translate from x+t=cdf(angle) back to angle
                # if angle change is too large, choose random direction, else, rotate by this
                # angle.
                if angle > 100:
                    return self.rand_point(direction.norm())
                return direction.rotate(angle)
            t -= y - x
        exit(1)

    @staticmethod
    def open_directions_for_circle_avoiding_point(circ: Circle, p: P, step) -> Region:
        """
        Handle the case where the load is near the edge of the segment. In this case the
        parent method (open_directions_for_avoiding_segment) does not compute the correct
        allowable region.
        """

        radius = circ.radius
        center = circ.center
        a = center.dist(p)
        if a > step + radius:
            # Case where the motion is fully allowed.
            return Region()
        if a < radius:
            # Case where the point is already within the load radius. i.e. numerical error or bug
            direction = center - p  # away from point
            return Region(-direction.perp(), direction.perp())  # half plane perpendicular to
            # direction  - defines allowed open region for further motion

            # x = (radius ** 2 - step ** 2 - a ** 2) / (2 * a)
            # if x < 0:
            #     print("wow")
            #     return None
            # y = np.sqrt(step ** 2 - x ** 2)
            # direction = (center - p).resize(a + x)
            # perp = direction.perp().resize(y)
            # return Region(direction - perp - p, direction + perp - p)

        # if a>radius and a<radius+step
        # first find the maximal step size for which the region limit grows.
        # Above this step size, the limit in the open direction stays the same as the load just
        # slides next to the edge.
        d = np.sqrt(a ** 2 - radius ** 2)
        if d < step:
            step = d


        # Using the perpendicular of the triangle connecting a, the radius and the line of size
        # step connecting the circle to the edge, we cut a into two parts x and y such that
        # r^2-y^2=step^2-x^2 -> b=r^2-step^2=y^2-x^2
        # We then use this equation as well as a=x+y
        # to get the size of the final vector in the direction of a (x) and its size in the
        # perpendicular direction (h) as a function of the known quantities (radius,step and a).
        b = radius ** 2 - step ** 2
        x = (a ** 2 - b) / (2 * a)
        if x >= step:
            return Region()
        h = np.sqrt(step ** 2 - x ** 2)
        direction = (p - center).resize(x)
        left = direction + direction.perp().resize(h)
        right = direction - direction.perp().resize(h)
        return Region(left, right)

    @staticmethod
    def open_directions_for_circle_avoiding_segment(circ: Circle, seg: S, step):
        """
        Find which motion directions are allowed for a circle (simulating load) which is near
        a segment (an edge of a cube).
        """
        center = circ.center
        radius = circ.radius
        closest, dist = seg.closest_point(center)
        open_region = GRegion(center=center)

        if dist <= radius:
            # segment is inside load radius
            direction = center - closest  # away from obstacle
            r = Region(-direction.perp(), direction.perp())  # half plane perpendicular to
            # direction  - defines allowed open region for further motion
            open_region.intersect_with(r)
        else:
            # segment is outside load radius - we want to check if there can be an intersection
            # between load and the cube segment if the load moves with speed "step" towards the
            # segment, and restrict possible direction of motions accordingly.
            shift = seg.dir.perp().resize(radius)  # Shift in the direction toward the segment
            for sign in -1, 1:
                # Check for which shift there is an intersection with the load
                seg2 = S(seg.q + shift * sign, seg.p + shift * sign)
                cut = seg2.intersect_with_circle(center, step)  # Returns intersected segment
                # with a circle of radius step if one exists, to determine the maximal angle the
                # load can move without encroaching on the segment.
                if cut:
                    v1, v2 = cut.p - center, cut.q - center
                    x = v1.alt_angle(v2)
                    # This is a little strange but needed....
                    if x < 0.00000000001 or x > 3.9999999999:
                        # case where the cut segment is almost a point within the load,
                        # accept this inaccuracy and move on (?), allow motion
                        continue
                    # Determine if open region is from v2 to v1 or the other way. Regions are
                    # defined from the first argument to the second argument counterclockwise.
                    if x <= 2:
                        r = Region(v2, v1)  # r is the allowed open region. v2 is further
                        # counterclockwise compared to v1
                    else:
                        r = Region(v1, v2)  # r is the allowed open region. v1 is further
                        # counterclockwise compared to v2
                    open_region.intersect_with(r)  # add to original fully open GRegion

            for p in seg:
                # Making sure the load avoids the endpoints of the segment (segment avoidance
                # calculation does not hold, another method is needed).
                r = GRegion.open_directions_for_circle_avoiding_point(circ, p, step)
                if r:
                    # pass
                    open_region.intersect_with(r)

        return open_region

