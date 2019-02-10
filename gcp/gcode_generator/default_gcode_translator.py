import logging
from gcp.path_planner import CncCommand
from gcp.path_planner import CncCommandTypes
from gcp.options import OptionKeys

import gcp.utils.vector as vector
from math import atan2, cos, sin, pi, fabs


class DefaultGcodeTranslator:

    @staticmethod
    def get_comment(comment):
        return ";" + comment

    @staticmethod
    def get_gcode(cmd: CncCommand, options):
        if cmd.cmd == CncCommandTypes.QUICK_LINE_MOVE:
            gc_str = "G0 X{:.2f} Y{:.2f} F{}".format(cmd.params[0], cmd.params[1], cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.SLOW_LINE_MOVE:
            gc_str = "G1 X{:.2f} Y{:.2f} F{}".format(cmd.params[0], cmd.params[1], cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.TOOL_UP:
            gc_str = "G0 Z{:.2f} F{}".format(cmd.params, cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.TOOL_DOWN:
            gc_str = "G0 Z{:.2f} F{}".format(cmd.params, cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.SLOW_CW_CIRCLE_MOVE:
            gc_str = "G2 I{:.2f} J{:.2f} F{}".format(cmd.params[0], cmd.params[1], cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.SLOW_CCW_ARC_MOVE:
            gc_str = "G3 I{:.2f} J{:.2f} X{:.2f} Y{:.2f} F{}".format(cmd.params[0][0], cmd.params[0][1], cmd.params[1][0], cmd.params[1][1], cmd.speed)
            return [gc_str]
        else:
            logging.warning("DefaultGcodeGenerator: Unsupported command: %s", cmd.cmd)


class DefaultInterpolatedGcodeTranslator:

    @staticmethod
    def get_comment(comment):
        return ";" + comment

    @staticmethod
    def get_gcode(cmd: CncCommand, options):
        if cmd.cmd == CncCommandTypes.QUICK_LINE_MOVE:
            gc_str = "G0 X{:.2f} Y{:.2f} F{}".format(cmd.params[0], cmd.params[1], cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.SLOW_LINE_MOVE:
            gc_str = "G1 X{:.2f} Y{:.2f} F{}".format(cmd.params[0], cmd.params[1], cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.TOOL_UP:
            gc_str = "G0 Z{:.2f} F{}".format(cmd.params, cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.TOOL_DOWN:
            gc_str = "G0 Z{:.2f} F{}".format(cmd.params, cmd.speed)
            return [gc_str]
        elif cmd.cmd == CncCommandTypes.SLOW_CW_CIRCLE_MOVE:
            output_code = []

            local_center = cmd.params
            circle_radius = vector.vec_length(local_center)
            start_alpha = atan2(-local_center[1], -local_center[0])
            interpolation_angle = options[OptionKeys.PATH_ARC_INTERPOLATION_ANGLE]
            interpolations_steps = int(2*pi/interpolation_angle)+1
            interpolation_angle = 2*pi / interpolations_steps

            for i in range(interpolations_steps+1):
                current_alpha = start_alpha + i*interpolation_angle
                c_x = cos(current_alpha)*circle_radius + local_center[0] + cmd.current_pos[0]
                c_y = -sin(current_alpha)*circle_radius + local_center[1] + cmd.current_pos[1]
                gc_str = "G1 X{:.2f} Y{:.2f} F{}".format(c_x, c_y, cmd.speed)
                output_code.append(gc_str)

            return output_code

        elif cmd.cmd == CncCommandTypes.SLOW_CCW_ARC_MOVE:
            local_center = cmd.params[0]
            local_angle_vector = vector.vec_sub(cmd.params[1], cmd.current_pos)
            arc_radius = vector.vec_length(local_center)

            start_alpha = atan2(-local_center[1], -local_center[0])
            end_alpha = atan2(local_angle_vector[1] - local_center[1], local_angle_vector[0] - local_center[0])
            delta_alpha = end_alpha - start_alpha
            if delta_alpha < 0:
                delta_alpha += 2*pi

            output_code = []

            interpolation_angle = options[OptionKeys.PATH_ARC_INTERPOLATION_ANGLE]
            interpolations_steps = int(fabs(delta_alpha) / interpolation_angle) + 1
            interpolation_angle = delta_alpha/interpolations_steps

            for i in range(interpolations_steps+1):
                current_alpha = start_alpha + i*interpolation_angle
                c_x = cos(current_alpha)*arc_radius + local_center[0] + cmd.current_pos[0]
                c_y = sin(current_alpha)*arc_radius + local_center[1] + cmd.current_pos[1]
                gc_str = "G1 X{:.2f} Y{:.2f} F{}".format(c_x, c_y, cmd.speed)
                output_code.append(gc_str)

            return output_code

            # gc_str = "G3 I{:.2f} J{:.2f} X{:.2f} Y{:.2f} F{}".format(cmd.params[0][0], cmd.params[0][1], cmd.params[1][0], cmd.params[1][1], cmd.speed)
            # return [gc_str]
        else:
            logging.warning("DefaultGcodeGenerator: Unsupported command: %s", cmd.cmd)
