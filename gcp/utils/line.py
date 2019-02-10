from math import fabs
from gcp.utils.vector import *


def line_normal(a, b):
    return vec_normalize(vec_normal(vec_sub(a, b)))


def line_move_by_vec(line, n, o):
    mv = vec_mul(n, o)

    na = vec_add(line[0], mv)
    nb = vec_add(line[1], mv)
    return [na, nb]


def line_crossing_point(l1, l2):
    def line_crossing_vertical(vx, l):
        a = vec_sub(l[0], (vx, 0))
        b = vec_sub(l[1], (vx, 0))
        dv = vec_normalize(vec_sub(b, a))

        vy = a[1] + dv[1]*a[0]
        return vx, vy

    def line_crossing_vertical2(vx, l):
        a = vec_sub(l[0], (vx, 0))
        b = vec_sub(l[1], (vx, 0))
        dv = vec_normalize(vec_sub(b, a))

        vy = b[1] + dv[1] * b[0]
        return vx, vy

    # a = (y2 - y1)/(x2 - x1)
    # b = -a*x1 + y1

    dx1 = (l1[1][0] - l1[0][0])
    if dx1 == 0:
        return line_crossing_vertical(l1[0][0], l2)

    a1 = (l1[1][1] - l1[0][1])/dx1
    b1 = -a1*l1[0][0] + l1[0][1]

    dx2 = (l2[1][0] - l2[0][0])
    if dx2 == 0:
        return line_crossing_vertical2(l2[0][0], l1)

    a2 = (l2[1][1] - l2[0][1]) / dx2
    b2 = -a2 * l2[0][0] + l2[0][1]

    if fabs(a1 - a2) < 0.00000000001:
        return None

    cx = (b2 - b1)/(a1 - a2)
    cy = a1*cx + b1

    return cx, cy


def line_crossing_point2(l1, l2):
    def _is_point_on_line(l, p):
        return max(l[0][0], l[1][0]) >= p[0] >= min(l[0][0], l[1][0])

    cp = line_crossing_point(l1, l2)

    if cp and _is_point_on_line(l1, cp) and _is_point_on_line(l2, cp):
        return cp

    return None


def line_trim_lines(l1, l2):
    cp = line_crossing_point2(l1, l2)
    if cp:
        return [[l1[0], cp], [cp, l2[1]]]
    return [l1, l2]
