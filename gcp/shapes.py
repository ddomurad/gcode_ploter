import gcp.utils.vector as vector
import gcp.utils.bbox as bbox
from gcp.options import OptionKeys
import logging


class LineShape:
    def __init__(self, start, end, width):
        self.start = tuple(start)
        self.end = tuple(end)
        self.width = width

    def dbg_dump(self):
        logging.debug("LineDump: [start: %s, end: %s, width: %f]", self.start, self.end, self.width)

    def get_bbox(self):
        return bbox.bbox_mk(self.start, self.end, offset=(self.width, self.width))

    def translate(self, v):
        self.start = vector.vec_add(self.start, v)
        self.end = vector.vec_add(self.end, v)

    def get_start_pos(self):
        return self.start

    def enlarge(self, value):
        self.width += value/2


class LinePathShape:
    def __init__(self, points, width):
        self.points = points.copy()
        self.width = width

    def append_line(self, line):
        if not self.points:
            self.points.append(line.start)
            self.points.append(line.end)
        elif line.start not in self.points:
            self.points.append(line.start)
        else:
            self.points.append(line.end)

    def dbg_dump(self):
        logging.debug("LinePathDump: [points: %s, width: %f]", self.points, self.width)

    def get_bbox(self):
        new_bbox = bbox.bbox_mk(self.points[0], self.points[1], offset=(self.width, self.width))
        for point in self.points:
            new_bbox = bbox.bbox_add_point(new_bbox, point, offset=(self.width, self.width))

        return new_bbox

    def translate(self, v):
        for i in range(len(self.points)):
            self.points[i] = vector.vec_add(self.points[i], v)

    def get_start_pos(self):
        return self.points[0]

    def enlarge(self, value):
        self.width += value/2


class RectShape:
    def __init__(self, lower_left, upper_right):
        self.lower_left = tuple(lower_left)
        self.upper_right = tuple(upper_right)

    def dbg_dump(self):
        logging.debug("RectDump: [lower_left: %s, upper_right: %s]", self.lower_left, self.upper_right)

    def get_bbox(self):
        return bbox.bbox_mk(self.lower_left, self.upper_right)

    def translate(self, v):
        self.lower_left = vector.vec_add(self.lower_left, v)
        self.upper_right = vector.vec_add(self.upper_right, v)

    def get_start_pos(self):
        return self.lower_left

    def enlarge(self, value):
        self.lower_left = vector.vec_sub_s(self.lower_left, value/2)
        self.upper_right = vector.vec_add_s(self.upper_right, value/2)


class CircleShape:
    def __init__(self, center, radius):
        self.center = tuple(center)
        self.radius = radius

    def dbg_dump(self):
        logging.debug("CircleDump: [center: %s, radius: %s]", self.center, self.radius)

    def get_bbox(self):
        return bbox.bbox_mk(self.center, self.center, offset=(self.radius, self.radius))

    def translate(self, v):
        self.center = vector.vec_add(self.center, v)

    def get_start_pos(self):
        return vector.vec_add(self.center, (self.radius, 0))

    def enlarge(self, value):
        self.radius += value/2


class ObroundShape:
    def __init__(self, position, radius, size, horizontal):
        self.position = tuple(position)
        self.radius = radius
        self.size = size
        self.horizontal = horizontal

    def dbg_dump(self):
        logging.debug("ObroundDump: [position: %s, radius: %s, size: %s, orint: %s]", self.position, self.radius, self.size, 'horizontal' if self.horizontal else 'vertical')

    def get_bbox(self):
        if self.horizontal:
            return bbox.bbox_mk(self.position, self.position, offset=(self.radius, self.size/2))
        else:
            return bbox.bbox_mk(self.position, self.position, offset=(self.size / 2, self.radius))

    def translate(self, v):
        self.position = vector.vec_add(self.position, v)

    def get_start_pos(self):
        if self.horizontal:
            return vector.vec_add(self.position, (-self.size/2, self.radius))
        return vector.vec_add(self.position, (self.radius, self.size/2))

    def enlarge(self, value):
        self.radius += value/2


class ShapesCollection:
    def __init__(self, shapes=None):
        self.shapes = shapes or []

    def append(self, shape):
        self.shapes.append(shape)

    def dbg_dump(self):
        logging.debug("Shape collection debug dump")
        for shape in self.shapes:
            shape.dbg_dump()

    def get_bbox(self):
        if not self.shapes:
            return None

        new_bbox = self.shapes[0].get_bbox()

        for shape in self.shapes:
            new_bbox = bbox.bbox_add_bbox(new_bbox, shape.get_bbox())

        return new_bbox

    def translate(self, v):
        for shape in self.shapes:
            shape.translate(v)

    def remove_offset(self):
        shapes_bbox = self.get_bbox()
        self.translate(vector.vec_mul(shapes_bbox[0], -1))

    def optimize(self):
        self._concatenate_lines_into_paths()

    def enlarge_shapes(self, options):
        enlarge_value = options[OptionKeys.PATH_ENLARGE_SHAPES]
        enlarge_lines_value = options[OptionKeys.PATH_ENLARGE_LINES_SHAPES]

        for shape in self.shapes:
            if type(shape) == LinePathShape or type(shape) == LineShape:
                shape.enlarge(enlarge_lines_value)
            else:
                shape.enlarge(enlarge_value)

    def prepare(self, options):
        self.optimize()
        self.remove_offset()
        self.enlarge_shapes(options)

    def get_shapes_by_type(self, shape_type):
        return [shape for shape in self.shapes if type(shape) == shape_type]

    def _concatenate_lines_into_paths(self):
        logging.debug("Concatenate lines into paths")
        sorted_lines = {}
        optimized_paths = []

        for line_shape in self.get_shapes_by_type(LineShape):
            self.shapes.remove(line_shape)

            if not line_shape.width in sorted_lines:
                sorted_lines[line_shape.width] = []
            sorted_lines[line_shape.width].append(line_shape)

        logging.debug("Total lines %d", sum([len(lines) for lines in sorted_lines.values()]))
        logging.debug("Lines widths: %s", sorted_lines.keys())

        def pop_continuation(width, point):
            for line in sorted_lines[width]:
                if line.start == point or line.end == point:
                    sorted_lines[width].remove(line)
                    return line

        def get_new_cp(original_cp, p1, p2):
            if original_cp == p1:
                return p2
            return p1

        def optimization_pass(width):
            start_line = sorted_lines[width].pop()
            _optimized_path = [start_line]

            cp = start_line.start

            while True:
                next_line = pop_continuation(width, cp)
                if next_line:
                    _optimized_path.insert(0, next_line)
                    cp = get_new_cp(cp, next_line.start, next_line.end)
                else:
                    break

            cp = start_line.end
            while True:
                next_line = pop_continuation(width, cp)
                if next_line:
                    _optimized_path.append(next_line)
                    cp = get_new_cp(cp, next_line.start, next_line.end)
                else:
                    break

            optimized_paths.append(_optimized_path)

            return sorted_lines[width]

        for w in sorted_lines.keys():
            while optimization_pass(w):
                pass

        logging.debug("Total optimized paths %d", len(optimized_paths))
        for raw_path in optimized_paths:
            path_shape = LinePathShape([], raw_path[0].width)
            for line in raw_path:
                path_shape.append_line(line)

            self.shapes.append(path_shape)
