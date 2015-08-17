#!/usr/bin/env python3

"""Usage: extract_last_frame.py [-h] [XYZINPUT] [XYZOUTPUT]

Extract the last frame from a XYZ file

Arguments:
    XYZINPUT                  the XYZ file to read (otherwise stdin)
    XYZOUTPUT                 the XYZ file to write (otherwise stdout)

Options:
    -h --help

"""
from docopt import docopt

from cp2k.parser import XYZParser
from cp2k.generator import XYZGenerator
from cp2k.tools import smart_open

if __name__ == '__main__':
    arguments = docopt(__doc__)

    p = XYZParser()
    g = XYZGenerator()
    with smart_open(arguments['XYZINPUT'], 'r') as source:
        with smart_open(arguments['XYZOUTPUT'], 'w') as dest:
            g.write([p.parse(source)[-1]], dest)
