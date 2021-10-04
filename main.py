import numpy as np
from matplotlib import pyplot as plt


def slope(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return (y2 - y1) / (x2 - x1)


def line(point1, point2):
    a = slope(point1, point2)
    b = -a * point1[0] + point1[1]
    return a, b


def upper_bound(point, gamma):
    return point[0], point[1] + gamma


def lower_bound(point, gamma):
    return point[0], point[1] - gamma


def intersection(l1, l2):
    a, c = l1
    b, d = l2
    return ((d - c) / (a - b)), ((a * d - b * c) / (a - b))


def above(point, line):
    return point[1] > line[0] * point[0] + line[1]


def below(point, line):
    return point[1] < line[0] * point[0] + line[1]


class GreedyPLR:

    def __init__(self, gamma):
        self.__state = "ready"
        self.__gamma = gamma

    def process(self, point):
        self.__last_point = point
        if self.__state == "ready":
            self.__p0 = point
            self.__state = "need"
        elif self.__state == "need":
            self.__p1 = point
            self.__setup()
            self.__state = "begin"
        elif self.__state == "begin":
            return self.__process(point)
        else:
            assert False

    def __setup(self):
        self.__lower = line(upper_bound(self.__p0, self.__gamma),
                            lower_bound(self.__p1, self.__gamma))
        self.__upper = line(lower_bound(self.__p0, self.__gamma),
                            upper_bound(self.__p1, self.__gamma))

        self.__intersection = intersection(self.__lower, self.__upper)

    def __current_segment(self):
        segment_start = self.__p0[0]
        segment_stop = self.__last_point[0]
        avg_slope = (self.__lower[0] + self.__upper[0]) / 2
        intercept = -avg_slope * self.__intersection[0] + self.__intersection[1]
        return segment_start, segment_stop, avg_slope, intercept

    def __process(self, point):
        if not (above(point, self.__lower) and below(point, self.__upper)):
            # we have to start a new segment.
            prev_segment = self.__current_segment()

            self.__p0 = point
            self.__state = "need"

            # return the previous segment
            return prev_segment

        s_upper = upper_bound(point, self.__gamma)
        s_lower = lower_bound(point, self.__gamma)
        if below(s_upper, self.__upper):
            self.__upper = line(self.__intersection, s_upper)
        if above(s_lower, self.__lower):
            self.__lower = line(self.__intersection, s_lower)
        return None

    def finish(self):
        if self.__state == "ready":
            self.__state = "finish"
            return None
        elif self.__state == "need":
            self.__state = "finish"
            return self.__p0[0], self.__p0[0] + 1, 0, self.__p0[1]
        elif self.__state == "begin":
            self.__state = "finish"
            return self.__current_segment()
        else:
            assert False


if __name__ == '__main__':
    x = np.linspace(0, 7, 1000)
    y = np.sin(x)
    data = list(zip(x, y))

    plr = GreedyPLR(0.0005)
    lines = []
    for point in data:
        l = plr.process(point)
        if l:
            lines.append(l)
    last = plr.finish()
    if last:
        lines.append(last)

    for l in lines:
        xl = np.linspace(l[0], l[1], 100)
        yl = l[2] * xl + l[3]
        plt.scatter(xl, yl)
    plt.show()
