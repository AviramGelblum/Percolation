import pickle
import configuration
import numpy as np
from point import P
from BoxAnalysis import BoxAnalysis, DistributionResults
import math
import misc


class TiledGridSimulation:
    def __init__(self, video_number, pickle_density_motion_file_name, tile_scale=1,
                 max_steps=10000):
        self.video_number = video_number
        self.cfg = configuration.Configuration(file_name=self.video_number, border=False)
        self.scale = tile_scale
        self.tile_size = self.scale * self.cfg.cheerio_radius
        self.max_steps = max_steps

        # load pickled density-motion data
        with open(pickle_density_motion_file_name, 'rb') as handle:
            distribution_list = pickle.load(handle)
        inds_of_correct_scale = [item[0] for item in enumerate(distribution_list)
                                 if item[1][1].scale == self.scale]
        self.distribution_list = [distribution_list[i] for i in inds_of_correct_scale]
        self.TiledGrid = self.create_tiled_grid()
        self.length_results = []
        self.time_results = []

    def create_tiled_grid(self):
        tilefilename = 'Tiled Grids/' + self.video_number + '_grid_scale_' + str(self.scale) \
                       + '.pickle'
        xbox_starts = np.arange(0, 1, self.tile_size/2)[:-2]
        ybox_starts = np.arange(self.cfg.y_range[0], self.cfg.y_range[1], self.tile_size/2)[:-2]
        self.actual_x_range = (0.5*self.tile_size, xbox_starts[-1]+0.5*self.tile_size)
        self.actual_y_range = (ybox_starts[0]+0.5*self.tile_size, ybox_starts[-1]+0.5*self.tile_size)

        if divmod(len(ybox_starts), 2)[1]:
            self.path = [P(0.5*self.tile_size, (self.actual_y_range[1] + self.actual_y_range[0])
                           / 2)]
        else:
            self.path = [P(0.5*self.tile_size, (self.actual_y_range[1] + self.actual_y_range[0])
                           / 2+self.tile_size/4)]

        try:
            with open(tilefilename, 'rb') as handle:
                tiled_grid = pickle.load(handle)
        except FileNotFoundError:
            point_list = [P(i, j) for i in xbox_starts for j in ybox_starts]
            tiled_grid = []
            for p in point_list:
                box = BoxAnalysis.create_box(p, 'bottom left', self.tile_size)
                density = self.cfg.stones.box_density(self.cfg.cheerio_radius, box)
                tiled_grid.append((p, density))
                print([p, density])
            with open(tilefilename, 'wb') as handle:
                pickle.dump(tiled_grid, handle, protocol=pickle.HIGHEST_PROTOCOL)
        finally:
            return tiled_grid

    def run_simulation(self):
        current_step = 0
        while True:
            self.step()
            current_step += 1
            bool_res, specific_res = self.is_done(current_step)
            if bool_res:
                return self.path, self.length_results, self.time_results, specific_res

    def step(self):
        current_density = next(point[1] for point in self.TiledGrid
                               if point[0].dist(self.path[-1]-P(0.5*self.tile_size,
                                                                0.5*self.tile_size)) < 10**-8)
        current_density = math.floor(current_density*10)/10
        relevant_distribution_results = next(item for item in self.distribution_list
                                             if item[1].box_density == current_density)
        exit_probabilities = np.append(np.array([0]), np.cumsum(np.array(
                        [relevant_distribution_results[i].exit_probability
                         for i in range(0, 3)])))
        drawn = np.random.random()
        while drawn == 0:
            drawn = np.random.random()
        direction_dict = {0: 'Back', 1: 'Front', 2: 'Sides'}
        for i in range(0, 3):
            if exit_probabilities[i] < drawn < exit_probabilities[i+1]:
                self.draw_from_distribution_results(direction_dict[i], relevant_distribution_results)
                # if i == 0:  # back
                #     self.path.append(self.path[-1]-P(0.5*self.tile_size, 0))
                # elif i == 1:  # front
                #     self.path.append(self.path[-1] + P(0.5 * self.tile_size, 0))
                # elif i == 2:  # sides
                #     if drawn[1] > 0.5:  # up
                #         self.path.append(self.path[-1] + P(0, 0.5 * self.tile_size))
                #     else:  # down
                #         self.path.append(self.path[-1] - P(0, 0.5 * self.tile_size))

    def draw_from_distribution_results(self, direction, relevant_distribution_results):
        add_dict = {'Back': -P(0.5*self.tile_size, 0), 'Front': P(0.5 * self.tile_size, 0),
                    'Sides': P(0, 0.5 * self.tile_size)}
        relevant_distribution = next(item for item in relevant_distribution_results
                                     if item[1].direction == direction)

        if self.path[-1].x == self.tile_size/2 and direction == 'Back':
            return

        if direction != 'Sides':
            self.path.append(self.path[-1]+add_dict[direction])
        else:
            drawn = np.random.random()
            while drawn == 0.5:
                drawn = np.random.random()
            self.path.append(self.path[-1] + misc.sign(drawn-0.5)*add_dict[direction])

        l = len(relevant_distribution.length_distribution)
        drawn = np.random.random()
        index = math.floor(drawn/(1/l))
        self.length_results.append(relevant_distribution.length_distribution[index])
        self.time_results.append(relevant_distribution.time_distribution[index])

    def is_done(self, current_step):
        if current_step >= self.max_steps:
            return True, 'InBounds'
        elif self.path[-1].x > self.actual_x_range[1]:
            return True, 'Front'
        elif self.path[-1].y > self.actual_y_range[1] or \
             self.path[-1].y < self.actual_y_range[0]:
            return True, 'Sides'
        return False, 'Continue'

if __name__ == "__main__":
    video_number = "1400008"
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    tilescale = 2
    sim = TiledGridSimulation(video_number, pickle_file_name, tile_scale=tilescale)
    load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
exit(0)
