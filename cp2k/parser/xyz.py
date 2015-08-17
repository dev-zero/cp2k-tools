
import re

class XYZParserException(Exception):
    pass

class XYZParser:
    def parse(self, fh):
        frames = []

        while True:
            line = fh.readline().strip()

            if len(frames) > 0 and len(line) == 0:
                break

            # let the exception propagate for now
            noa = int(line)

            comment = fh.readline().strip()

            struct = {
                    'comment': comment,
                    'data': []
                    }

            for i in range(0, noa):
                m = re.match('^(?P<sym>[a-zA-Z0-9]+)\s+(?P<x>[\-]?\d+\.\d+)\s+(?P<y>[\-]?\d+\.\d+)\s+(?P<z>[\-]?\d+\.\d+)$', fh.readline().strip())

                if not m:
                    raise XYZParserException()

                struct['data'].append(( m.group('sym'), float(m.group('x')), float(m.group('y')), float(m.group('z')) ))

            frames.append(struct)

        return frames
