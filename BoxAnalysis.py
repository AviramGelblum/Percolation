import configuration
import rectangle
import movie
import run
import path
import numpy as np
import misc


class BoxAnalysis:

    def __init__(self, scale, cfg: configuration.Configuration, load_center_loc='middle',
                 draw=True):
        if load_center_loc == 'middle' or load_center_loc == 'left':
            self._load_center_loc = load_center_loc
        else:
            raise ValueError('load_center_loc can only take the following values: \n\t\t middle, '
                             'left')
        self.draw = draw
        self.cfg = cfg
        self.size = scale * self.cfg.cheerio_radius
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

        while self.index_condition_entire(index):
            p = self.path[index]
            box = self.create_box(p)
            r, ant_res = run.Run(run.AntRunner(self.cfg, index), containing_box=box).run()
            r_length = len(r)
            if r[-1].x > box.qx:
                exit_direction = 'front'
            elif r[-1].x < box.px:
                exit_direction = 'back'
            elif r[-1].y < box.py or r[-1].y > box.qy:
                exit_direction = 'sides'
            else:
                exit_direction = 'error'

            self.AnalysisResult.append((self.cfg.stones.box_density(self.cfg.cheerio_radius, box),
                                        ant_res, path.MotionPath(r).length(), exit_direction,
                                        r_length))

            if self._load_center_loc == 'middle':
                dist_test_generator = (ind for ind in range(index+r_length-1, self.path_length) if
                                       self.away_from_center_test(self.path[ind], box))
            elif self._load_center_loc == 'left':
                dist_test_generator = (ind for ind in range(index+r_length-1, self.path_length)
                                       if box.px > self.path[ind].x or self.path[ind].x > box.qx or
                                       box.py > self.path[ind].y or self.path[ind].y > box.qy)
            index = next(dist_test_generator, self.path_length)
            print('\r' + '{} out of {}'.format(index, self.path_length), sep=' ', end=' ',
                  flush=True)
            # while index < len(path_var) and box.px < path_var[index].x < box.qx \
            #         and box.py < path_var[index].y < box.qy:
            #     index += 1

    def index_condition_entire(self, index):
        if self._load_center_loc == 'left':
            continue_loop = index < self.path_length and \
                self.path[index].x < 1 - self.size and \
                self.size / 2 < self.path[index].y < 1 - self.size / 2
        elif self._load_center_loc == 'middle':
            continue_loop = index < len(self.path) and \
                self.size / 2 < self.path[index].x < 1 - self.size / 2 and \
                self.size / 2 < self.path[index].y < 1 - self.size / 2
        return continue_loop

    def create_box(self, p):
        if self._load_center_loc == 'left':
            box = rectangle.Rectangle(p.x, p.y - self.size/2, p.x + self.size, p.y + self.size/2)
        elif self._load_center_loc == 'middle':
            box = rectangle.Rectangle(p.x - self.size/2, p.y - self.size/2, p.x + self.size/2,
                                      p.y + self.size/2)
        return box

    def away_from_center_test(self, path_point, box):
        dist_list = [path_point.dist(box_point) for box_point in box]
        if min(dist_list) > np.sqrt(2)*self.size/2:
            return True
        return False

    @staticmethod
    def compute_statistics(analysis_results, scale):
        sample_size = len(analysis_results)
        box_density = [i[0] for i in analysis_results]
        density_bins = np.arange(0, 1.1, 0.1)
        bins_idx = np.digitize(box_density, density_bins)
        distribution_list = []
        distributions = []
        for current_box_density in range(0, len(density_bins)-1):

            distributions.append(DistributionResults(analysis_results, bins_idx,
                                                     current_box_density, 'Back', scale))

            distributions.append(DistributionResults(analysis_results, bins_idx,
                                                     current_box_density, 'Front', scale))

            distributions.append(DistributionResults(analysis_results, bins_idx,
                                                     current_box_density, 'sides', scale))

            distributions = DistributionResults.calculate_exit_probabilities(distributions)
            distribution_list.append(distributions)
            distributions = []


class DistributionResults:

    def __init__(self, analysis_results, bins_indices, box_density, direction, scale):
        which_indices = [inds[0] for inds in enumerate(bins_indices) if inds[1] == box_density]
        relevant_density_analysis_results = [analysis_results[k] for k in which_indices]
        exit_direction = [i[3] for i in relevant_density_analysis_results]
        final_indices = [inds[0] for inds in enumerate(exit_direction) if inds[1] == direction]
        final_relevant_density_analysis_results = [relevant_density_analysis_results[k] for k in
                                                   final_indices]
        self.length_distribution = [i[2] for i in final_relevant_density_analysis_results]
        self.time_distribution = [i[4] for i in final_relevant_density_analysis_results]
        self.box_density = box_density
        self.direction = direction
        self.scale = scale
        self.exit_probability = None

    @staticmethod
    def calculate_exit_probabilities(object_list: list):
        assert len(object_list) == 3

        direction_list = [obj.direction for obj in object_list]
        sorted_direction_indices = [i[0] for i in sorted(enumerate(direction_list),
                                                         key=lambda x: x[1])]
        assert [direction_list[i] for i in sorted_direction_indices] == ['back', 'front', 'sides']

        object_list = [object_list[i] for i in sorted_direction_indices]
        lengths = [len(obj) for obj in object_list]
        sample_size = sum(lengths)
        [setattr(object_list[i], 'exit_probability', lengths[i]/sample_size)
         for i in range(0, len(object_list)-1)]
        return object_list

    def __len__(self):
        return len(self.length_distribution)


if __name__ == "__main__":
    scale_list = [2, 4, 6, 8, 10, 15, 20]
    results_dict = dict()
    for scale_size in scale_list:
        single_scale_analysis_list = []
        for file in misc.all_file_names():
            print(file)
            current_cfg = configuration.Configuration(file_name=file)
            NewBox = BoxAnalysis(scale_size, current_cfg, 'middle', False)
            NewBox.boxes_stats()
            single_scale_analysis_list.extend(NewBox.AnalysisResult)
            # run_movie(current_cfg, current_runner, only_save=True)
        BoxAnalysis.compute_statistics(single_scale_analysis_list, scale_size)
        results_dict[scale_size] = single_scale_analysis_list
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


