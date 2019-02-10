from gcp.path_planner import ToolPath
from gcp.options import OptionKeys


class GcodeGenerator:
    def __init__(self, gcode_translator):
        self._gcode_translator = gcode_translator

    def generate(self, path: ToolPath, options):
        gcode_str = self._gcode_translator.get_comment("-------- START GCODE --------")
        gcode_str += "\n"
        gcode_str += options[OptionKeys.GCODE_START].strip()
        gcode_str += "\n"

        gcode_str += self._gcode_translator.get_comment("-------- IMAGE GCODE --------")
        gcode_str += "\n"

        for cmd in path.commands:
            for line in self._gcode_translator.get_gcode(cmd, options) or []:
                gcode_str += line
                gcode_str += "\n"

        gcode_str += self._gcode_translator.get_comment("-------- END GCODE --------")
        gcode_str += "\n"
        gcode_str += options[OptionKeys.GCODE_END].strip()
        gcode_str += "\n"
        return gcode_str
