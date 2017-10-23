
import jinja2 as j2

class CP2KInputGenerator:
    def write_input(self, fh):
        fh.write(self._t.render(self._c))

    def write_coords(self, fh):
        fh.write('{0}\n{1}\n'.format(
            len(self._c['atoms']),
            self._c['global']['project']
            ))

        for a in self._c['atoms']:
            fh.write('{symbol} {x} {y} {z}\n'.format(**a))

    def load_template(self, template):
        self._t = j2.Template(template)

    def load_config(self, config):
        self._c = config
