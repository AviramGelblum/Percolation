
# # will random walk until target dist is achieved.
# def random_walks_from_path(start, num_ants, target, target_radius, remember_radius):
#     ants = [start] * num_ants
#     ant_memory = [None] * num_ants
#     ant_v_norm = 0.02
#     bias = 1
#     while True:
#         current_draw = []
#         for i in range(num_ants):
#             if not ant_memory[i] and ants[i].dist(target) <= remember_radius:
#                 ant_memory[i] = ants[i]
#             if ants[i].dist(target) <= target_radius:
#                 return ants[i]
#
#             open = stones.open_directions_for_point(ants[i], ant_v_norm * 1.1)
#             if rand() < bias:
#                 rs = [open.rand_point(ant_v_norm) for j in range(3)]
#                 dir = target - ants[i]
#                 coss = [dir.cos(r) for r in rs]
#                 j = coss.index(max(coss))
#                 step = rs[j]
#             else:
#                 step = open.rand_point(ant_v_norm)
#             ants[i] += step


# will random walk until target dist is achieved.
# For the winning ant, we take the last time it was at pull_dist_factor * target_dist,
# and that is where we pull to.
from misc import *
from general_region import GRegion

def random_walks_from_cheerio(start, num_ants, target_dist):
    full = GRegion()
    ants = [ start + full.rand_point(cheerio_radius) for i in range(num_ants) ]
    paths = [[]] * num_ants
    bias_direction = nest
    ant_v_norm = 0.004
    bias = 1
    while True:
        for i in range(num_ants):
            if start.dist(ants[i]) >= target_dist:
                paths[i].append(ants[i])
                return paths[i]
            if rand() < 0.3:
                paths[i].append(ants[i])
            open = stones.open_directions_for_point(ants[i], ant_v_norm * 1.1)
            if rand() < bias:
                rs = [open.rand_point(ant_v_norm) for j in range(5)]
                dir = bias_direction - ants[i]
                coss = [dir.cos(r) for r in rs]
                j = coss.index(max(coss))
                step = rs[j]
            else:
                step = open.rand_point(ant_v_norm)
            ants[i] += step


def run_old(cheerio, num_frames):
    placements = []
    pull = nest
    path = None
    v = P(0,0)
    for i in range(num_frames):
        if i % (num_frames / 10) == 0:
            print("Finished ", i / num_frames * 100, " percent")
        if cheerio.y < 0:
            print("Yey!")
            break

        allowable = stones.open_direction_for_circle(cheerio, cheerio_radius, maxSpeed)
        if not allowable:
            print("Stuck!")
            break

        #if not pull or rand() < 0.01 or cheerio.dist(pull) < cheerio_radius/2:
        #    path = random_walks_from_cheerio(cheerio, 4, cheerio_radius * 5)
        #    pull = path[-1]


        to_draw = [(Circle(cheerio, cheerio_radius), "green")]
        # (Circle(pull, cheerio_radius / 5), "black")]
        #for i in range(len(path)-1):
        #    to_draw.append((S(path[i], path[i+1]), "purple"))
        placements.append(to_draw)


        # Turns out that the following is more important than it seems,
        # It gives a kind of persistence. If we didn't add to the current v, we would be stuck
        # more easily, as in:     v = (pull - cheerio).resize(maxSpeed)
        v += (pull - cheerio).resize(maxSpeed/4)
        v = v.resize(maxSpeed)

        if not allowable.contains(v):
            v = allowable.align_with_closest_side(v)

        cheerio = cheerio + v

    return placements




