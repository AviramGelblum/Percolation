"""
Percolation is a simulation/analysis combined program made in order to check different theories on
the motion of a group of collectively carrying ants within a maze of cubes.
"""

import misc
from heat_map import HeatMap
# from tests import *
from path import MotionPath
from movie import Movie
import configuration
import run
import circle
import rectangle
import BoxAnalysis
import numpy as np
from plots import Plots


def run_movie(cfg: configuration.Configuration, runner: run.Runner, only_plot=False,
              only_save=False, repeat=True):
    """Create the video."""
    movie = Movie()
    movie.background([(cfg, None)])  # draws the cubes, their shade and the experimental path if
    # there is one
    cheerios, result = run.Run(runner).run()  # runs the algorithm/analysis specified by runner
    # returns a list of points (class p) specifying the location of the load over time and a
    # boolean variable describing whether the run was successful
    print(result)
    if only_plot or only_save:
        movie.background([(MotionPath(cheerios), {'color': 'green'})])
        # draws the simulated load path
        if only_save:
            movie.save_figure(cfg.file_name + "_image")
        else:
            movie.just_draw()  # plotting without saving
    else:
        # Creating a video of the simulated load moving through the cube maze
        # to_draw = []
        # # create list of tuples(Circle,str), one for each frame to be drawn in the animation
        # for cheerio in cheerios:
        #     to_draw.append([(circle.Circle(cheerio, cfg.cheerio_radius), {'color': 'green'})])
        to_draw = [[(circle.Circle(cheerio[1], cfg.cheerio_radius), {'color': 'green'}),
                    cheerio[0]] for
                   cheerio in enumerate(cheerios)]
        movie.run_animation(to_draw, 0, repeat=repeat)  # drawing the load


def run_two(cfg: configuration.Configuration):
    print(cfg)
    movie = Movie()
    draw_cfg(movie, cfg)
    cheerios, result = run(cfg)
    cfg.rolling = False
    cheerios2, result = run(cfg)
    to_draw = [[(circle.Circle(cheerio, cfg.cheerio_radius), "green"),
                (circle.Circle(cheerio2, cfg.cheerio_radius), "blue")]
               for cheerio, cheerio2 in zip(cheerios, cheerios2)]
    movie.run_animation(to_draw, 0)
    exit(0)


def just_draw_cfg(cfg: configuration.Configuration):
    print(cfg)
    movie = Movie()
    movie.background([(cfg, None)])
    movie.just_draw()
    exit(0)


def experiment(cfg: configuration.Configuration, times, randomize_stones):
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
    movie.background([(s, {'color': 'green'}) for s in stones])
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


def where_did_it_go(cfg: configuration.Configuration, movie, index):
    path = cfg.path.points
    cheerio = path[index]
    box_size = cfg.cheerio_radius * 6
    safety_distance = cfg.cheerio_radius * 3 + cfg.stone_size
    start_x = cheerio.x + safety_distance
    box1 = rectangle.Rectangle(start_x, cheerio.y - box_size, start_x + box_size, cheerio.y)
    box2 = rectangle.Rectangle(start_x, cheerio.y, start_x + box_size, cheerio.y + box_size)

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
                          (circle.Circle(cheerio, cfg.cheerio_radius / 3), "green")])

    return (density1 > density2) == (path[index].y > cheerio.y)


def remote_sensing1(cfg: configuration.Configuration, draw=False):
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
    for file_name in misc.all_file_names():
        cfg = configuration.Configuration(file_name=file_name)
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
    for file_name in misc.all_file_names():
        cfg = configuration.Configuration(file_name=file_name)
        gap, a, b = max_backwards(cfg.path.points)
        print(file_name, gap/cfg.cheerio_radius)
    exit(0)


def draw_gap(file_name):
    cfg = configuration.Configuration(file_name=file_name)
    gap, a, b = max_backwards(cfg.path.points)
    path = cfg.path.points
    movie = Movie()
    movie.background([(cfg, None)])
    movie.background([(circle.Circle(path[a], cfg.cheerio_radius / 2), {'color': 'green'})])
    movie.background([(circle.Circle(path[b], cfg.cheerio_radius / 2), {'color': 'green'})])
    movie.just_draw()
    exit(0)


########################################################################

if __name__ == '__main__':
    f1 = "1410003"
    f2 = "1380012"
    f3 = "1260001"
    f4 = "1110006"
    f5 = "1110004"
    f10 = "1350003"
    f11 = "1400008"


    # Difficult f10 f2 f1
    # check_open_directions_for_circle_avoiding_segment()
    # check_problem()

    # current_cfg = configuration.Configuration(file_name=f11)
    # current_runner = run.DeterministicRunner(current_cfg)
    # run_movie(current_cfg, current_runner)
    # exit(0)

    for file in misc.all_file_names():
        print(file)
        current_cfg = configuration.Configuration(file_name=file)
        current_runner = run.DeterministicRunner(current_cfg)
        run_movie(current_cfg, current_runner, only_save=True)

    exit(0)



    # for file_name in misc.all_file_names():
    #     current_cfg = configuration.Configuration(file_name=file_name)
    #     boxes(current_cfg, 6, draw=True)
    # exit(0)

    # current_cfg = configuration.Configuration(num_stones=200)

    # size = 10
    # good = np.zeros(size + 1)
    # count = np.zeros(size + 1)
    # for file_name in all_file_names():
    #     current_cfg = configuration.Configuration(file_name=file_name)
    #     for res, fullness in boxes(current_cfg, draw=False):
    #         index = int(fullness * size)
    #         count[index] += 1
    #         if res:
    #             good[index] += 1
    # print(count)
    # hist = good / count
    # print(hist)
    # exit(0)

    # run_movie(current_cfg)
    # run_two(current_cfg)
    #
    # for file_name in misc.all_file_names():
    #     current_cfg = configuration.Configuration(file_name=file_name)
    #     experiment(current_cfg, 10, False)
    #     current_cfg.rolling = False
    #     experiment(current_cfg, 10, False)
    # exit(0)
    #
    # for i in range(100, 550, 50):
    #     current_cfg = configuration.Configuration(num_stones=i, rolling=True)
    #     experiment(current_cfg, 25, True)
    #     current_cfg = configuration.Configuration(num_stones=i, rolling=False)
    #     experiment(current_cfg, 25, True)
    #     print()
    # exit(0)
    #
    # file_name = None
    # print(file_name)
    # create_heat_map(10, file_name)
    # read_heat_map(file_name)

