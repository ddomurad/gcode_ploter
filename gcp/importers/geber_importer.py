import logging
import gerber
import gcp.shapes


class GeberImporter:
    def __init__(self):
        pass

    def load(self, path) -> gcp.shapes.ShapesCollection:
        geber_layer = gerber.read(path)
        return gcp.shapes.ShapesCollection(list(filter(None, [self._cvt_shape(geber_primitive) for geber_primitive in geber_layer.primitives])))

    def _cvt_shape(self, geber_primitive):
        if type(geber_primitive) == gerber.primitives.Line:
            logging.debug("Loading geber line: [start=%s, end=%s, width=%s]", geber_primitive.start, geber_primitive.end, geber_primitive.aperture.diameter)
            return gcp.shapes.LineShape(geber_primitive.start, geber_primitive.end, geber_primitive.aperture.diameter)
        elif type(geber_primitive) == gerber.primitives.Rectangle:
            logging.debug("Loading geber rect: [position=%s, size=[%s, %s]]", geber_primitive.position, geber_primitive.width, geber_primitive.height)
            return gcp.shapes.RectShape(geber_primitive.lower_left, geber_primitive.upper_right)
        elif type(geber_primitive) == gerber.primitives.Circle:
            logging.debug("Loading geber circle: [position=%s, radius=%s]", geber_primitive.position, geber_primitive.radius)
            return gcp.shapes.CircleShape(geber_primitive.position, geber_primitive.radius)
        elif type(geber_primitive) == gerber.primitives.Obround:
            logging.debug("Loading geber obround: [position=%s, width=%s, height=%s]", geber_primitive.position, geber_primitive.width, geber_primitive.height)
            is_horizontal = geber_primitive.orientation == 'horizontal'

            if is_horizontal:
                radius = geber_primitive.height/2
                size = geber_primitive.width - geber_primitive.height
            else:
                radius = geber_primitive.width/2
                size = geber_primitive.height - geber_primitive.width

            return gcp.shapes.ObroundShape(geber_primitive.position, radius, size, is_horizontal)
        else:
            logging.warning("Geber primitive not supported: %s", type(geber_primitive))
            return None
