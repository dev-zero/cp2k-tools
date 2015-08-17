
class XYZGenerator:
    def write(self, data, fh):
        for frame in data:
            fh.write('%8i\n' % len(frame['data']))
            fh.write(' %s\n' % frame['comment'])
            for atom in frame['data']:
                fh.write(' %2s %20.10f%20.10f%20.10f\n' % atom)
