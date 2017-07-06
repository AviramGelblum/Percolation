"""
Percolation is a simulation/analysis combined program made in order to check different theories on
the motion of a group of collectively carrying ants within a maze of cubes.
"""

from misc import *
from heat_map import HeatMap
from tests import *
from path import MotionPath
from movie import Movie
from configuration import Configuration
from run import *
from plots import Plots


def run_movie(cfg: Configuration, runner: Runner, only_plot=False, only_save=False):
    """Create the video."""
    movie = Movie()
    movie.background([(cfg, "black")])  # draws the cubes
    cheerios, result = Run(runner).run()  # runs the algorithm/analysis specified by runner
    print(result)
    if only_plot or only_save:
        movie.background([(MotionPath(cheerios), "green")])  # draws the cheerio path
        if only_save:
            movie.save_figure(cfg.file_name + "_image")
        else:
            movie.just_draw()  # plotting only the cubes
    else:
        # plotting the load trajectory within the cube maze
        to_draw = []
        for cheerio in cheerios:
            to_draw.append([(Circle(cheerio, cfg.cheerio_radius), "green")])
        movie.run_animation(to_draw, 0)



def run_two(cfg: Configuration):
    print(cfg)
    movie = Movie()
    draw_cfg(movie, cfg)
    cheerios, result = run(cfg)
    cfg.rolling = False
    cheerios2, result = run(cfg)
    to_draw = [[(Circle(cheerio, cfg.cheerio_radius), "green"),
                (Circle(cheerio2, cfg.cheerio_radius), "blue")]
               for cheerio, cheerio2 in zip(cheerios, cheerios2)]
    movie.run_animation(to_draw, 0)
    exit(0)


def just_draw_cfg(cfg: Configuration):
    print(cfg)
    movie = Movie()
    movie.background([(cfg, "black")])
    movie.just_draw()
    exit(0)

def experiment(cfg: Configuration, times, randomize_stones):
    count = 0
    count_ok = 0
    total_time = 0
    total_path_length = 0
    while count < times:
        if randomize_stones:
            cfg.rerandom_stones()
        cfg.reset_runseed(None)
        cheerios, result = run(cfg, verbose=False)
        if result != -1:
            count += 1
            if result > 0:
                count_ok += 1
                total_time += result
            else:
                total_time += cfg.max_frames
            total_path_length += MotionPath(cheerios).length()
    avg_time = int(total_time / times)
    success_percent = int(count_ok * 100.0 / times)
    avg_length = int(1000 * total_path_length / times)
    ants_length = int(1000 * cfg.path.length())
    print("{}  finished = {}%  time={}   antslength={}  length={}".format(
        cfg, success_percent, avg_time, ants_length, avg_length))


def many_experiments(times):
    lines = []
    for num_stones in range(50, 750, 50):
        for i in range(11):
            sigma_fresh = sigma_stuck = i * 0.05
            lines.append(experiment(sigma_fresh, sigma_stuck, times, num_stones))
    for l in lines:
        print(','.join(map(str, l)))


def create_heat_map(times, file_name, uniquely=False):
    stones, cheerio, nest, path = init_stones(file_name)
    print("Ants:", path.length())
    h = HeatMap()
    sum = 0
    for i in range(times):
        cheerios, result = run(cheerio, nest, stones, max_frames, verbose=False)
        sum += MotionPath(cheerios).length()
        h.add_to_map(cheerios, uniquely)
        if i % 100 == 0 and i:
            print(i)
    print("Simulation:", sum / times)
    if not file_name:
        file_name = "tmp"
    h.save_map("data/" + file_name + "_heatmap.txt")


def read_heat_map(file_name, display=True):
    stones, cheerio, nest, path = init_stones(file_name)
    movie = Movie()
    movie.background([(s, "green") for s in stones])
    h = HeatMap()
    if not file_name:
        file_name = "tmp"
    h.read_map("data/" + file_name + "_heatmap.txt")
    movie.background(h.to_draw())
    movie.background([(path, "red")])
    movie.save_figure("data/" + file_name + "_heatmap")
    if display:
        movie.just_draw()
    else:
        movie.close()


#####################################################################

def box_density(cfg, box):
    return cfg.stones.box_density(cfg.cheerio_radius, box)


