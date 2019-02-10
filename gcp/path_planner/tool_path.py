from enum import Enum
import gcp.utils.vector as vector


class CncCommandTypes(Enum):
    NOP = 0
    QUICK_LINE_MOVE = 1
    SLOW_LINE_MOVE = 2
    SLOW_CW_CIRCLE_MOVE = 3
    SLOW_CW_ARC_MOVE = 4
    SLOW_CCW_ARC_MOVE = 5
    TOOL_UP = 6
    TOOL_DOWN = 7


class CncCommand:
    def __init__(self, cmd, params, speed, current_pos):
        self.cmd = cmd
        self.params = params
        self.speed = speed
        self.current_pos = current_pos


class ToolPath:
    def __init__(self, move_z, plot_z, cnc_offset, max_speed, precise_speed, semi_precise_speed):
        self.commands = []

        self._plot_z = plot_z + cnc_offset[2]
        self._move_z = move_z + cnc_offset[2]
        self._cnc_offset = cnc_offset
        self._max_speed = max_speed
        self._precise_speed = precise_speed
        self._semi_precise_speed = semi_precise_speed

        self._current_z = self._cnc_offset[2]
        self._current_pos = self._cnc_offset

    def current_tool_pos(self):
        return self._current_pos

    def move_to(self, p):
        p = vector.vec_add(p, self._cnc_offset)

        if p != self._current_pos:
            if self._current_z != self._move_z:
                self._append_tool_up_cmd()
            self._append_quick_move_cmd(p)

    def plot_line(self, p1, p2, fast=False):
        p1 = vector.vec_add(p1, self._cnc_offset)
        p2 = vector.vec_add(p2, self._cnc_offset)

        if p1 != self._current_pos:
            if self._current_z != self._move_z:
                self._append_tool_up_cmd()
            self._append_quick_move_cmd(p1)

        if self._current_z != self._plot_z:
            self._append_tool_down_cmd()

        self._append_precise_move_cmd(p2, fast)

    def plot_to(self, p, fast=False):
        p = vector.vec_add(p, self._cnc_offset)

        if p == self._current_pos:
            return

        if self._current_z != self._plot_z:
            self._append_tool_down_cmd()

        self._append_precise_move_cmd(p, fast)

    def plot_circle(self, center):
        center = vector.vec_add(center, self._cnc_offset)

        if self._current_z != self._plot_z:
            self._append_tool_down_cmd()

        self._append_slow_cw_circle_move(vector.vec_sub(center, self._current_pos), False)

    def plot_arc(self, r_center, stop, ccw):
        stop = vector.vec_add(stop, self._cnc_offset)

        if self._current_z != self._plot_z:
            self._append_tool_down_cmd()

        if ccw:
            self._append_ccw_slow_arc_cmd(r_center, stop, False)
        else:
            self._append_cw_slow_arc_cmd(r_center, stop, False)

    def _append_quick_move_cmd(self, pos):
        self.commands.append(CncCommand(CncCommandTypes.QUICK_LINE_MOVE, pos, self._max_speed, self._current_pos))
        self._current_pos = pos

    def _append_precise_move_cmd(self, pos, fast):
        self.commands.append(CncCommand(CncCommandTypes.SLOW_LINE_MOVE, pos, self._precise_speed if not fast else self._semi_precise_speed, self._current_pos))
        self._current_pos = pos

    def _append_slow_cw_circle_move(self, r_center, fast):
        self.commands.append(CncCommand(CncCommandTypes.SLOW_CW_CIRCLE_MOVE, r_center, self._precise_speed if not fast else self._semi_precise_speed, self._current_pos))

    def _append_cw_slow_arc_cmd(self, r_center, stop, fast):
        self.commands.append(CncCommand(CncCommandTypes.SLOW_CW_ARC_MOVE, (r_center, stop), self._precise_speed if not fast else self._semi_precise_speed, self._current_pos))
        self._current_pos = stop

    def _append_ccw_slow_arc_cmd(self, r_center, stop, fast):
        self.commands.append(CncCommand(CncCommandTypes.SLOW_CCW_ARC_MOVE, (r_center, stop), self._precise_speed if not fast else self._semi_precise_speed, self._current_pos))
        self._current_pos = stop

    def _append_tool_down_cmd(self):
        self.commands.append(CncCommand(CncCommandTypes.TOOL_DOWN, self._plot_z, self._max_speed, self._current_pos))
        self._current_z = self._plot_z

    def _append_tool_up_cmd(self):
        self.commands.append(CncCommand(CncCommandTypes.TOOL_UP, self._move_z, self._max_speed, self._current_pos))
        self._current_z = self._move_z

