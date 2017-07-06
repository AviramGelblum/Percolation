from misc import *
from point import P
from circle import Circle
from segment import S
from polygon import Polygon
from region import Region
from general_region import GRegion
from polygon_set import PolygonSet
import movie


time_interval = 10

max_speed = 0.001
max_rotational_speed = max_speed
rect_x = 0.005
rect_y = 0.1
start = P(0.1, 0.9)
pull = P(0.5, 0.2)
g = 0.0001


class MovingStick:

    def __init__(self):
        self.rectangle = Polygon.rectangle(start, rect_x, rect_y)
        self.rotational_speed = 0
        self.linear_speed = P(0, 0)
        self.center = self.rectangle.center()

    def move(self):
        new_rect = self.rectangle.rotate(self.center, 2 * np.pi * self.rotational_speed)
        self.rectangle = new_rect.shift(self.linear_speed)
        self.center = self.rectangle.center()

    @staticmethod
    def calc_pull(p):
        return (pull - p).resize(g/4)

    def update_speeds(self):
        linear_pull = P(0, 0)
        rotational_pull = 0
        for p in self.rectangle.points:
            mine = MovingStick.calc_pull(p)
            linear_pull += mine
            dir = (p - self.center).perp()
            rotational_pull += (dir * mine) / (dir * dir)

        self.linear_speed += linear_pull
        self.rotational_speed += rotational_pull

        if self.linear_speed.norm() > max_speed:
            self.linear_speed = self.linear_speed.resize(max_speed)

        if self.rotational_speed > max_rotational_speed:
            self.rotational_speed = max_rotational_speed
        elif self.rotational_speed < -max_rotational_speed:
            self.rotational_speed = -max_rotational_speed

    def frame(self):
        res = [(self.rectangle, "red")]
        return res


def run():
    movie.background([(Circle(pull, 0.005), "black")])
    stick = MovingStick()
    frames = []
    for i in range(10000):
        stick.update_speeds()
        stick.move()
        frames.append(stick.frame())
    movie.run_animation(frames, time_interval)


run()