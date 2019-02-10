from gcp.options import OptionKeys
from gcp.path_planner import ToolPath
from gcp.shapes import RectShape
import gcp.utils.vector as vector


class RectPathShapePlanner:
    @staticmethod
    def can_handle(shape):
        return type(shape) == RectShape

    @staticmethod
    def plan_path(shape: RectShape, path: ToolPath, options):
        tool_radius = options[OptionKeys.CNC_TOOL_RADIUS]
        path_overlap = options[OptionKeys.PATH_TOOL_MIN_OVERLAP]

        def border_offset(n):
            return (n+1)*tool_radius - n*path_overlap

        rec_size = vector.vec_sub(shape.upper_right, shape.lower_left)
        n = 0
        while True:
            cur_border_offset = border_offset(n)
            if cur_border_offset >= rec_size[0]/2 or cur_border_offset >= rec_size[1]/2:
                break

            RectPathShapePlanner._plan_rect(
                vector.vec_add_s(shape.lower_left, cur_border_offset),
                vector.vec_sub_s(shape.upper_right, cur_border_offset),
                path)

            n += 1
            path.plot_to(vector.vec_add_s(shape.lower_left, border_offset(n)))


    @staticmethod
    def _plan_rect(ll, ur, path: ToolPath):
        path.plot_line(ll, (ll[0], ur[1]))
        path.plot_line((ll[0], ur[1]), ur)
        path.plot_line(ur, (ur[0], ll[1]))
        path.plot_line((ur[0], ll[1]), ll)
