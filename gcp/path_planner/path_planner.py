import logging
from gcp.path_planner import LinePathShapePlanner
from gcp.path_planner import RectPathShapePlanner
from gcp.path_planner import CirclePathShapePlanner
from gcp.path_planner import ObroundPathShapePlanner
from gcp.shapes import ShapesCollection
from gcp.path_planner import ToolPath
from gcp.options import OptionKeys
import gcp.utils.vector as vector


class PathPlanner:
    def __init__(self):
        self._planners = []

    def init_default(self):
        self._planners.append(LinePathShapePlanner())
        self._planners.append(RectPathShapePlanner())
        self._planners.append(CirclePathShapePlanner())
        self._planners.append(ObroundPathShapePlanner())

    def plan_path_for_shapes(self, shapes: ShapesCollection, options):
        offset = options[OptionKeys.CNC_HOME_OFFSET]
        plot_z = options[OptionKeys.PATH_PLOT_Z]
        move_z = options[OptionKeys.PATH_MOVE_Z]
        max_speed = options[OptionKeys.PATH_MAX_SPEED]
        precise_speed = options[OptionKeys.PATH_PRECISE_SPEED]
        semi_precise_speed = options[OptionKeys.PATH_SEMI_PRECISE_SPEED]

        path = ToolPath(move_z, plot_z, offset, max_speed, precise_speed, semi_precise_speed)

        shape_pool = shapes.shapes.copy()

        def _get_nearest_shape():
            _neares_shape = shape_pool[0]
            _dist = vector.vec_dist2(_neares_shape.get_start_pos(), path.current_tool_pos())

            for shape in shape_pool:
                _new_dist = vector.vec_dist2(shape.get_start_pos(), path.current_tool_pos())
                if _new_dist < _dist:
                    _neares_shape = shape
                    _dist = _new_dist

            shape_pool.remove(_neares_shape)
            return _neares_shape

        while shape_pool:
            shape = _get_nearest_shape()
            self.plan_path_for_shape(shape, path, options)

        return path

    def plan_path_for_shape(self, shape, path, options):
        for planner in self._planners:
            if planner.can_handle(shape):
                logging.debug("Planning tool path: [planner: %s, shape: %s]", type(planner), type(shape))
                planner.plan_path(shape, path, options)
                return

        logging.warning("Unsupported shape for planning: %s", type(shape))
