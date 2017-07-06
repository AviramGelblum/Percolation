from misc import *
from movie import Movie
from point import P
from segment import S
from circle import Circle
from circle_set import CircleSet
from polygon_set import PolygonSet
from polygon import Polygon
from general_region import GRegion
from configuration import Configuration


def check_circle_set(movie):
    to_draw = []

    m = Circle(P(0.5, 0.5), 0.2)
    to_draw.append((m, "black"))

    s = CircleSet(0.1)
    for i in range(3):
        c = Circle(P.random(), 0.1)
        s.add(c, c)
        to_draw.append((c, "yellow"))

    for c in s.intersecting(m):
        print(c)
        to_draw.append((c, "red"))

    movie.background(to_draw)
    movie.just_draw()


def check_circle_set2(movie):
    gran = 0.09
    to_draw = []

    s = CircleSet(gran)
    c = Circle(P(0.5, 0.5), 0.3)
    s.add(c, c)
    to_draw.append((c, "red"))

    for i in range(50):
        for j in range(50):
            p = P(i * gran, j * gran)
            if s.intersecting(Circle(p, 0.001)):
                to_draw.append((p, "black"))
            else:
                to_draw.append((p, "gold"))

    movie.background(to_draw)
    movie.just_draw()


def check_open_directions_for_point():
    placements = []
    for i in range(1000):
        stones = PolygonSet()
        stones.add(Polygon.square(P.polar(0.3, i / 1000 * 2 * np.pi) + P(0.3, 0.40), 0.2, 0.2))
        directions = stones.open_directions_for_point(P(0.5, 0.5), 0.4)
        placements.append([(s, "red") for s in stones] + [(directions, "green")])

    movie.run_animation(placements, 10)
    exit()


def check_open_directions_for_point2():
    stones = PolygonSet()
    stones.add(Polygon.square(P(0.6, 0.2), 0.2, 0))
    directions = stones.open_directions_for_point(P(0.5, 0.5), 0.4)
    movie.background([(s, "red") for s in stones] + [(directions, "green")])
    movie.just_draw()
    exit()


def check_segment_stuff2():
    s = S(P(0.3, 0.5), P(0.7, 0.4))
    radius = 0.2
    movie.background([(s, "black")])
    placements = []
    for i in range(5000):
        center = P.polar(i / 10000, i / 1000 * 2 * np.pi) + P(0.5, 0.5)
        current = [(Circle(center, radius), "red")]
        intersect = s.intersect_with_circle(center, radius)
        closest, dist = s.closest_point(center)
        if intersect:
            current.append((intersect, "yellow"))
        current.append((closest, "green"))

        if dist < radius and not intersect:
            print("WHAT??")

        placements.append(current)

    movie.run_animation(placements, 10)
    exit()


def check_segment_stuff():
    s = S(P(0.30000000000000004, 0.8000000000000002), P(0.3, 0.3))
    center = P(0.2987672191724942, 0.8145637895291986)
    radius = 0.014705882352941176
    closest, dist = s.closest_point(center)
    if dist >= radius:
        print("Shouldn't")
    s2 = s.intersect_with_circle(center, radius)
    if not s2:
        print("Got it")

    s = S(P(0.3, 0.8), P(0.3, 0.3))
    s2 = s.intersect_with_circle(center, radius)
    if not s2:
        print("Got it??")

    exit(1)


def draw_distribution(sigma):
    direction = P(0.3, 0)
    stones = PolygonSet()
    stones.add(Polygon.square(P(0.6, 0.6), 0.2, 0.1))
    stones.add(Polygon.square(P(0.3, 0.6), 0.2, 0.1))
    stones.add(Polygon.square(P(0.7, 0.4), 0.2, 0.1))
    cheerio = P(0.5, 0.5)
    g = stones.open_direction_for_circle(cheerio, 0, 1)

    movie = Movie()
    movie.background([(s, "red") for s in stones])
    movie.background([(S(cheerio, direction + cheerio), "blue")])
    movie.background([(g, "black")])

    points = []
    for i in range(300):
        rand_dir = g.rand_point_normal(direction, sigma)
        # rand_dir = direction.rotate(np.random.normal(scale=sigma) * np.pi)
        points.append(cheerio + rand_dir)
    movie.background([(Circle(p, 0.0015), "blue") for p in points])

    movie.just_draw()
    exit()


