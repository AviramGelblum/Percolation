import pickle
import configuration
import numpy as np
from point import P
from BoxAnalysis import BoxAnalysis, DistributionResults
import math
import misc
import movie
from path import MotionPath
import matplotlib.pyplot as plt


####################### Base Grid Simulation Class ############################

class GridSimulation:
    def __init__(self, pickle_density_motion_file_name, video_number=None, seed=None,
                 num_stones=None, tile_scale=1, max_steps=10000):
        self.video_number = video_number
        self.num_stones = num_stones

        if video_number:
            self.cfg = configuration.Configuration(file_name=self.video_number, border=False)
        else:
            # no video number specified, cfg uses random seed or given seed if specified
            if num_stones:
                self.cfg = configuration.Configuration(seed=seed, num_stones=self.num_stones, border=False)
            else:
                raise ValueError('number of cubes (num_stones parameter) must be specified')

        self.scale = tile_scale
        self.tile_size = self.scale * self.cfg.cheerio_radius
        self.max_steps = max_steps

        # load pickled density-motion data
        with open(pickle_density_motion_file_name, 'rb') as handle:
            distribution_list = pickle.load(handle)
        inds_of_correct_scale = [item[0] for item in enumerate(distribution_list)
                                 if item[1][1].scale == self.scale]
        self.distribution_list = [distribution_list[i] for i in inds_of_correct_scale]
        self.TiledGrid, self.actual_x_range, self.actual_y_range, self.path = \
            self.create_tiled_grid()
        self.length_results = []
        self.time_results = []

    def create_tiled_grid(self):
        if self.video_number:
            tilefilename = 'Tiled Grids/' + self.video_number + '_grid_scale_' + str(self.scale) \
                       + '.pickle'
        else:
            tilefilename = 'Tiled Grids/seed_' + str(self.cfg.seed) + '_grid_scale_' \
                           + str(self.scale) + '_num_cubes_' + str(self.num_stones) \
                           + '.pickle'

        xbox_starts = np.arange(0, 1, self.tile_size/2)[:-2]
        ybox_starts = np.arange(self.cfg.y_range[0], self.cfg.y_range[1], self.tile_size/2)[:-2]
        actual_x_range = (0.5*self.tile_size, xbox_starts[-1]+0.5*self.tile_size)
        actual_y_range = (ybox_starts[0]+0.5*self.tile_size, ybox_starts[-1]+0.5*self.tile_size)
        # (min_val, index_min) = min((v, i) for i, v in
        #                        enumerate([abs(self.cfg.path.points[0].x - num)
        #
        #                                    for num in xbox_starts]))
        # import operator
        # min_index, min_value = min(enumerate(values), key=operator.itemgetter(1))

        index_min_x = np.argmin([abs(self.cfg.path.points[0].x - num) for num in
                                xbox_starts])
        index_min_y = np.argmin([abs(self.cfg.path.points[0].y - num) for num in
                                ybox_starts])

        path_out = [P(xbox_starts[max([index_min_x, 1])], ybox_starts[max([index_min_y, 1])])]

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
            return tiled_grid, actual_x_range, actual_y_range, path_out

    def compute_exit_probabilities_and_distributions(self, current_density):
        init_density = math.floor(current_density * 10) / 10
        # assert divmod(current_density/0.1, 1)[1] == 0
        while True:
            try:
                current_density = math.floor(current_density * 10) / 10
                relevant_distribution_results = next(item for item in self.distribution_list
                                                     if item[1].box_density == current_density)
                exit_probabilities = np.append(np.array([0]), np.cumsum(np.array(
                    [relevant_distribution_results[i].exit_probability
                     for i in range(0, 3)])))
                break
            except TypeError as e:
                if e.args[0][51:-1] == 'NoneType':
                    if init_density < 0.3:
                        current_density += 0.1
                    else:
                        current_density -= 0.1
                    if current_density < 0:
                        raise ValueError('Current Density is 0!')
                else:
                    raise
            except StopIteration:
                current_density -= 0.1
                if current_density < 0:
                    raise ValueError('Current Density is 0!')
        return exit_probabilities, relevant_distribution_results

    @staticmethod
    def draw_from_distribution_results(direction, relevant_distribution_results):

        relevant_distribution = next(item for item in relevant_distribution_results
                                     if item.direction == direction)

        drawn = np.random.random()
        index = math.floor(drawn / (1 / len(relevant_distribution.length_distribution)))
        return relevant_distribution.time_distribution[index],\
            relevant_distribution.length_distribution[index]

    def draw_from_exit_and_perform_function(self, exit_probabilities, method_to_perform,
                                            relevant_distribution_results, *optional_parameters):
        drawn = np.random.random()
        while drawn == 0:
            drawn = np.random.random()
        direction_dict = {0: 'Back', 1: 'Front', 2: 'Sides'}
        for i in range(0, 3):
            if exit_probabilities[i] < drawn < exit_probabilities[i+1]:
                method = getattr(self, method_to_perform)
                return method(direction_dict[i], relevant_distribution_results,
                              *optional_parameters)

    def run_simulation(self):
        current_step = 0
        while True:
            self.step()
            current_step += 1
            # print(current_step)
            bool_res, final_out = self.is_done(current_step)
            if bool_res:
                return self.path, self.length_results, self.time_results, final_out

    def step(self):
        pass

    def move(self, direction):
        add_dict = {'Back': -P(0.5*self.tile_size, 0), 'Front': P(0.5 * self.tile_size, 0),
                    'Sides': P(0, 0.5 * self.tile_size)}
        if math.isclose(self.path[-1].x, self.tile_size/2) and direction == 'Back':
            return False

        if direction != 'Sides':
            self.path.append(self.path[-1]+add_dict[direction])
        else:
            drawn = np.random.random()
            while drawn == 0.5:
                drawn = np.random.random()
            self.path.append(self.path[-1] + misc.sign(drawn-0.5)*add_dict[direction])

        return True

    def is_done(self, current_step):
        if current_step >= self.max_steps:
            return True, 'InBounds'
        elif self.path[-1].x > self.actual_x_range[1]:
            return True, 'Front'
        elif self.path[-1].y > self.actual_y_range[1] or self.path[-1].y < self.actual_y_range[0]:
            return True, 'Sides'
        return False, 'Continue'


