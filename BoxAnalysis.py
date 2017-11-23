import configuration
import rectangle
import run
import path
import numpy as np
import misc
import pickle
import math


class BoxAnalysis:

    def __init__(self, scale, cfg: configuration.Configuration, load_center_loc='middle',
                 given_path=None):
        if load_center_loc == 'middle' or load_center_loc == 'left':
            self._load_center_loc = load_center_loc
        else:
            raise ValueError('load_center_loc can only take the following values: \n\t\t middle, '
                             'left')
        self.cfg = cfg
        self.size = scale * self.cfg.cheerio_radius
        if given_path:
            self.path = given_path
        else:
            self.path = self.cfg.path.points
        self.path_length = len(self.path)
        self.AnalysisResult = []

    def boxes_stats(self):
        """
        Computes stats for motion of load through small tiles of the board.
        :return: list of tuples containing (density of (inflated) cubes in the box (float ratio),
        result of run - used to know which elements to ignore (boolean), total distance travelled
        within box, time to traverse the box
        """

        if self._load_center_loc == 'middle':
            index = next(point[0] for point in enumerate(self.path) if point[1].x > self.size/2)
        elif self._load_center_loc == 'left':
            index = 0
        if 'index' not in locals():
            raise NameError

        # noinspection PyUnboundLocalVariable
        while self.index_condition_entire(index):
            p = self.path[index]
            box = BoxAnalysis.create_box(p, self._load_center_loc, self.size)
            r, ant_res = run.Run(run.AntRunner(self.cfg, index, self.path),
                                 containing_box=box).run()
            r_length = len(r)
            if r[-1].x > box.qx:
                exit_direction = 'Front'
            elif r[-1].x < box.px:
                exit_direction = 'Back'
            elif r[-1].y < box.py or r[-1].y > box.qy:
                exit_direction = 'Sides'
            else:
                exit_direction = 'error'

            self.AnalysisResult.append((self.cfg.stones.box_density(self.cfg.cheerio_radius, box),
                                        path.MotionPath(r).length(), exit_direction, r_length))

            if self._load_center_loc == 'middle':
                dist_test_generator = (ind for ind in range(index+r_length-1, self.path_length) if
                                       self.away_from_center_test(self.path[ind], box))
            elif self._load_center_loc == 'left':
                dist_test_generator = (ind for ind in range(index+r_length-1, self.path_length)
                                       if box.px > self.path[ind].x or self.path[ind].x > box.qx or
                                       box.py > self.path[ind].y or self.path[ind].y > box.qy)
            if 'dist_test_generator' in locals():
                # noinspection PyUnboundLocalVariable
                index = next(dist_test_generator, self.path_length)
                print('\r' + '{} out of {}'.format(index, self.path_length), sep=' ', end=' ',
                      flush=True)
            else:
                raise NameError

    def index_condition_entire(self, index):
        if self._load_center_loc == 'left':
            continue_loop = index < self.path_length and \
                self.path[index].x < 1 - self.size and \
                self.size / 2 < self.path[index].y < 1 - self.size / 2
        elif self._load_center_loc == 'middle':
            continue_loop = index < len(self.path) and \
                self.size / 2 < self.path[index].x < 1 - self.size / 2 and \
                self.size / 2 < self.path[index].y < 1 - self.size / 2
        if 'continue_loop' in locals():
            # noinspection PyUnboundLocalVariable
            return continue_loop
        else:
            raise NameError

    @staticmethod
    def create_box(p, load_center_loc, size):
        if load_center_loc == 'left':
            box = rectangle.Rectangle(p.x, p.y - size/2, p.x + size, p.y + size/2)
        elif load_center_loc == 'middle':
            box = rectangle.Rectangle(p.x - size/2, p.y - size/2, p.x + size/2,
                                      p.y + size/2)
        elif load_center_loc == 'bottom left':
            box = rectangle.Rectangle(p.x, p.y, p.x + size, p.y + size)
        if 'box' in locals():
            # noinspection PyUnboundLocalVariable
            return box
        else:
            raise NameError

    def away_from_center_test(self, path_point, box):
        dist_list = [path_point.dist(box_point) for box_point in box]
        if min(dist_list) > np.sqrt(2)*self.size/2:
            return True
        return False

    @staticmethod
    def compute_statistics(analysis_results, scale):
        box_density = [i[0] for i in analysis_results]
        density_bins = np.arange(0, 1.1, 0.1)
        bins_idx = np.digitize(box_density, density_bins)
        # noinspection PyShadowingNames
        distribution_list = []
        for current_box_density_index in range(density_bins.size-1):
            which_indices = [inds[0] for inds in enumerate(bins_idx) if inds[1] ==
                             current_box_density_index + 1]
            relevant_density_analysis_results = [analysis_results[k] for k in which_indices]
            distributions = tuple(DistributionResults(relevant_density_analysis_results,
                                                      math.floor(density_bins[
                                                          current_box_density_index]*10)/10,
                                                      string, scale)
                                  for string in ['Back', 'Front', 'Sides'])
            distributions = DistributionResults.calculate_exit_probabilities(distributions)
            distribution_list.append(distributions)
        return distribution_list


