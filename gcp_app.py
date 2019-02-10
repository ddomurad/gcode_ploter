import logging
import gcp


logging.basicConfig(format="[%(levelname)s] %(message)s", level="INFO")

options = gcp.options.OptionsProvider.mk_example()

imp = gcp.importers.GeberImporter()

shape_collection = imp.load("./resources/test_pcb-F.Cu.gbr")
shape_collection.prepare(options)
logging.info("BOUNDARY: [%s]", shape_collection.get_bbox())

planner = gcp.path_planner.PathPlanner()
planner.init_default()
tool_path = planner.plan_path_for_shapes(shape_collection, options)

gcode_generator = gcp.gcode_generator.GcodeGenerator(gcp.gcode_generator.DefaultInterpolatedGcodeTranslator())
gcode_string = gcode_generator.generate(tool_path, options)

with open("out.gcode", "w") as out_file:
    out_file.write(gcode_string)
