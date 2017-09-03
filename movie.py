import matplotlib.pyplot as plt
import matplotlib.animation as animation
from configuration import Configuration
from path import MotionPath
from rectangle import Rectangle
from circle import Circle
from typing import List, Tuple, Union
Drawables = List[Tuple[Union[Configuration, MotionPath, Rectangle, Circle], Union[dict, None]]]
# type definition


class Movie:
    """
    Creates animation of different types.
    """
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect='equal', autoscale_on=False, xlim=(0, 1))
        #self.cid = self.fig.canvas.mpl_connect('button_press_event', Movie.onclick)

    @staticmethod
    def onclick(event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

    def background(self, drawables: Drawables):
        """
        Create background image for the animation. The draw() method in configuration specifies
        drawing of a few objects: the cubes, shading around the cubes signalling where the load
        center cannot be, the real path of the load.
        :param drawables: list of (one) tuple containing (object to be drawn, string or dictionary
        defining color/s)
        :return: No output
        """

        for d, option_dict in drawables:
                d.draw(self.ax, option_dict)

    def just_draw(self):
        """Plotting without saving."""
        self.figManager = plt.get_current_fig_manager()
        self.figManager.window.showMaximized()
        plt.show()

    def save_figure(self, file_name):
        """Plotting and Saving"""
        self.figManager = plt.get_current_fig_manager()
        self.figManager.window.showMaximized()
        self.fig.savefig(file_name, bbox_inches='tight', dpi='figure')

    def close(self):
        self.fig.clear()

    @staticmethod
    def animate(to_draw_in_current_frame, movie):
        """
        Function input into FuncAnimation in run_animation(). Receives the current drawables - a
        circle representing the load and the color. Returns

        :param to_draw_in_current_frame: The current drawables to be drawn in each frame,
        list of tuples of (object with defined draw() method, color)
        :param movie: self - to take the axis in which we plot the current frame in the animation.
        :return: list of objects drawn
        """
        clear = []
        for d, colordict in to_draw_in_current_frame:
            clear += d.draw(movie.ax, colordict)
        return clear

    def run_animation(self, to_draw_in_current_frame, time_interval):
        """Run FuncAnimation function to create animation of the load within the cube maze."""
        anim = animation.FuncAnimation(self.fig, self.animate, to_draw_in_current_frame,
                                       fargs=[self], interval=time_interval, blit=True)
        # repeat=True
        self.just_draw()  # show plot