def boxes(cfg, box_size_in_cheerio_radiuses=6, draw=True):
    if draw:
        movie = Movie()
        movie.background([(cfg, "black")])
    size = box_size_in_cheerio_radiuses * cfg.cheerio_radius

    index = 0
    path = cfg.path.points
    result = []
    while index < len(path) and path[index].x < 1 - size:
        p = path[index]
        box = Rectangle(p.x, p.y - size / 2, p.x + size, p.y + size / 2)

        good = 0
        times = 10
        for i in range(times):
            cfg.start = p
            cfg.reset_runseed()
            r, sim_res = Run(SimulationRunner(cfg), containing_box=box).run()
            if sim_res:
                good += 1
            if draw:
                if sim_res:
                    color = "green"
                else:
                    color = "black"
                movie.background([(MotionPath(r), color)])

        r, ant_res = Run(AntRunner(cfg, index), containing_box=box).run()
        if draw:
            if ant_res:
                color = "green"
            else:
                color = "black"
            movie.background([(MotionPath(r), "blue")])
            box.add_text('{:.0f}%,{:.0f}%'.format(box_density(cfg, box) * 100, good / times * 100))
            movie.background([(box, color)])

        result.append((box_density(cfg, box), ant_res, good / times))
        while index < len(path) and path[index].x < box.qx:
            index += 1

    if draw:
        movie.save_figure(cfg.file_name + "_boxes")
        movie.close()
        # movie.just_draw()
    return result


def boxes_stats(cfg, box_size_in_cheerio_radiuses=6):
    size = box_size_in_cheerio_radiuses * cfg.cheerio_radius
    index = 0
    path = cfg.path.points
    result = []
    while index < len(path) and path[index].x < 1 - size:
        p = path[index]
        box = Rectangle(p.x, p.y - size / 2, p.x + size, p.y + size / 2)
        r, ant_res = Run(AntRunner(cfg, index), containing_box=box).run()
        result.append((box_density(cfg, box), ant_res, MotionPath(r).length()))
        while index < len(path) and path[index].x < box.qx:
            index += 1
    return result


######################################################################

def all_boxes(size, dots=5):
    good = np.zeros(dots + 1)
    count = np.zeros(dots + 1)
    lengths = np.zeros(dots + 1)
    for file_name in all_file_names():
        cfg = Configuration(file_name=file_name)
        for density, res, length in boxes_stats(cfg, size):
            index = density * dots
            length /= size * cfg.cheerio_radius
            add_at_fractional_index(count, index, 1)
            if res:
                add_at_fractional_index(good, index, 1)
                add_at_fractional_index(lengths, index, length)
    return good / count, lengths / good


def plot_boxes():
    plots = Plots()
    dots = 5
    for size in range(2, 11, 2):
        x = np.linspace(0, 1, dots + 1)
        y = all_boxes(size, dots)
        plots.add_plot(x, y, str(size))
    plt.legend()
    plots.show()
    exit(0)


def plot_boxes2():
    plots = Plots()
    dots = 5
    res = None
    for size in range(2, 11, 1):
        dummy, r = all_boxes(size, dots)
        if res is None:
            res = r
        else:
            res = np.vstack((res, r))
    res = res.transpose()
    print(res)
    x = np.arange(2, 11, 1)
    for i in range(dots + 1):
        plots.add_plot(x, res[i], str(round(i * 0.2, 1)))

    plots.show()
    exit(0)


####################################################################


def where_did_it_go(cfg: Configuration, movie, index):
    path = cfg.path.points
    cheerio = path[index]
    box_size = cfg.cheerio_radius * 6
    safety_distance = cfg.cheerio_radius * 3 + cfg.stone_size
    startx = cheerio.x + safety_distance
    box1 = Rectangle(startx, cheerio.y - box_size, startx + box_size, cheerio.y)
    box2 = Rectangle(startx, cheerio.y, startx + box_size, cheerio.y + box_size)

    while index < len(path) and path[index].x < cheerio.x + cfg.cheerio_radius:
        index += 1
    if index == len(path):
        return "done"
    if abs(path[index].y - cheerio.y) < cfg.cheerio_radius / 8:
        return "skip"
    density1 = box_density(cfg, box1)
    density2 = box_density(cfg, box2)
    if abs(density1 - density2) < 0.1:
        return "skip"

    if movie:
        if density1 > density2:
            color1 = "red"
            color2 = "blue"
        else:
            color1 = "blue"
            color2 = "red"
        movie.background([(box1, color1), (box2, color2),
                          (Circle(cheerio, cfg.cheerio_radius / 3), "green")])

    return (density1 > density2) == (path[index].y > cheerio.y)




