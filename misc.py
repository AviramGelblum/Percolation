import numpy as np
import os

import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import matplotlib.lines as lines
from typing import List
from scipy.stats import norm
import scipy as sc
import scipy.stats as sct


def init_rand(seed=None):
    """Return random seed if seed is not defined. Seed the RNG"""
    if not seed:
        seed = np.random.random_integers(1000000)
    np.random.seed(seed)
    return seed


def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0


def rand():
    return np.random.random()


all_colors = ["silver", "yellow", "orange", "violet", "beige", "brown", "cadetblue", "blue"]
color_num = 0


def random_color():
    global color_num
    color_num += 1
    color_num %= len(all_colors)
    return all_colors[color_num]


def remember(func):
    """
    A decorator to make an argument-less method run only once and remember the
    result so that it will not run again. Efficiency improvement trick.
    """
    cache = "cache" + func.__name__  # cache the name of the function to be remembered by the
    # resulting object.

    def new_func(s):
        """
        New function returned by the remember decorator, s is the object on which the
        remember-decorated method is called.
        """
        try:
            # returns cached value in s.cache+func.__name__. If it does not exist throws an
            # AttributeError
            return getattr(s, cache)
        except AttributeError:
            # Computes the value for the given object with the original method function,
            # setting s.cache+func.__name__ to this value, and returns said value.
            setattr(s, cache, func(s))
            return getattr(s, cache)
    return new_func


def most(item_list, func):
    best = None
    best_val = None
    for item in item_list:
        val = func(item)
        if not best_val or val > best_val:
            best = item
            best_val = val
    return best, best_val


def pairs(l):
    """Iterate over a list of length l, yielding two points at a time"""
    for i in range(int(len(l) / 2)):
        yield l[2*i], l[2*i+1]


def all_file_names():
    for file_name in os.listdir(os.getcwd() + "/data"):
        if file_name[-4:] == ".txt" and len(file_name) == 11:
            yield file_name[:-4]


def file_names_by_density(density):
    density2filename = {100: ['1110004', '1110006', '1110008', '1150001', '1150003', '1150004',
                              '1150006', '1150007', '1150008', '1150010'],
                        200: ['1260001'],
                        225: ['1400008'],
                        250: ['1380012'],
                        275: ['1410003'],
                        300: ['1350003']}
    for i in density2filename[density]:
        yield i


def add_at_fractional_index(a, index, value):
    index1 = int(index)
    index2 = index1 + 1
    weight1 = 1 - (index - index1)
    weight2 = 1 - weight1
    if weight1:
        a[index1] += value * weight1
    if weight2:
        a[index2] += value * weight2
