from gcp.options import OptionKeys
from gcp.path_planner import ToolPath
from gcp.shapes import CircleShape
import gcp.utils.vector as vector


class CirclePathShapePlanner:
    @staticmethod
    def can_handle(shape):
        return type(shape) == CircleShape

    @staticmethod
    def plan_path(shape: CircleShape, path: ToolPath, options):
        tool_radius = options[OptionKeys.CNC_TOOL_RADIUS]
        path_overlap = options[OptionKeys.PATH_TOOL_MIN_OVERLAP]

        def border_offset(nn):
            return (nn+1)*tool_radius - nn*path_overlap

        n = 0
        while True:
            cur_border_offset = border_offset(n)
            if cur_border_offset >= shape.radius:
                break

            CirclePathShapePlanner._plan_circle(
                shape.center, shape.radius-cur_border_offset, path, n == 0)

            n += 1

    @staticmethod
    def _plan_circle(center, radius, path: ToolPath, move_to_pos):
        border_pos = vector.vec_sub(center, (radius, 0))
        if move_to_pos:
            path.move_to(border_pos)
        else:
            path.plot_to(border_pos)

        path.plot_circle(center)
