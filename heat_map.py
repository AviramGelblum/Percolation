from circle import Circle
from point import P
from math import sqrt


class HeatMap:
    def __init__(self, dx=0.0025):
        self.dx = dx
        self.n = int(1 / dx) + 1
        self.heat = [[0] * self.n for i in range(self.n)]

    def __iter__(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.heat[i][j]:
                    yield i, j, self.heat[i][j]

    def add_to_map(self, points, uniquely=False):
        points = [(int(p.x / self.dx), int(p.y / self.dx)) for p in points]
        if uniquely:
            points = set(points)
        for x, y in points:
            self.heat[x][y] += 1

    def save_map(self, file_name):
        f = open(file_name, 'w')
        for i, j, h in self:
            f.write("{:d},{:d},{:d}\n".format(i, j, h))
        f.close()

    def read_map(self, file_name):
        f = open(file_name, 'r')
        for line in f:
            i, j, h = [int(x) for x in line.split(',')]
            self.heat[i][j] += h
        f.close()

    def diffuse(self):
        temp = [[0] * self.n for i in range(self.n)]

        def fix(index):
            if index < 0:
                index = 0
            elif index >= self.n:
                index = self.n
            return index

        def add_to_temp(i, j, amount):
            temp[fix(i)][fix(j)] += amount

        for i, j, h in self:
            for i1 in range(i-1,i+1):
                for j1 in range(j-1,j+1):
                    add_to_temp(i1, j1, h/9)
            add_to_temp(i, j, h)

        self.heat = temp

    def to_draw(self):
        self.diffuse()
        res = []
        m = max(h for i, j, h in self)
        for i, j, h in self:
            x, y = i * self.dx, j * self.dx
            strength = sqrt(h+1)/sqrt(m+1) * 3
            strength = max(0, min(strength, 1))
            strength = 1 - strength
            color = (strength, strength, strength)
            res.append((Circle(P(x, y), self.dx), color))
        return res