def check_open_directions_for_circle_avoiding_point():
    placements = []
    radius = 0.2
    step = 0.15
    center = P(0.55, 0.5)
    circ = Circle(center, radius)
    for i in range(1000):
        p = P.polar(0.35, i / 1000 * 2 * np.pi) + P(0.4, 0.40)
        dirs = GRegion.open_directions_for_circle_avoiding_point(circ, p, step)
        directions = GRegion(center=circ.center)
        if dirs:
            directions.intersect_with(dirs)
        placements.append([(Circle(center, step), "green"),
                           (Circle(p, radius), "lightgrey"),
                           (directions, "black")
                           ])

    movie = Movie()
    movie.run_animation(placements, 10)
    exit()


def check_open_directions_for_circle_avoiding_segment():
    placements = []
    radius = 0.25
    step = 0.15
    center = P(0.5, 0.5)
    circ = Circle(center, radius)
    m = 0
    for i in range(10000):
        p = P.polar(0.35, i / 1000 * 2 * np.pi) + P(0.5, 0.5)
        q = p + P.polar(0.2, i / 314 * 2 * np.pi)
        seg = S(p, q)
        directions = GRegion.open_directions_for_circle_avoiding_segment(circ, seg, step)
        shift = seg.dir.perp().resize(radius)
        box = Polygon([p - shift, p + shift, q + shift, q - shift])
        l = [(Circle(center, step), "lightgreen"),
             (box, "lightgrey"),
             (Circle(p, radius), "lightgrey"),
             (Circle(q, radius), "lightgrey"),
             (directions, "black"),
             (seg, "red"),
             (Circle(center, 0.004), "red")]
        pp, dist = seg.closest_point(center)
        if dist >= radius:
            for r in directions.regions:
                for t in r:
                    cut = seg.intersect_with_circle(center + t.resize(step), radius)
                    if cut and cut.length() > 0.00000001:
                        l += [(Circle(center + t.resize(step), radius), "pink")]
                        m = max(m, cut.length())
                        print(m)
        placements.append(l)

    movie = Movie()
    movie.run_animation(placements, 10)
    exit()


def check_open_directions_for_circle_avoiding_segment3():
    placements = []
    radius = 0.25
    step = 0.15
    center = P(0.5, 0.5)
    circ = Circle(center, radius)
    for i in range(1000):
        p = P.polar(0.37, i / 1000 * 2 * np.pi) + P(0.43, 0.38)
        q = p + P(0.1, 0.2)
        seg = S(p, q)
        directions = GRegion.open_directions_for_circle_avoiding_segment(circ, seg, step)
        if len(directions.regions) > 1:
            shift = seg.dir.perp().resize(radius)
            print(seg.p.x, seg.p.y, seg.q.x, seg.q.y)
            box = Polygon([p - shift, p + shift, q + shift, q - shift])
            l = [(Circle(center, step), "lightgreen"),
                 (box, "lightgrey"),
                 (Circle(p, radius), "lightgrey"),
                 (Circle(q, radius), "lightgrey"),
                 (directions, "black"),
                 (seg, "red"),
                 (Circle(center, 0.004), "red")]
            placements.append(l)
            movie = Movie()
            movie.background(l)
            movie.just_draw()
            break
    exit(0)


def check_open_directions_for_circle_avoiding_segment2():
    radius = 0.25
    step = 0.15
    center = P(0.5, 0.5)
    circ = Circle(center, radius)
    p = P(0.12661771955, 0.59179988647)
    q = P(0.22661771955, 0.79179988647)

    seg = S(p, q)
    directions = GRegion.open_directions_for_circle_avoiding_segment(circ, seg, step)
    shift = seg.dir.perp().resize(radius)
    box = Polygon([p - shift, p + shift, q + shift, q - shift])
    l = [(Circle(center, step), "lightgreen"),
         (box, "lightgrey"),
         # (Circle(p, radius), "lightgrey"),
         # (Circle(q, radius), "lightgrey"),
         (directions, "black"),
         (seg, "red"),
         (Circle(center, 0.004), "red")]
    movie = Movie()
    movie.background(l)
    movie.just_draw()
    exit(0)


def check_problem():
    movie = Movie()
    f = 1

    def aff(x, y):
        return P(x, y)

    stone = Polygon([
        aff(0.09897029702970297, 0.27443716679360247),
        aff(0.11047372429550648, 0.2750952018278751),
        aff(0.10981568926123382, 0.2865955826351866),
        aff(0.09831530845392232, 0.285940594059406)
    ])
    center = aff(0.08183068719268435, 0.28569424117242365)
    radius = 0.0164719687883 * f
    step = 0.000823598439415 * f

    stones = PolygonSet()
    stones.add(stone)
    allowable = stones.open_direction_for_circle(center, radius, step)

    l = [(stone, "red"), (Circle(center, radius), "green"), (allowable, "black")]

    movie.background(l)
    movie.just_draw()
    exit(0)
