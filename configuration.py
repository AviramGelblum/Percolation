
from misc import *
from path import MotionPath
from point import P
from polygon_set import PolygonSet
from polygon import Polygon
from circle import Circle


class Configuration:

    def __init__(self, base_dir="data", file_name=None, seed=None, num_stones=0):
        self.base_dir = base_dir
        self.file_name = file_name
        max_y = 1
        min_y = 0
        self.stones = PolygonSet()
        self.path = None
        if self.file_name:
            trajectory_file_name = self.base_dir + "/" + file_name + "_load_trajectory.txt"
            stones_file_name = self.base_dir + "/" + file_name + ".txt"
            m = 0.0
            raw_stone_values = []
            try:
                with open(stones_file_name, 'r') as f:
                    for line in f:
                        new_values = [float(x) for x in line.split()]
                        raw_stone_values.append(new_values)
                        m = max(m, max(new_values))
            except IOError:
                print("Warning: stones file not found: ", stones_file_name)

            raw_path_values = []
            try:
                with open(trajectory_file_name, 'r') as f:
                    for line in f:
                        new_values = [float(x) for x in line.split()]
                        raw_path_values.append(new_values)
                        m = max(m, max(new_values))
            except IOError:
                print("Warning: trajectoy file not found: ", trajectory_file_name)

            if raw_stone_values:
                for raw_stone in raw_stone_values:
                    stone = Polygon([P(x / m, y / m) for x, y in pairs(raw_stone)])
                    self.stones.add(stone, allow_intersecting=True)
                max_y = max(p.y for stone in self.stones for p in stone.points)
                min_y = min(p.y for stone in self.stones for p in stone.points)

            if raw_path_values:
                path = [P(x / m, y / m) for x, y in raw_path_values]
                self.path = MotionPath(path)

        if self.stones.polys:
            self.stone_size = self.stones.polys[-1].segments[0].length()
            self.cheerio_radius = self.stone_size / 0.7
        else:
            real_boardy = 64
            real_boardx = 48
            self.cheerio_radius = 1 / real_boardy
            self.stone_size = self.cheerio_radius * 0.7

        if not file_name:
            self.seed = init_rand(seed)
            self.stones.random_squares(num_stones, self.stone_size)

        if not self.path:
            mid_y = (max_y + min_y) / 2
            self.path = MotionPath([P(0, mid_y), P(1, mid_y)])
        self.start = self.path.points[0]
        temp = self.path.points[-1]
        self.nest = self.start + (temp - self.start) * 2
        self.num_stones = len(self.stones.polys)

        dy = self.cheerio_radius/2
        border1 = Polygon.rectangle(P(-1, min_y - 2*dy), 2, dy)
        border2 = Polygon.rectangle(P(-1, max_y + dy), 2, dy)
        self.stones.add(border1, True)
        self.stones.add(border2, True)

    def __str__(self):
        if self.file_name:
            f = "F=" + self.file_name
        else:
            f = "S=" + str(self.seed)
        return '[{},{}]'.format(f, self.num_stones)

    def draw(self, ax, color):
        for stone in self.stones:
            for s in stone.segments:
                poly = Polygon.tilted_rectangle(s.p, (s.q - s.p).norm(), self.cheerio_radius,
                                                (s.q - s.p).angle())
                circle = Circle(s.p, self.cheerio_radius)
                poly.draw(ax, "lightgrey")
                circle.draw(ax, "lightgrey")
        for stone in self.stones:
            stone.draw(ax, "red")
        if self.path:
            self.path.draw(ax, "blue")
        ax.text(0, 1.01, str(self))
        return []