def run2(cheerio, num_frames):
    placements = []
    pull = nest
    distances_from_nest = []
    v = P(0,0)
    for i in range(num_frames):
        if i % (num_frames / 10) == 0:
            print("Finished ", i / num_frames * 100, " percent")
        if cheerio.y < 0:
            print("Yey!")
            break
        allowable = stones.open_direction_for_circle(cheerio, cheerio_radius, maxSpeed)
        if not allowable:
            print("Stuck!")
            break
        to_draw = [(Circle(cheerio, cheerio_radius), "green")]
        if pull:
            to_draw.append((Circle(cheerio + (pull-cheerio).resize(4 * cheerio_radius), cheerio_radius/10), "black"))
        placements.append(to_draw)

        distances_from_nest.append(cheerio.dist(nest))
        if rand() < 0.02:
            if len(distances_from_nest) > 50 and \
                                    distances_from_nest[-50] - distances_from_nest[-1] <= 0:
                angle = min(rand(), rand())
                if rand() < 0.5:
                    angle = -angle
                pull = (nest-cheerio).rotate(angle * np.pi) + cheerio
            else:
                pull = nest

        v += (pull - cheerio).resize(maxSpeed/5)
        v = v.resize(maxSpeed)

        if not allowable.contains(v):
            v = allowable.align_with_closest_side(v)

        cheerio = cheerio + v

    return placements


def triangulation_stuff:
    points = np.array([p.to_tuple() for s in stones for p in s.points])
    tri = points[Delaunay(points).simplices]
    tri = [[P.A(p) for p in t] for t in tri]

    lines = []
    for t in tri:
        lines += [S(t[0], t[1]), S(t[1], t[2]), S(t[2], t[0])]

    movie.background([(l, "black") for l in lines])
    movie.just_draw()



def run(cheerio, num_frames):
    placements = []
    pull = nest
    v = nest.resize(max_speed)
    stuck = False
    for i in range(num_frames):
        if i % (num_frames / 10) == 0:
            print("Finished ", i / num_frames * 100, " percent")
        if cheerio.y < 0:
            print("Yey!")
            break
        allowable = stones.open_direction_for_circle(cheerio, cheerio_radius, max_speed)
        if not allowable:
            print("Stuck!")
            break
        placements.append(to_draw(cheerio, v, pull))

        if stuck:
            #pull = random_pull(cheerio, 0.3)
            pull = ant_pull(cheerio)
        elif rand() < max_speed / persistence_distance:
            pull = random_pull(cheerio, 0.1)

        v += (pull - cheerio).resize(max_speed / 5)
        v = v.resize(max_speed)

        stuck = False
        if not allowable.contains(v):
            v2 = allowable.align_with_closest_side(v)
            if v2.cos(v) <= 0:
                stuck = True
            v = v2

        cheerio = cheerio + v

    return placements




def run(cheerio, num_frames):
    placements = []
    pull = nest
    path = Path([])
    v = nest.resize(cheerio_speed)
    for i in range(num_frames):
        if i % (num_frames / 10) == 0:
            print("Finished ", i / num_frames * 100, " percent")
        if cheerio.y < 0:
            print("Yey!")
            break
        allowable = stones.open_direction_for_circle(cheerio, cheerio_radius, cheerio_speed)
        if not allowable:
            print("Stuck!")
            break

        if cheerio.dist(pull) < cheerio_radius or rand() < cheerio_speed / persistence_distance:
            pull, path = ant_pull(cheerio, cheerio_radius * 10, 10)

        placements.append(to_draw(cheerio, v, path, pull))

        v += (pull - cheerio).resize(cheerio_speed / 5)
        v = v.resize(cheerio_speed)

        if not allowable.contains(v):
            v = allowable.align_with_closest_side(v)

        cheerio = cheerio + v

    return placements



# def ant_pull(cheerio, target_distance, num_ants):
#     paths = [Path([cheerio])] * num_ants
#     found_path = None
#     while not found_path:
#         for path in paths:
#             if nest.dist(path.last()) < nest.dist(cheerio) - target_distance:
#                 found_path = path
#                 break
#             path.random_step(stones, ant_speed, nest - cheerio)
#     found_path.simplify(stones)
#     found_path.remove_cycles()
#     furthest = nest.furthest_point(found_path.path)
#     if furthest == cheerio:
#         furthest = found_path.path[1]
#     return furthest, found_path


def paths(times, file_name=None, save_to_file=None, display=True):
    stones, cheerio, nest = init_stones(file_name)
    movie = Movie()
    movie.background([(s, "red") for s in stones])
    for i in range(times):
        cheerios, result = run(cheerio, nest, stones, max_frames, verbose=False)
        movie.background([(Path(cheerios), random_color())])
    if save_to_file:
        movie.save_figure(save_to_file)
    if display:
        movie.just_draw()
    exit()