####################### Children Simulation Classes ############################


######### Tiled Grid Simulation ###########

class TiledGridSimulation(GridSimulation):
    def __init__(self, pickle_density_motion_file_name, video_number=None, seed=None,
                 num_stones=None, tile_scale=1, max_steps=10000):
        super().__init__(pickle_density_motion_file_name, video_number, seed, num_stones,
                         tile_scale, max_steps)

    def step(self):
        current_density = next(point[1] for point in self.TiledGrid
                               if point[0] == self.path[-1]-P(0.5*self.tile_size,
                                                              0.5*self.tile_size))
        exit_probabilities, relevant_distribution_results = \
            self.compute_exit_probabilities_and_distributions(current_density)

        self.draw_from_exit_and_perform_function(exit_probabilities, 'tiled_motion',
                                                 relevant_distribution_results)

    def tiled_motion(self, direction, relevant_distribution_results):
                if self.move(direction):
                    time_result, length_result = GridSimulation.draw_from_distribution_results(
                                               direction, relevant_distribution_results)
                    self.time_results.append(time_result)
                    self.length_results.append(length_result)
                return None


######### Quenched Grid Simulation ###########

class QuenchedGridSimulation(GridSimulation):
    def __init__(self, pickle_density_motion_file_name, video_number=None, seed=None,
                 num_stones=None,  tile_scale=1, max_steps=10000):
        super().__init__(pickle_density_motion_file_name, video_number, seed, num_stones,
                         tile_scale, max_steps)
        self.QuenchedGrid = self.quench_grid()
        self.fix_quenched_grid()

    def quench_grid(self):
        def set_tile_direction(tile_density):
            exit_probabilities, relevant_distribution_results = \
                self.compute_exit_probabilities_and_distributions(tile_density)
            return self.draw_from_exit_and_perform_function(exit_probabilities, 'quenched_setup',
                                                            relevant_distribution_results)

        quenched_tiled_grid = [self.TiledGrid[i] + set_tile_direction(self.TiledGrid[i][1])
                               for i in range(len(self.TiledGrid))]
        return quenched_tiled_grid


    @staticmethod
    def quenched_setup(direction, relevant_distribution_results):
                time_result, length_result = GridSimulation.draw_from_distribution_results(
                                             direction, relevant_distribution_results)
                return direction, time_result, length_result

    def fix_quenched_grid(self):
        def find_prior_x_tile(tile, other_tile):
            return math.isclose(tile[1] - other_tile[0].x, self.tile_size / 2) and \
                   math.isclose(tile[2], other_tile[0].y)

        tiles_to_check = [(tile[0], tile[1][0].x, tile[1][0].y, tile[1][1]) for tile in
                          enumerate(self.QuenchedGrid) if tile[1][2] == 'Back']
        if tiles_to_check:
            for tile in tiles_to_check:

                fix_it = False
                if math.isclose(tile[1], 0):
                    fix_it = True

                if not fix_it:
                    prior_x_tile_generator = (other_tile for other_tile in self.QuenchedGrid
                                              if find_prior_x_tile(tile, other_tile))
                    try:
                        prior_tile = next(prior_x_tile_generator)
                        fix_it = prior_tile[2] == 'Front'
                    except StopIteration:
                        raise ValueError('Found x<0 as prior tile!')

                if fix_it:
                    relevant_distribution_results = \
                        self.compute_exit_probabilities_and_distributions(tile[3])[1]

                    if relevant_distribution_results[2].exit_probability >= \
                            relevant_distribution_results[1].exit_probability:  # change to sides
                        direction_to = 'Sides'
                    else:  # change to front
                        direction_to = 'Front'

                    time_result, length_result = \
                        QuenchedGridSimulation.quenched_setup(
                            direction_to, relevant_distribution_results)[1:]
                    self.QuenchedGrid[tile[0]] = self.QuenchedGrid[tile[0]][:2] + \
                        (direction_to, time_result, length_result)

    def step(self):
        current_direction, time_result,\
            length_result = next(point[2:] for point in self.QuenchedGrid
                                 if point[0] == self.path[-1]-P(0.5*self.tile_size,
                                                                0.5*self.tile_size))

        if self.move(current_direction):
            self.time_results.append(time_result)
            self.length_results.append(length_result)
        else:
            raise ValueError('Backwards motion assigned to x=0 tile.')


