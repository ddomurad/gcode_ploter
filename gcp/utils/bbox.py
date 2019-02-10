def bbox_mk(p1, p2, offset=(0, 0)):
    x1 = min(p1[0], p2[0]) - offset[0]
    x2 = max(p1[0], p2[0]) + offset[0]

    y1 = min(p1[1], p2[1]) - offset[1]
    y2 = max(p1[1], p2[1]) + offset[1]

    return (x1, y1), (x2, y2)


def bbox_add_point(bbox, p, offset=(0, 0)):
    x1 = min(bbox[0][0], p[0] - offset[0])
    x2 = max(bbox[1][0], p[0] + offset[0])

    y1 = min(bbox[0][1], p[1] - offset[1])
    y2 = max(bbox[1][1], p[1] + offset[1])

    return (x1, y1), (x2, y2)


def bbox_add_bbox(b1, b2):
    bb = bbox_add_point(b1, b2[0])
    bb = bbox_add_point(bb, b2[1])
    return bb
