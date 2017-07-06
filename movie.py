from misc import *


class Movie:

    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect='equal', autoscale_on=False,xlim=(0, 1), ylim=(-0.05, 1.05))
        #self.cid = self.fig.canvas.mpl_connect('button_press_event', Movie.onclick)

    @staticmethod
    def onclick(event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

    def background(self, drawables):
        for d, color in drawables:
            d.draw(self.ax, color=color)

    def just_draw(self):
        self.figManager = plt.get_current_fig_manager()
        self.figManager.window.showMaximized()
        plt.show()

    def save_figure(self, file_name):
        self.figManager = plt.get_current_fig_manager()
        self.figManager.window.showMaximized()
        self.fig.savefig(file_name, bbox_inches='tight', dpi='figure')

    def close(self):
        self.fig.clear()

    @staticmethod
    def animate(current_frame, movie):
        clear = []
        for d, color in current_frame:
            clear += d.draw(movie.ax, color)
        return clear

    def run_animation(self, sequence, time_interval):
        self.anim = animation.FuncAnimation(self.fig, self.animate, sequence, fargs=[self], interval=time_interval, blit=True, repeat=True)
        self.just_draw()