############ Quenched Simulation with mid-trail bias #######

class QuenchedGridTrailBiasSimulation(QuenchedGridSimulation):

    def __init__(self, pickle_density_motion_file_name, bias_values=('constant', None),
                 trail_bias_file_name=None, video_number=None, seed=None, num_stones=None,
                 tile_scale=1, max_steps=10000):
        super(QuenchedGridTrailBiasSimulation, self).__init__(pickle_density_motion_file_name,
              video_number, seed, num_stones, tile_scale, max_steps)
        self.bias_values = bias_values  # tuple(bias_type, max_probability (constant bias), dist,
        # added_probability) where for bias_type 'hooke', for a given distance from trail center (
        # dist, in cm) we add added_probability to the bias towards the trail. Calculated using
        # self.cfg.cheerio_radius as the simulation_units to cm conversion rate,
        # in calculate_trail_bias(). max_probability is the maximum bias towards center (bias
        # saturation). constant bias is the bias we add in case bias_type is 'constant'.
        self.trail_bias_file_name = trail_bias_file_name

    def move(self, direction):
        add_dict = {'Back': -P(0.5 * self.tile_size, 0), 'Front': P(0.5 * self.tile_size, 0),
                    'Sides': P(0, 0.5 * self.tile_size)}
        if math.isclose(self.path[-1].x, self.tile_size / 2) and direction == 'Back':
            return False

        if direction != 'Sides':
            self.path.append(self.path[-1] + add_dict[direction])
        else:
            go_down_chance = self.calculate_trail_bias()
            drawn = np.random.random()
            while drawn == go_down_chance:
                drawn = np.random.random()
            self.path.append(self.path[-1] + misc.sign(drawn - go_down_chance) * add_dict[
                direction])

        return True

    def calculate_trail_bias(self):
        y_diff = self.path[-1].y - self.path[0].y
        bias_direction = -misc.sign(y_diff)
        if bias_direction == 0:
            return 0.5

        if self.bias_values[0] == 'constant':
            if self.bias_values[1]:
                if bias_direction > 0:
                    return 1-self.bias_values[1]
                else:
                    return self.bias_values[1]
            else:
                raise ValueError('bias_values must be supplied.')
        elif self.bias_values[0] == 'hooke':
            if self.bias_values[1]:
                hooke_coef = self.bias_values[3]\
                             / (self.bias_values[2] * self.cfg.cheerio_radius)
                if bias_direction > 0:
                    return 1-min(0.5 + hooke_coef * abs(y_diff), self.bias_values[1])
                else:
                    return min(0.5 + hooke_coef * abs(y_diff), self.bias_values[1])
            else:
                raise ValueError('bias_values must be supplied.')
        elif self.bias_values[0] == 'data':
            if self.trail_bias_file_name:
                with open(self.trail_bias_file_name, 'r') as handle:
                    pass
                raise BaseException('Not implemented yet. Lazy bum!')
            else:
                raise ValueError('trail_bias_file_name must be supplied.')
        else:
            raise ValueError('bias type must take one of the following values: \n constant, '
                             'hooke, data.')