def remote_sensing1(cfg: Configuration, draw=False):
    if draw:
        movie = Movie()
        movie.background([(cfg, "black")])
    else:
        movie = None
    path = cfg.path.points
    index = 0
    last = 0
    count = 0
    count_good = 0
    while index < len(path):
        if path[index].x - path[last].x > cfg.cheerio_radius * 6:
            res = where_did_it_go(cfg, movie, index)
            if isinstance(res, bool):
                count += 1
                if res:
                    count_good += 1
            last = index
        index += 1
    if draw:
        movie.just_draw()
    print(cfg.file_name, count, count_good)
    return count, count_good

def remote_sensing():
    count = 0
    count_good = 0
    for file_name in all_file_names():
        cfg = Configuration(file_name=file_name)
        count1, count_good1 = remote_sensing1(cfg)
        count += count1
        count_good += count_good1
    print(count, count_good, count_good/count)
    exit(0)

########################################################################


def max_backwards(path):
    xs = [p.x for p in path]
    min_val, min_place = xs[-1], -1
    max_gap = 0
    a, b = None, None
    for i in range(len(xs) - 2, -1, -1):
        if xs[i] < min_val:
            min_val, min_place = xs[i], i
        gap = xs[i] - min_val
        if gap >= max_gap:
            max_gap = gap
            a, b = i, min_place
    return max_gap, a, b


def all_gaps():
    for file_name in all_file_names():
        cfg = Configuration(file_name=file_name)
        gap, a, b = max_backwards(cfg.path.points)
        print(file_name, gap/cfg.cheerio_radius)
    exit(0)


def draw_gap(file_name):
    cfg = Configuration(file_name=file_name)
    gap, a, b = max_backwards(cfg.path.points)
    path = cfg.path.points
    movie = Movie()
    movie.background([(cfg, "black")])
    movie.background([(Circle(path[a], cfg.cheerio_radius / 2), "green")])
    movie.background([(Circle(path[b], cfg.cheerio_radius / 2), "green")])
    movie.just_draw()
    exit(0)


########################################################################


f1 = "1410003"
f2 = "1380012"
f3 = "1260001"
f4 = "1110006"
f5 = "1110004"
f10 = "1350003"
f11 = "1400008"

# Difficult f10 f2 f1
#check_open_directions_for_circle_avoiding_segment()
#check_problem()

#cfg = Configuration(file_name=f11)
#runner = DeterministicRunner(cfg)
#run_movie(cfg, runner)
#exit(0)


for file in all_file_names():
    print(file)
    cfg = Configuration(file_name=file)
    runner = DeterministicRunner(cfg)
    run_movie(cfg, runner, only_save=True)

exit(0)




# for file_name in all_file_names():
#     cfg = Configuration(file_name=file_name)
#     boxes(cfg, 6, draw=True)
# exit(0)

# cfg = Configuration(num_stones=200)

# size = 10
# good = np.zeros(size + 1)
# count = np.zeros(size + 1)
# for file_name in all_file_names():
#     cfg = Configuration(file_name=file_name)
#     for res, fullness in boxes(cfg, draw=False):
#         index = int(fullness * size)
#         count[index] += 1
#         if res:
#             good[index] += 1
# print(count)
# hist = good / count
# print(hist)
# exit(0)

# run_movie(cfg)
# run_two(cfg)
#
# for file_name in all_file_names():
#     cfg = Configuration(file_name=file_name)
#     experiment(cfg, 10, False)
#     cfg.rolling = False
#     experiment(cfg, 10, False)
# exit(0)
#
# for i in range(100, 550, 50):
#     cfg = Configuration(num_stones=i, rolling=True)
#     experiment(cfg, 25, True)
#     cfg = Configuration(num_stones=i, rolling=False)
#     experiment(cfg, 25, True)
#     print()
# exit(0)
#
# file_name = None
# print(file_name)
# create_heat_map(10, file_name)
# read_heat_map(file_name)
