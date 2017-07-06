import numpy as np
import matplotlib.pyplot as plt


class Plots:

    def __init__(self):
        fig = plt.figure()
        self.ax = plt.axes()

    def add_plot(self, x, y, label=None):
        self.ax.plot(x, y, label=label)

    def show(self):
        plt.legend(loc='best')
        plt.show()