############# Simulation Results Class ###################

class SimulationResults:
    def __init__(self, path, length_results, time_results, final_out, scale, number_of_cubes,
                 video_number=None, seed=None):
        self.path = [path]
        self.length_results = [length_results]
        self.time_results = [time_results]
        self.final_out = [final_out]
        self.scale = [scale]
        self.number_of_cubes = [number_of_cubes]
        if video_number:
            self.video_number = [video_number]
        else:
            self.seed = [seed]

    def append(self, other):
        self.path.append(other.path[0])
        self.length_results.append(other.length_results[0])
        self.time_results.append(other.time_results[0])
        self.final_out.append(other.final_out[0])
        self.scale.append(other.scale[0])
        self.number_of_cubes.append(other.number_of_cubes[0])
        if video_number:
            self.video_number.append(other.video_number[0])
        else:
            self.seed.append(other.seed[0])

    def get_relevant_runs(self,attribute_list=None, attribute_value_list=None):
        if attribute_list.__class__ == list and attribute_value_list.__class__ == list:
            object_length = len(self)
            indices_of_relevant_objects = [i for i in range(object_length) if
                                           self.all_attributes_fit_test(i, attribute_list,
                                                                        attribute_value_list)]
            for i in indices_of_relevant_objects:
                try:
                    relevant_runs.append(self[i])
                except NameError as e:
                    if e.args[0][16:29] == 'relevant_runs':
                        relevant_runs = self[i]
                    else:
                        raise
        elif attribute_list.__class__ != list:
            raise TypeError('attribute_list is not a list!')
        else:
            raise TypeError('attribute_value_list is not a list')
        return relevant_runs

    def all_attributes_fit_test(self, i, attribute_list, attribute_value_list):
            return all([getattr(self, attribute_list[j])[i].__eq__(attribute_value_list[j]) for j in
                        range(len(attribute_list))])

    @staticmethod
    def compute_mean_and_median_sums(relevant_runs):
        num_of_runs = len(relevant_runs)
        sum_length = [sum(relevant_runs[i].length_results[0]) for i in range(num_of_runs)]
        sum_time = [sum(relevant_runs[i].time_results[0]) for i in range(num_of_runs)]
        mean_total_length = np.mean(sum_length)
        median_total_length = np.median(sum_length)
        mean_total_time = np.mean(sum_time)
        median_total_time = np.median(sum_time)
        fraction_front = len(list(filter(lambda x: x == 'Front', [relevant_runs[i].final_out[0]
                                  for i in range(num_of_runs)])))/num_of_runs
        return fraction_front, mean_total_length, mean_total_time, \
               median_total_length, median_total_time, \

    def __len__(self):
        return len(self.scale)

    def __iter__(self):
        for i in range(0, len(self)):
            yield self[i]

    def __getitem__(self, key):
        if self.video_number:
            return SimulationResults(self.path[key], self.length_results[key],
                                     self.time_results[key], self.final_out[key], self.scale[key],
                                     self.number_of_cubes[key], self.video_number[key])
        else:
            return SimulationResults(self.path[key], self.length_results[key],
                                     self.time_results[key], self.final_out[key], self.scale[key],
                                     self.number_of_cubes[key], self.seed[key])
    @staticmethod
    def plot_means_vs_scale(mean_total_lengths, mean_total_times, fractions_front, scale,
                            num_of_cubes, save=False, save_location=None):
        save_addition = ['mean_total_length', 'mean_total_time', 'fraction_front']
        ylabels = ['Mean Total Length', 'Mean Total Time', 'Fraction Front']
        col = ['r', 'b', 'g']

        for stat, c, ylabel, save_add in zip([mean_total_lengths, mean_total_times, fractions_front]
                                             , col, ylabels, save_addition):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(scale, stat, lw=2, color=c)
            ax.set(title=ylabel + ' vs. Scale, ' + str(num_of_cubes) + ' cubes', ylabel=ylabel,
                   xlabel='Scale [cm]')

            fig_manager = plt.get_current_fig_manager()
            fig_manager.window.showMaximized()
            if save:
                if save_location is None:
                    raise ValueError('save_location must be provided')
                fig.savefig(save_location + '_' + save_add + '_' + str(num_of_cubes) + '_cubes',
                            bbox_inches='tight', dpi='figure')
            else:
                plt.show()

    @staticmethod
    def plot_boxplots_vs_scale(relevant_runs, scale, num_of_cubes, save=False, save_location=None):
        save_addition = ['total_length', 'total_time']
        ylabels = ['Total Length', 'Total Time']
        col = ['r', 'b']
        num_of_scales = len(relevant_runs)
        sum_length = []
        sum_time = []
        for i in range(num_of_scales):
            sum_length_temp = []
            sum_time_temp = []
            for k in range(len(relevant_runs[i])):
                sum_length_temp.append(sum(relevant_runs[i][k].length_results[0]))
                sum_time_temp.append(sum(relevant_runs[i][k].time_results[0]))
            sum_length.append(sum_length_temp)
            sum_time.append(sum_time_temp)

        for stat, c, ylabel, save_add in zip([sum_length, sum_time], col, ylabels, save_addition):

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.boxplot(stat, whis=[20, 80])
            ax.set(title=ylabel + ' vs. Scale, ' + str(num_of_cubes) + ' cubes', ylabel=ylabel,
                   xlabel='Scale [cm]')
            ax.xaxis.set_ticklabels(scale)

            fig_manager = plt.get_current_fig_manager()
            fig_manager.window.showMaximized()
            if save:
                if save_location is None:
                    raise ValueError('save_location must be provided')
                fig.savefig(save_location + '_' + save_add + '_' + str(num_of_cubes) + '_cubes',
                            bbox_inches='tight', dpi='figure')
            else:
                plt.show()

    def draw_simulation_run(self, cfg: configuration.Configuration, save=False,
                            save_location=None, background_kwargs_dict=None,
                            simulation_kwargs_dict=None):
        assert len(self) == 1, 'must be a single simulation'
        if background_kwargs_dict is None:
            background_kwargs_dict = {'CubeColor': misc.RGB_255to1((139, 101, 8)), 'PathAlpha':
                                      0.2, 'ShadeAlpha': 0.4, 'CubeAlpha': 0.3}
        drawing_obj = movie.Movie()
        self.draw(drawing_obj, simulation_kwargs_dict)
        drawing_obj.ax.set_ylim(cfg.y_range[0]-0.05, cfg.y_range[1]+0.05)
        drawing_obj.background([(cfg, background_kwargs_dict)])
        if save:
            if save_location is None:
                raise ValueError('save_location must be provided')
            drawing_obj.save_figure(save_location)
        else:
            drawing_obj.just_draw()

    def draw(self, drawing_obj, simulation_kwargs_dict):
        """Draw one iteration"""
        assert len(self) == 1, 'must be a single simulation object'
        current_sim = self[0]
        # if len(self) > 1:
        #     for i in range(0, len(self)):
        #         placeholder = 1
        default_grid_keys = ['cmap', 'cmap_alpha']
        default_grid_values = ['OrRd', 0.8]
        grid_dict = dict(zip(default_grid_keys, default_grid_values))
        default_simulation_path_keys = ['PathColor', 'alpha']
        default_simulation_path_values = ['green', 1]
        simulation_path_dict = dict(zip(default_simulation_path_keys, default_simulation_path_values))
        if simulation_kwargs_dict is not None:
            for key in set(default_grid_keys).intersection(simulation_kwargs_dict.keys()):
                grid_dict[key] = simulation_kwargs_dict[key]
            for key in set(default_simulation_path_keys).intersection(simulation_kwargs_dict.keys()):
                simulation_path_dict[key] = simulation_kwargs_dict[key]

        current_path = MotionPath(current_sim.path[0])
        current_path.draw(drawing_obj.ax, {'color': simulation_path_dict['PathColor'],
                                           'alpha': simulation_path_dict['alpha']})
        if self.video_number:
            tilefilename = 'Tiled Grids/' + self.video_number[0] + '_grid_scale_' + str(self.scale[0]) \
                           + '.pickle'
        else:
            tilefilename = 'Tiled Grids/seed_' + str(self.seed[0]) + '_grid_scale_' \
                           + str(self.scale[0]) + '_num_cubes_' + str(self.number_of_cubes[0]) \
                           + '.pickle'
        with open(tilefilename, 'rb') as handle:
            tiled_grid = pickle.load(handle)

        x_unique = np.unique([tup[0].x for tup in tiled_grid])
        y_unique = np.unique([tup[0].y for tup in tiled_grid])

        [xmesh, ymesh] = np.meshgrid(x_unique[slice(0, len(x_unique), 2)],
                                     y_unique[slice(0, len(y_unique), 2)])
        zmesh = np.empty(xmesh.shape)

        for i in range(0, xmesh.shape[0]):
            for j in range(0, xmesh.shape[1]):
                gr_generator = (k[0] for k in enumerate(tiled_grid) if
                                k[1][0] == P(xmesh[i, j], ymesh[i, j]))
                zmesh[i, j] = tiled_grid[next(gr_generator)][1]

        pcm = drawing_obj.ax.pcolormesh(xmesh, ymesh, zmesh, **{'cmap': grid_dict['cmap'], 'alpha':
                                        grid_dict['cmap_alpha']})
        drawing_obj.fig.colorbar(pcm)


