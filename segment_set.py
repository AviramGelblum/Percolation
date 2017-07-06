from misc import *
from point import P
from segment import S

class Segment_Set:

    def __init__(self, ss):
        self.ss = ss

    def intersect(self, s):
        for s1 in self.ss:
            if s.intersecting(s1):