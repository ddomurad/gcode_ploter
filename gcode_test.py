import gcp

options = gcp.options.OptionsProvider.mk_example()
offset = options[gcp.options.OptionKeys.CNC_HOME_OFFSET]
plot_z = options[gcp.options.OptionKeys.PATH_PLOT_Z]
move_z = options[gcp.options.OptionKeys.PATH_MOVE_Z]
max_speed = options[gcp.options.OptionKeys.PATH_MAX_SPEED]
precise_speed = options[gcp.options.OptionKeys.PATH_PRECISE_SPEED]

shapes = gcp.shapes.ShapesCollection()
shapes.shapes.append(gcp.shapes.ObroundShape((80, 80), 2, 3, True))

planner = gcp.path_planner.PathPlanner()
planner.init_default()
path = planner.plan_path_for_shapes(shapes, options)
# path = gcp.path_planner.ToolPath(move_z, plot_z, offset, max_speed, precise_speed)
# generator = gcp.gcode_generator.GcodeGenerator(gcp.gcode_generator.DefaultGcodeTranslator())
generator = gcp.gcode_generator.GcodeGenerator(gcp.gcode_generator.DefaultInterpolatedGcodeTranslator())
gcode = generator.generate(path, options)


with open("gcode.gcode", "w") as out_file:
    out_file.write(gcode)
