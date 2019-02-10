from math import sqrt


def vec_add(v1, v2):
    return v1[0]+v2[0], v1[1]+v2[1]


def vec_add_s(v1, k):
    return v1[0]+k, v1[1]+k


def vec_sub(v1, v2):
    return v1[0]-v2[0], v1[1]-v2[1]


def vec_sub_s(v1, k):
    return v1[0]-k, v1[1]-k


def vec_mul(v, k):
    return v[0]*k, v[1]*k


def vec_div(v, k):
    return v[0]/k, v[1]/k


def vec_length(v):
    return sqrt(v[0]*v[0] + v[1]*v[1])


def vec_length2(v):
    return v[0]*v[0] + v[1]*v[1]


def vec_dist(v1, v2):
    return vec_length(vec_sub(v1, v2))


def vec_dist2(v1, v2):
    return vec_length2(vec_sub(v1, v2))


def vec_normalize(v):
    length = vec_length(v)
    if length == 0:
        length = 0.000000000001
    return vec_div(v, length)


def vec_normal(v):
    return -v[1], v[0]

