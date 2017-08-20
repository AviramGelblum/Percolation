import configuration
import rectangle
import movie
import run
import path as path_class

class BoxAnalysis:

    def __init__(self, scale, cfg: configuration.Configuration, load_center_loc='middle',
                 draw=True):
        self.draw = draw
        self.cfg = cfg
        self.size = scale * self.cfg.cheerio_radius
        self.load_center_loc = load_center_loc

    @staticmethod
    def box_density(cfg: configuration.Configuration, box: rectangle.Rectangle):
        return cfg.stones.box_density(cfg.cheerio_radius, box)

    def index_condition(self, index):
        path = self.cfg.path.points
        if self.load_center_loc == 'middle':
            result = index < len(path) and \
                path[index].x < 1 - self.size and \
                self.size / 2 < path[index].y < 1 - self.size / 2
        elif self.load_center_loc == 'left':
            result = index < len(path) and \
                self.size / 2 < path[index].x > 1 - self.size / 2 and \
                self.size / 2 < path[index].y > 1 - self.size / 2
        else:
            raise ValueError('load_center_loc can only take the following values: \n\t middle, left')
        return result

    def boxes_stats(self):
        index = 0
        path = self.cfg.path.points
        result = []
        while index < len(path) and path[index].x < 1 - self.size:
            p = path[index]
            box = rectangle.Rectangle(p.x, p.y - self.size / 2, p.x + self.size, p.y + self.size
                                      / 2)
            r, ant_res = run.Run(run.AntRunner(self.cfg, index), containing_box=box).run()
            result.append(BoxAnalysis.box_density(self.cfg, box), ant_res, path_class.MotionPath(
                r).length())
            while index < len(path) and path[index].x < box.qx:
                index += 1
        return result


    def boxes(self, draw=True):
        if draw:
            movie_instance = movie.Movie()
            movie_instance.background([(self.cfg, "black")])
        index = 0
        path = self.cfg.path.points
        result = []

        while self.index_condition(index):
            p = path[index]
            box = rectangle.Rectangle(p.x, p.y - self.size / 2, p.x + self.size, p.y + self.size
                                      / 2)

            good = 0
            times = 10
            for i in range(times):
                self.cfg.start = p
                self.cfg.reset_runseed()
                r, sim_res = run.Run(run.SimulationRunner(self.cfg), containing_box=box).run()
                if sim_res:
                    good += 1
                if draw:
                    if sim_res:
                        color = "green"
                    else:
                        color = "black"
                    movie.background([(MotionPath(r), color)])

            r, ant_res = run.Run(run.AntRunner(cfg, index), containing_box=box).run()
            if draw:
                if ant_res:
                    color = "green"
                else:
                    color = "black"
                movie.background([(MotionPath(r), "blue")])
                box.add_text(
                    '{:.0f}%,{:.0f}%'.format(box_density(cfg, box) * 100, good / times * 100))
                movie.background([(box, color)])

            result.append((box_density(cfg, box), ant_res, good / times))
            while index < len(path) and path[index].x < box.qx:
                index += 1

        if draw:
            movie_instance.save_figure(cfg.file_name + "_boxes")
            movie_instance.close()
            # movie.just_draw()
        return result



    def all_boxes(size, dots=5):
        good = np.zeros(dots + 1)
        count = np.zeros(dots + 1)
        lengths = np.zeros(dots + 1)
        for file_name in misc.all_file_names():
            cfg = configuration.Configuration(file_name=file_name)
            for density, res, length in boxes_stats(cfg, size):
                index = density * dots
                length /= size * cfg.cheerio_radius
                misc.add_at_fractional_index(count, index, 1)
                if res:
                    misc.add_at_fractional_index(good, index, 1)
                    misc.add_at_fractional_index(lengths, index, length)
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