######### main ####################


############## cube mazes from data #############

if 0:  # __name__ == "__main__":

    scale_list = [1, 2, 4, 6, 8, 10, 15]
    number_of_iterations = 50
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    # results_pickle_file_name = 'Pickle Files/SimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    cube_densities = [100, 200, 225, 250, 275, 300]
    # bias_values = ('constant', 0.75)
    bias_values = ('hooke', 0.8, 10, 0.3)
    for tilescale in scale_list:
        for cube_density in cube_densities:
            for video_number in misc.file_names_by_density(cube_density):
                print('scale = ' + str(tilescale))
                print(video_number)
                for iteration in range(1, number_of_iterations+1):
                    print(iteration)
                    # sim = TiledGridSimulation(pickle_file_name, video_number=video_number,
                    #                           tile_scale=tilescale)
                    # sim = QuenchedGridSimulation(pickle_file_name, video_number=video_number,
                    #                              tile_scale=tilescale)
                    sim = QuenchedGridTrailBiasSimulation(pickle_file_name, bias_values,
                                                          video_number=video_number,
                                                          tile_scale=tilescale)

                    load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
                    try:
                        ResultsObject.append(SimulationResults(load_path, load_trajectory_length,
                                                               load_time, where_out, tilescale,
                                                               cube_density,
                                                               video_number=video_number))
                    except NameError as e:
                        if e.args[0][6:19] == 'ResultsObject':
                            ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                              load_time, where_out, tilescale,
                                                              cube_density,
                                                              video_number=video_number)
                        else:
                            raise
                    except AttributeError:
                        ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                          load_time, where_out, tilescale,
                                                          cube_density, video_number)
        # results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
        #                            '_iterations_' + str(number_of_iterations) + '.pickle'
        # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_Scale_' + str(tilescale) \
        #                            + '_iterations_' + str(number_of_iterations) + '.pickle'
        results_pickle_file_name = 'Pickle Files/QuenchedMidBiasSimulationResults_Scale_' + str(
            tilescale) + '_iterations_' + str(number_of_iterations) + '.pickle'
        with open(results_pickle_file_name, 'wb') as handle:
            pickle.dump([ResultsObject, tilescale, cube_densities, number_of_iterations,
                         bias_values], handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        ResultsObject = None

##################### simulated cubes ############

if __name__ == "__main__":
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    number_of_iterations = 75
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    # results_pickle_file_name = 'Pickle Files/SimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    cube_densities = [100, 150, 200, 225, 250, 275, 300, 400]
    number_of_mazes_per_density = 30
    # bias_values = ('constant', 0.75)
    bias_values = ('hooke', 0.8, 10, 0.3)
    for tilescale in scale_list:
        for cube_density in cube_densities:
            for seed in misc.yield_rand(number_of_mazes_per_density):
                print('scale = ' + str(tilescale))
                print('seed = ' + str(seed))
                for iteration in range(1, number_of_iterations+1):
                    print(iteration)
                    # sim = TiledGridSimulation(pickle_file_name, video_number=video_number,
                    #                           tile_scale=tilescale)
                    # sim = QuenchedGridSimulation(pickle_file_name, video_number=video_number,
                    #                              tile_scale=tilescale)
                    sim = QuenchedGridTrailBiasSimulation(pickle_file_name, bias_values,
                                                          seed=seed, num_stones=cube_density,
                                                          tile_scale=tilescale)

                    load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
                    try:
                        ResultsObject.append(SimulationResults(load_path, load_trajectory_length,
                                                               load_time, where_out, tilescale,
                                                               cube_density, seed=seed))
                    except NameError as e:
                        if e.args[0][6:19] == 'ResultsObject':
                            ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                              load_time, where_out, tilescale,
                                                              cube_density, seed=seed)
                        else:
                            raise
                    except AttributeError:
                        ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                          load_time, where_out, tilescale,
                                                          cube_density, seed=seed)
        # results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
        #                            '_iterations_' + str(number_of_iterations) + '.pickle'
        # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_Scale_' + str(tilescale) \
        #                            + '_iterations_' + str(number_of_iterations) + '.pickle'
        results_pickle_file_name = 'Pickle ' \
                                   'Files/QuenchedMidBiasSimulationResults_Simulated_Cubes_Scale_' \
                                   + str(tilescale) + '_iterations_' + str(number_of_iterations) \
                                   + '.pickle'
        with open(results_pickle_file_name, 'wb') as handle:
            pickle.dump([ResultsObject, tilescale, cube_densities, number_of_iterations,
                         bias_values], handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        ResultsObject = None

# if __name__ == "__main__":
#     scale_list = [1, 2, 4, 6, 8, 10, 15]
#     loadloc = 'middle'
#     pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
#     cube_densities = [100, 200, 225, 250, 275, 300]
#     for tilescale in scale_list:
#         for cube_density in cube_densities:
#             for video_number in misc.file_names_by_density(cube_density):
#                     sim = TiledGridSimulation(video_number, pickle_file_name, tile_scale=tilescale)
# exit(0)
