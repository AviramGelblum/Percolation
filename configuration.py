
import misc
from path import MotionPath
from point import P
from polygon_set import PolygonSet
from polygon import Polygon
from circle import Circle

class Configuration:
    """
    Configuration class defines the basic data for a specific video, extracting the data from the
    .txt files. The following are defined: cube locations and actual path taken by the ants.
    Configuration possesses a draw() method used to draw these.
    """

    def __init__(self, base_dir="data", file_name=None, seed=None, num_stones=0, border=True):
        """
        Extract data from txt files and save in our defined classes.

        :param base_dir:  directory name within the root
        :param file_name: video number
        :param seed: seed - in case we are running a simulation on a random distribution of cubes
        :param num_stones: number of stones to be randomized in case of simulation on a random
        distribution
        """

        self.base_dir = base_dir  # root/base_dir - directory name
        self.file_name = file_name  # number of video

        # used for normalization of the data to the range 0-1
        # max_y = 1
        # min_y = 0
        self.y_range = [0, 1]

        self.stones = PolygonSet()  # PolygonSet object which will contain a list of polygons
        # corresponding to the cubes

        self.path = None  # placeholder for normalized trajectory data
        if self.file_name:  # if there is data (not random cube maze)
            trajectory_file_name = self.base_dir + "/" + file_name + "_load_trajectory.txt"
            stones_file_name = self.base_dir + "/" + file_name + ".txt"
            m = 0.0  # placeholder for max value in x or y
            raw_stone_values = []  # placeholder for extracted cube data
            try:
                with open(stones_file_name, 'r') as f:
                    for line in f:
                        # get cube data
                        new_values = [float(x) for x in line.split()]
                        raw_stone_values.append(new_values)
                        m = max(m, max(new_values))
            except IOError:
                print("Warning: stones file not found: ", stones_file_name)

            raw_path_values = []  # placeholder for extracted trajectory data
            try:
                with open(trajectory_file_name, 'r') as f:
                    for line in f:
                        # get trajectory data
                        new_values = [float(x) for x in line.split()]
                        raw_path_values.append(new_values)
                        m = max(m, max(new_values))
            except IOError:
                print("Warning: trajectoy file not found: ", trajectory_file_name)

            if raw_stone_values:
                for raw_stone in raw_stone_values:
                    # normalize cubes and put in Polygon objects
                    stone = Polygon([P(x / m, y / m) for x, y in misc.pairs(raw_stone)])
                    self.stones.add(stone, allow_intersecting=True)  # add to PolygonSet object
                self.y_range[1] = max(p.y for stone in self.stones for p in stone.points)
                self.y_range[0] = min(p.y for stone in self.stones for p in stone.points)

            if raw_path_values:
                # normalize path and put in a List object
                path = [P(x / m, y / m) for x, y in raw_path_values]
                self.path = MotionPath(path)  # define MotionPath Object from list

        # if cube data is taken from actual video, get sizes from data. Else, get sizes from
        # general data measurements.
        if self.stones.polys:
            self.stone_size = self.stones.polys[-1].segments[0].length()
            self.cheerio_radius = self.stone_size / 0.7
        else:
            real_boardx = 68  # Yoav used 64 for some reason
            real_boardy = 48
            self.cheerio_radius = 1 / real_boardx
            self.stone_size = self.cheerio_radius * 0.7

        # Randomized cube maze generation
        if not file_name:
            self.seed = misc.init_rand(seed)
            self.stones.random_squares(num_stones, self.stone_size, (1, real_boardy/real_boardx))
            self.y_range[1] = real_boardy/real_boardx

        # Fictitious initial path for nest direction and starting point - (0,midy) to (1,midy)
        if not self.path:
            mid_y = (sum(self.y_range)) / 2
            self.path = MotionPath([P(0, mid_y), P(1, mid_y)])
        self.start = self.path.points[0]  # Initial location of load - from data or (0,midy)
        temp = self.path.points[-1]
        self.nest = self.start + (temp - self.start) * 2  # Initial location of nest - from data or
        # (2,midy)
        self.num_stones = len(self.stones.polys)  # used for command-line printing

        # Create border polygon objects to prevent the simulated load from wandering too far.
        if border:
            dy = self.cheerio_radius/2
            border1 = Polygon.rectangle(P(-1, self.y_range[0] - 2*dy), 2, dy)
            border2 = Polygon.rectangle(P(-1, self.y_range[1] + dy), 2, dy)
            self.stones.add(border1, True)
            self.stones.add(border2, True)

    def __str__(self):
        if self.file_name:
            f = "F=" + self.file_name
        else:
            f = "S=" + str(self.seed)
        return '[{},{}]'.format(f, self.num_stones)

    def draw(self, ax, kwargsdict=None):
        """
        Method for drawing the cubes, highlighted areas around the cubes where the load center
        cannot go, and the actual trajectory path.
        This is a shell calling the actual drawing methods for the above objects.

        :param ax: axis object in which the drawables will be drawn
        :param kwargsdict: optional dictionary listing the colors of the different shapes to be
        drawn
        :return:
        """
        # color dictionaries unpacked
        default_keys = ['ShadeColor', 'CubeColor', 'PathColor', 'ShadeAlpha', 'CubeAlpha',
                        'PathAlpha']
        default_values = ['lightgrey', 'red', 'blue', 1, 1, 1]
        colordict = dict(zip(default_keys, default_values))
        if kwargsdict is not None:
            for key in kwargsdict.keys():
                colordict[key] = kwargsdict[key]

        ax.set_ylim(self.y_range[0] - 0.05, self.y_range[1] + 0.05)
        # Create areas where the load cannot go around the cube and draw them
        for stone in self.stones:
            for s in stone.segments:
                # For every segment of every cube, create a rectangle with the cube segment as
                # its first side, the rectangle faces away from the cube, and the other side size
                # is the same as the load size. This limits the load center when it is near the
                # segment.
                poly = Polygon.tilted_rectangle(s.p, (s.q - s.p).norm(), self.cheerio_radius,
                                                (s.q - s.p).angle())

                # However, this tilted rectangle is not enough, as it doesn't capture the
                # limitations on the load near the vertices of the cubes. For that we also
                # create a circle around each cube vertex.
                circle = Circle(s.p, self.cheerio_radius)

                # Draw both types of areas for each segment
                poly.draw(ax, **{'color': colordict['ShadeColor'], 'alpha': colordict[
                    'ShadeAlpha']})
                circle.draw(ax, {'color': colordict['ShadeColor'], 'alpha': colordict[
                    'ShadeAlpha']})
        # Draw cubes
        for stone in self.stones:
            stone.draw(ax, **{'color': colordict['CubeColor'],'alpha': colordict[
                    'CubeAlpha']})
        # Draw experimental load trajectory if one exists for the current run
        if self.path:
            self.path.draw(ax, {'color': colordict['PathColor'], 'alpha': colordict['PathAlpha']})
        ax.text(self.y_range[0] - 0.02, self.y_range[1] + 0.02, str(self))  # Add number of
        # video, seed and number of stones as text
        return []
