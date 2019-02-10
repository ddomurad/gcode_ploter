from gcp.options import OptionKeys
from gcp.path_planner import ToolPath
from gcp.shapes import ObroundShape
import gcp.utils.vector as vector


class ObroundPathShapePlanner:
    @staticmethod
    def can_handle(shape):
        return type(shape) == ObroundShape

    @staticmethod
    def plan_path(shape: ObroundShape, path: ToolPath, options):
        tool_radius = options[OptionKeys.CNC_TOOL_RADIUS]
        path_overlap = options[OptionKeys.PATH_TOOL_MIN_OVERLAP]

        def border_offset(nn):
            return (nn+1)*tool_radius - nn*path_overlap

        n = 0
        while True:
            cur_border_offset = border_offset(n)
            if cur_border_offset >= shape.radius:
                break

            if shape.horizontal:
                ObroundPathShapePlanner._plan_horizontal_obround(
                    shape.position, shape.radius-cur_border_offset, shape.size, path, n == 0)
            else:
                ObroundPathShapePlanner._plan_vertical_obround(
                    shape.position, shape.radius - cur_border_offset, shape.size, path, n == 0)

            n += 1

    @staticmethod
    def _plan_horizontal_obround(position, radius, size, path: ToolPath, move_to_pos):
        border_pos_1 = vector.vec_add(position, (-size/2, radius))
        border_pos_2 = vector.vec_add(position, (-size/2, -radius))
        border_pos_3 = vector.vec_add(position, (size/2, -radius))
        border_pos_4 = vector.vec_add(position, (size/2, radius))

        if move_to_pos:
            path.move_to(border_pos_1)
        else:
            path.plot_to(border_pos_1)

        path.plot_arc((0, -radius), border_pos_2, True)
        path.plot_to(border_pos_3)
        path.plot_arc((0, radius), border_pos_4, True)
        path.plot_to(border_pos_1)

    @staticmethod
    def _plan_vertical_obround(position, radius, size, path: ToolPath, move_to_pos):
        border_pos_1 = vector.vec_add(position, (radius, size/2))
        border_pos_2 = vector.vec_add(position, (-radius, size/2))
        border_pos_3 = vector.vec_add(position, (-radius, -size/2))
        border_pos_4 = vector.vec_add(position, (radius, -size/2))

        if move_to_pos:
            path.move_to(border_pos_1)
        else:
            path.plot_to(border_pos_1)

        path.plot_arc((-radius, 0), border_pos_2, True)
        path.plot_to(border_pos_3)
        path.plot_arc((radius, 0), border_pos_4, True)
        path.plot_to(border_pos_1)
