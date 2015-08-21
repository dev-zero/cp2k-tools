#!/usr/bin/env python3

"""Usage: generate_inputs.py [-h] single TEMPLATE SNIPPET [OUTPUT COORDS]
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
from docopt import docopt

from cp2k.generator import CP2KInputGenerator
from cp2k.tools import smart_open
import sys

if __name__ == '__main__':
    arguments = docopt(__doc__)

    generator = CP2KInputGenerator()

    import os as o
    import glob as g
    import json as j

    with open(arguments['TEMPLATE'], 'r') as f:
        generator.load_template(f.read())

    if arguments['single']:
        with open(arguments['SNIPPET'], 'r') as f:
            generator.load_config(j.load(f))

        with smart_open(arguments['OUTPUT']) as f:
            generator.write_input(f)

        with smart_open(arguments['COORDS']) as f:
            generator.write_coords(f)

        sys.exit(0)

    for snippet in g.glob(o.path.join(arguments['SNIPPETDIR'], '*.json')):
        config = '{}'

        with open(snippet, 'r') as f:
            config = j.load(f)

        generator.load_config(config)

        target_dir = o.path.join(arguments['OUTPUTDIR'], config['global']['project'])
        target_filename = '%s.inp' % o.path.basename(snippet)[:-5]

        try:
            o.mkdir(target_dir)
        except FileExistsError:
            pass # ignore if directory already exists

        target_config_path = o.path.join(target_dir, target_filename)
        target_coord_path = o.path.join(target_dir, 'initial_coords.xyz')

        with open(target_config_path, 'w') as f:
            generator.write_input(f)

        with open(target_coord_path, 'w') as f:
            generator.write_coords(f)

        print('generating configuration for %s (in %s)' % (config['global']['project'], target_dir))
