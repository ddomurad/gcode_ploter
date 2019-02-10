import logging
import svgwrite
import gcp.shapes
import gcp.utils.vector as vector


class SvgExporter:
    def __init__(self):
        pass

    def save(self, path, shapes: gcp.shapes.ShapesCollection):
        logging.debug("Export shapes to SVG file: %s", path)
        dwg = svgwrite.Drawing(path, profile='tiny')

        for shape in shapes.shapes:
            if type(shape) == gcp.shapes.LineShape:
                dwg.add(dwg.line(shape.start, shape.end, stroke='black', stroke_width=shape.width))
            elif type(shape) == gcp.shapes.LinePathShape:
                prev_point = shape.points[0]
                for next_point in shape.points[1:]:
                    dwg.add(dwg.line(prev_point, next_point, stroke='black', stroke_width=shape.width))
                    prev_point = next_point
            elif type(shape) == gcp.shapes.RectShape:
                dwg.add(dwg.rect(shape.lower_left, vector.vec_sub(shape.upper_right, shape.lower_left)))
            elif type(shape) == gcp.shapes.CircleShape:
                dwg.add(dwg.circle(shape.center, shape.radius))
            else:
                logging.warning("Unsupported SVG export for type %s", type(shape))

        dwg.save()