class DistributionResults:

    def __init__(self, analysis_results, current_box_density, direction, scale):
        exit_direction = [i[2] for i in analysis_results]
        final_indices = [inds[0] for inds in enumerate(exit_direction) if inds[1] == direction]
        final_relevant_density_analysis_results = [analysis_results[k] for k in
                                                   final_indices]
        self.length_distribution = [i[1] for i in final_relevant_density_analysis_results]
        self.time_distribution = [i[3] for i in final_relevant_density_analysis_results]
        self.box_density = current_box_density
        self.direction = direction
        self.scale = scale
        self.exit_probability = None

    @staticmethod
    def calculate_exit_probabilities(object_tuple: tuple):
        assert len(object_tuple) == 3

        direction_list = [obj.direction for obj in object_tuple]
        # sorted_direction_indices = [i[0] for i in sorted(enumerate(direction_list),
        #                                                  key=lambda x: x[1])]
        assert [direction_list[i] for i in range(3)] == ['Back', 'Front', 'Sides']

        lengths = [len(obj) for obj in object_tuple]
        sample_size = sum(lengths)
        if sample_size > 0:
            [setattr(object_tuple[i], 'exit_probability', lengths[i]/sample_size)
             for i in range(len(object_tuple))]
        return object_tuple

    def __len__(self):
        return len(self.length_distribution)

    def __eq__(self, other):
        if self.__class__ != DistributionResults or other.__class__ != DistributionResults:
            raise TypeError

        attribute_list = dir(self)
        compare_attr = (self.__getattribute__(attr).__eq__(other.__getattribute__(attr)) for attr in
                        attribute_list if attr[1] != '_')
        if all(compare_attr):
            return True
        else:
            return False

if __name__ == "__main__":
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    # scale_list = [5]
    distribution_list = []
    # maxfiles = 3
    # filenum = 0
    loadloc = 'middle'
    for scale_size in scale_list:
        single_scale_analysis_list = []
        for file in misc.all_file_names():
            print(file)
            current_cfg = configuration.Configuration(file_name=file)
            NewBox = BoxAnalysis(scale_size, current_cfg, loadloc)
            NewBox.boxes_stats()
            single_scale_analysis_list.extend(NewBox.AnalysisResult)
            # filenum += 1
            # if filenum == maxfiles:
            #     break
            # run_movie(current_cfg, current_runner, only_save=True)
        distribution_list.extend(BoxAnalysis.compute_statistics(single_scale_analysis_list,
                                                                scale_size))
    filename = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    with open(filename, 'wb') as handle:
        pickle.dump(distribution_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

    exit(0)

####################################################################################################

# def boxes(self):
#       if self.draw:
#           movie_instance = movie.Movie()
#           movie_instance.background([(self.cfg, "black")])
#       index = 0
#       path_var = self.cfg.path.points
#       result = []
#
#       while self.index_condition(index):
#           p = path_var[index]
#           box = rectangle.Rectangle(p.x, p.y - self.size / 2, p.x + self.size, p.y + self.size
#                                     / 2)
#
#           good = 0
#           times = 10
#           for i in range(times):
#               self.cfg.start = p
#               self.cfg.reset_runseed() #### ??? ####
#               r, sim_res = run.Run(run.SimulationRunner(self.cfg), containing_box=box).run()
#               if sim_res:
#                   good += 1
#               if self.draw:
#                   if sim_res:
#                       color = "green"
#                   else:
#                       color = "black"
#                       movie_instance.background([(path_var.MotionPath(r), color)])
#
#           r, ant_res = run.Run(run.AntRunner(self.cfg, index), containing_box=box).run()
#           if self.draw:
#               if ant_res:
#                   color = "green"
#               else:
#                   color = "black"
#                   movie_instance.background([(path_var.MotionPath(r), "blue")])
#               box.add_text(
#                   '{:.0f}%,{:.0f}%'.format(BoxAnalysis.box_density(self.cfg, box) * 100,
#                                            good / times * 100))
#               movie_instance.background([(box, color)])
#
#           result.append((BoxAnalysis.box_density(self.cfg, box), ant_res, good / times))
#           while index < len(path_var) and path_var[index].x < box.qx:
#               index += 1
#
#       if self.draw:
#           movie_instance.save_figure(self.cfg.file_name + "_boxes")
#           movie_instance.close()
#           # movie.just_draw()
#       return result

#  #######   probably needs to be taken out to run with different box analysis
#     def all_boxes(self, dots=5):
#         good = np.zeros(dots + 1)
#         count = np.zeros(dots + 1)
#         lengths = np.zeros(dots + 1)
#         for file_name in misc.all_file_names():
#             cfg = configuration.Configuration(file_name=file_name)
#             for density, res, length in self.boxes_stats(self.cfg):
#                 index = density * dots
#                 length /= self.size * cfg.cheerio_radius
#                 misc.add_at_fractional_index(count, index, 1)
#                 if res:
#                     misc.add_at_fractional_index(good, index, 1)
#                     misc.add_at_fractional_index(lengths, index, length)
#         return good / count, lengths / good
#
#
#     def plot_boxes():
#         plots = Plots()
#         dots = 5
#         for size in range(2, 11, 2):
#             x = np.linspace(0, 1, dots + 1)
#             y = all_boxes(size, dots)
#             plots.add_plot(x, y, str(size))
#         plt.legend()
#         plots.show()
#         exit(0)
#
#     def plot_boxes2():
#         plots = Plots()
#         dots = 5
#         res = None
#         for size in range(2, 11, 1):
#             dummy, r = all_boxes(size, dots)
#             if res is None:
#                 res = r
#             else:
#                 res = np.vstack((res, r))
#         res = res.transpose()
#         print(res)
#         x = np.arange(2, 11, 1)
#         for i in range(dots + 1):
#             plots.add_plot(x, res[i], str(round(i * 0.2, 1)))
#
#         plots.show()
#         exit(0)
#
#
# # main boxes run


