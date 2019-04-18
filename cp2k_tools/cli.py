#!/usr/bin/env python

from cp2k_tools.tools import *
from cp2k_tools.parser import *
from cp2k_tools.generator import *
import sys
from docopt import docopt


def extract_last_frame():
    """Usage: extract_last_frame.py [-h] [XYZINPUT] [XYZOUTPUT]

Extract the last frame from a XYZ file

Arguments:
    XYZINPUT                  the XYZ file to read (otherwise stdin)
    XYZOUTPUT                 the XYZ file to write (otherwise stdout)

Options:
    -h --help

"""

    arguments = docopt(extract_last_frame.__doc__)

    p = XYZParser()
    g = XYZGenerator()
    with smart_open(arguments['XYZINPUT'], 'r') as source:
        with smart_open(arguments['XYZOUTPUT'], 'w') as dest:
            g.write([p.parse(source)[-1]], dest)


def generate_inputs():
    """Usage: generate_inputs.py [-h] single TEMPLATE SNIPPET [OUTPUT] [COORDS]
       generate_inputs.py [-h] batch TEMPLATE SNIPPETDIR OUTPUTDIR

Use the configuration in SNIPPET/SNIPPETDIR to generate cp2k input files
based on the template.

Arguments:
    TEMPLATE                  the template to use for generating the input files
    SNIPPET                   a single json file
    SNIPPETDIR                a directory with json files
    OUTPUT                    the output file (otherwise standard output)
    COORDS                    the coordinates output file (otherwise standard output)
    OUTPUTDIR                 where to create the project directories

Options:
    -h --help

"""

    arguments = docopt(generate_inputs.__doc__)

    generator = CP2KInputGenerator()

    import os
    import json
    from glob import glob

    with open(arguments['TEMPLATE'], 'r') as f:
        generator.load_template(f.read())

    if arguments['single']:
        with open(arguments['SNIPPET'], 'r') as f:
            generator.load_config(json.load(f))

        with smart_open(arguments['OUTPUT']) as f:
            generator.write_input(f)

        with smart_open(arguments['COORDS']) as f:
            generator.write_coords(f)

        sys.exit(0)

    for snippet in glob(os.path.join(arguments['SNIPPETDIR'], '*.json')):
        config = '{}'

        with open(snippet, 'r') as f:
            config = json.load(f)

        generator.load_config(config)

        target_dir = os.path.join(arguments['OUTPUTDIR'],
                                  config['global']['project'])
        target_filename = '%s.inp' % os.path.basename(snippet)[:-5]

        try:
            os.mkdir(target_dir)
        except FileExistsError:
            pass  # ignore if directory already exists

        target_config_path = os.path.join(target_dir, target_filename)
        target_coord_path = os.path.join(target_dir, 'initial_coords.xyz')

        with open(target_config_path, 'w') as f:
            generator.write_input(f)

        with open(target_coord_path, 'w') as f:
            generator.write_coords(f)

        print('generating configuration for %s (in %s)' %
              (config['global']['project'], target_dir))


def cp2kparse():
    """Usage: cp2kparse.py [-hj] [-f FILE]

Parse cp2k output.

Options:
    -h --help
    -f --file=FILE    cp2k output file to read [default: -]
    -j --json         produce JSON output instead of pretty printed python objects

"""

    arguments = docopt(cp2kparse.__doc__)

    p = CP2KOutputBlockParser()
    with smart_open(arguments['--file'], 'r') as fh:
        out = p.parse(fh.read())
        if arguments['--json']:
            import json
            print(json.dumps(out))
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(out)


def oq():
    """Usage: oq.py [-hj] [-f FILE] QUERY

Extract data from cp2k output. The syntax is similar to that of the jq tool.

Options:
    -h --help
    -f --file=FILE    cp2k output file to read [default: -]
    -j --json         produce JSON output instead of pretty printed python objects

"""

    arguments = docopt(oq.__doc__)

    p = CP2KOutputParser()
    with smart_open(arguments['--file'], 'r') as fh:
        p.parse(fh)
        if arguments['--json']:
            import json
            print(json.dumps(p.query(arguments['QUERY'])))
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(p.query(arguments['QUERY']))


if __name__ == '__main__':
    sys.argv = sys.argv[1:]
    import cp2k_tools.cli
    getattr(cp2k_tools.cli, sys.argv[0])()
