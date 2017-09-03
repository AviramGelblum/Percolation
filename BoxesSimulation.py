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
        # (min_val, index_min) = min((v, i) for i, v in
        #                        enumerate([math.fabs(self.cfg.path.points[0].x - num)
        #
        #                                    for num in xbox_starts]))
        # import operator
        # min_index, min_value = min(enumerate(values), key=operator.itemgetter(1))

        index_min_x = np.argmin([math.fabs(self.cfg.path.points[0].x - num) for num in
                                xbox_starts])
        index_min_y = np.argmin([math.fabs(self.cfg.path.points[0].y - num) for num in
                                ybox_starts])

        self.path = [P(xbox_starts[max([index_min_x, 1])], ybox_starts[max([index_min_y, 1])])]

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
            # print(current_step)
            bool_res, final_out = self.is_done(current_step)
            if bool_res:
                return self.path, self.length_results, self.time_results, final_out

    def step(self):
        current_density = next(point[1] for point in self.TiledGrid
                               if point[0].dist(self.path[-1]-P(0.5*self.tile_size,
                                                                0.5*self.tile_size)) < 10**-8)

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

        drawn = np.random.random()
        while drawn == 0:
            drawn = np.random.random()
        direction_dict = {0: 'Back', 1: 'Front', 2: 'Sides'}
        for i in range(0, 3):
            if exit_probabilities[i] < drawn < exit_probabilities[i+1]:
                self.draw_from_distribution_results(direction_dict[i], relevant_distribution_results)

    def draw_from_distribution_results(self, direction, relevant_distribution_results):
        add_dict = {'Back': -P(0.5*self.tile_size, 0), 'Front': P(0.5 * self.tile_size, 0),
                    'Sides': P(0, 0.5 * self.tile_size)}
        relevant_distribution = next(item for item in relevant_distribution_results
                                     if item.direction == direction)

        if self.path[-1].x == self.tile_size/2 and direction == 'Back':
            return

        if direction != 'Sides':
            self.path.append(self.path[-1]+add_dict[direction])
        else:
            drawn = np.random.random()
            while drawn == 0.5:
                drawn = np.random.random()
            self.path.append(self.path[-1] + misc.sign(drawn-0.5)*add_dict[direction])

        drawn = np.random.random()
        index = math.floor(drawn/(1/len(relevant_distribution.length_distribution)))
        self.length_results.append(relevant_distribution.length_distribution[index])
        self.time_results.append(relevant_distribution.time_distribution[index])

    def is_done(self, current_step):
        if current_step >= self.max_steps:
            return True, 'InBounds'
        elif self.path[-1].x > self.actual_x_range[1]:
            return True, 'Front'
        elif self.path[-1].y > self.actual_y_range[1] or self.path[-1].y < self.actual_y_range[0]:
            return True, 'Sides'
        return False, 'Continue'


class SimulationResults:
    def __init__(self, path, length_results, time_results, final_out, scale, number_of_cubes,
                 video_number):
        self.path = [path]
        self.length_results = [length_results]
        self.time_results = [time_results]
        self.final_out = [final_out]
        self.scale = [scale]
        self.number_of_cubes = [number_of_cubes]
        self.video_number = [video_number]

    def append(self, other):
        self.path.append(other.path[0])
        self.length_results.append(other.length_results[0])
        self.time_results.append(other.time_results[0])
        self.final_out.append(other.final_out[0])
        self.scale.append(other.scale[0])
        self.number_of_cubes.append(other.number_of_cubes[0])
        self.video_number.append(other.video_number[0])

    ######################################################################
    def compute_mean_sums_by(self, attribute_list=None, attribute_value_list=None):
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

        num_of_runs = len(relevant_runs)
        mean_total_length = np.mean([sum(relevant_runs[i].length_results[0]) for i in range(
                                    num_of_runs)])
        mean_total_time = np.mean([sum(relevant_runs[i].time_results[0]) for i in range(
                                  num_of_runs)])
        fraction_front = len(list(filter(lambda x: x == 'Front', [relevant_runs[i].final_out[0]
                                  for i in range(num_of_runs)])))/num_of_runs
        return mean_total_length, mean_total_time, fraction_front

    def all_attributes_fit_test(self, i, attribute_list, attribute_value_list):
            attribute_list_length = len(attribute_list)
            return all([getattr(self, attribute_list[j])[i].__eq__(attribute_value_list[j]) for j in
                        range(attribute_list_length)])

    def __len__(self):
        return len(self.scale)

    def __iter__(self):
        for i in range(0, len(self)):
            yield self[i]

    def __getitem__(self, key):
        return SimulationResults(self.path[key], self.length_results[key], self.time_results[key],
                                 self.final_out[key], self.scale[key], self.number_of_cubes[key],
                                 self.video_number[key])
    @staticmethod
    def plot_stats_vs_scale(mean_total_lengths, mean_total_times, fractions_front, scale,
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

        tilefilename = 'Tiled Grids/' + self.video_number[0] + '_grid_scale_' + str(self.scale[0]) \
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
                                k[1][0].dist(P(xmesh[i, j], ymesh[i, j])) < 10 ** -8)
                zmesh[i, j] = tiled_grid[next(gr_generator)][1]

        pcm = drawing_obj.ax.pcolormesh(xmesh, ymesh, zmesh, **{'cmap': grid_dict['cmap'], 'alpha':
                                        grid_dict['cmap_alpha']})
        drawing_obj.fig.colorbar(pcm)



#########################################################################


if __name__ == "__main__":
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    number_of_iterations = 50
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    results_pickle_file_name = 'Pickle Files/SimulationResults_' + str(
        number_of_iterations)+'iterations'
    cube_densities = [100, 200, 225, 250, 275, 300]
    for tilescale in scale_list:
        for cube_density in cube_densities:
            for video_number in misc.file_names_by_density(cube_density):
                print('scale = ' + str(tilescale))
                print(video_number)
                for iteration in range(1, number_of_iterations+1):
                    print(iteration)
                    sim = TiledGridSimulation(video_number, pickle_file_name, tile_scale=tilescale)
                    load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
                    try:
                        ResultsObject.append(SimulationResults(load_path, load_trajectory_length,
                                                               load_time, where_out, tilescale,
                                                               cube_density, video_number))
                    except NameError as e:
                        if e.args[0][6:19] == 'ResultsObject':
                            ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                              load_time, where_out, tilescale,
                                                              cube_density, video_number)
                        else:
                            raise
                    except AttributeError:
                        ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                          load_time, where_out, tilescale,
                                                          cube_density, video_number)
        results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
                                   '_iterations_' + str(number_of_iterations) + '.pickle'
        with open(results_pickle_file_name, 'wb') as handle:
            pickle.dump([ResultsObject, tilescale, cube_densities, number_of_iterations], handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        ResultsObject = 1

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
