from enum import Enum


class OptionKeys(Enum):
    GCODE_START = "start_gcode"
    GCODE_END = "end_gcode"

    CNC_HOME_OFFSET = "cnc_home_offset"
    CNC_TOOL_RADIUS = "cnc_tool_radius"

    PATH_MAX_SPEED = "cnc_max_feed_rate"
    PATH_PRECISE_SPEED = "cnc_precise_feed_rate"
    PATH_SEMI_PRECISE_SPEED = "cnc_semi_precise_feed_rate"

    PATH_FAST_LINE_LENGTH = "path_speedup_lines"
    PATH_FAST_LINE_WIDTH = "path_speedup_lwidth"
    PATH_MOVE_Z = "path_move_z"
    PATH_PLOT_Z = "path_plot_z"
    PATH_TOOL_MIN_OVERLAP = "path_tool_min_overlap"
    PATH_ARC_INTERPOLATION_ANGLE = "path_interpolation_angle"
    PATH_ENLARGE_SHAPES = "path_enlarge_shapes"
    PATH_ENLARGE_LINES_SHAPES = "path_enlarge_lines"


class OptionsProvider:
    @staticmethod
    def mk_example():
        return {
            OptionKeys.GCODE_START: "G21\nG91\nG0 Z14\nG90\nG28 X Y\nG28 Z\nG0 Z14",
            OptionKeys.GCODE_END: "G0 Z14\nG28 X\nG1 Y200",
            OptionKeys.CNC_HOME_OFFSET: [54, 62, 4], #[18, 56, 2.6],
            OptionKeys.CNC_TOOL_RADIUS: 0.25,
            OptionKeys.PATH_MAX_SPEED: 1500,
            OptionKeys.PATH_SEMI_PRECISE_SPEED: 1000,
            OptionKeys.PATH_PRECISE_SPEED: 500,
            OptionKeys.PATH_MOVE_Z: 0,
            OptionKeys.PATH_PLOT_Z: -2,
            OptionKeys.PATH_TOOL_MIN_OVERLAP: 0.05,
            OptionKeys.PATH_ARC_INTERPOLATION_ANGLE: 0.8,
            OptionKeys.PATH_FAST_LINE_LENGTH: 4,
            OptionKeys.PATH_FAST_LINE_WIDTH: 0.4,
            OptionKeys.PATH_ENLARGE_SHAPES: 0.4,
            OptionKeys.PATH_ENLARGE_LINES_SHAPES: 0
        }
