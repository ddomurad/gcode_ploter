from gcp.path_planner import ToolPath
from gcp.shapes import LinePathShape
from gcp.options import OptionKeys
import gcp.utils.vector as vector
import gcp.utils.line as line


class LinePathShapePlanner:
    @staticmethod
    def can_handle(shape):
        return type(shape) == LinePathShape

    @staticmethod
    def prepare_segments(segments, div_count):
        if div_count == 0 or len(segments) <= 1:
            return

        for div_no in range(div_count):
            prev_segment = segments[0]
            for next_segment in segments[1:]:
                prev_line = prev_segment['divs'][div_no]
                next_line = next_segment['divs'][div_no]

                new_prev_line, new_next_line = line.line_trim_lines(prev_line, next_line)
                prev_segment['divs'][div_no] = new_prev_line
                next_segment['divs'][div_no] = new_next_line

                prev_segment = next_segment

    @staticmethod
    def plan_path(shape: LinePathShape, path: ToolPath, options):
        segments = []

        prev_point = shape.points[0]
        tool_radius = options[OptionKeys.CNC_TOOL_RADIUS]
        min_overlap = options[OptionKeys.PATH_TOOL_MIN_OVERLAP]
        fast_line_length = options[OptionKeys.PATH_FAST_LINE_LENGTH]
        fast_line_width = options[OptionKeys.PATH_FAST_LINE_WIDTH]

        for next_point in shape.points[1:]:
            vec = vector.vec_sub(next_point, prev_point)
            segments.append({'orig_line': [prev_point, next_point], 'orig_vec': vec, 'orig_norm': vector.vec_normalize(vector.vec_normal(vec))})
            prev_point = next_point

        def _divide_segment(t_segment):
            def _get_offset(nn):
                return shape.width/2 - ((nn+1)*tool_radius - nn*min_overlap)

            t_segment['divs'] = []
            n = 0
            while True:
                curr_offset = _get_offset(n)
                if curr_offset < 0 and shape.width/2 <= -curr_offset:
                    #TODO add final pass to divs
                    break

                offset_line = line.line_move_by_vec(t_segment['orig_line'], t_segment['orig_norm'], curr_offset)
                t_segment['divs'].append(offset_line)
                n += 1

        def is_fast_line(p1, p2):
            return fast_line_width <= shape.width or vector.vec_dist(p1, p2) >= fast_line_length

        for segment in segments:
            _divide_segment(segment)

        divs_count = len(segments[0]['divs'])

        LinePathShapePlanner.prepare_segments(segments, divs_count)

        if not divs_count:
            for segment in segments:
                seg_line = segment['orig_line']
                path.plot_line(seg_line[0], seg_line[1], is_fast_line(seg_line[0], seg_line[1]))

        first_pass = True
        for div_no in range(divs_count):
            prev_segment = None
            tmp_segments = segments if div_no % 2 == 0 else reversed(segments)

            for segment in tmp_segments:
                div_line = segment['divs'][div_no]
                _is_fast_line = is_fast_line(div_line[0], div_line[1])

                if prev_segment:
                    if div_no % 2 == 0:
                        path.plot_line(prev_segment['divs'][div_no][1], div_line[0], _is_fast_line)
                    else:
                        path.plot_line(prev_segment['divs'][div_no][0], div_line[1], _is_fast_line)
                elif not first_pass:
                    if div_no % 2 == 0:
                        path.plot_to(segment['divs'][div_no][0], _is_fast_line)
                    else:
                        path.plot_to(segment['divs'][div_no][1], _is_fast_line)

                if div_no % 2 == 0:
                    path.plot_line(div_line[0], div_line[1], _is_fast_line)
                else:
                    path.plot_line(div_line[1], div_line[0], _is_fast_line)

                prev_segment = segment
            first_pass = False