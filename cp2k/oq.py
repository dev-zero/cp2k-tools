#!/usr/bin/env python3

"""Usage: oq.py [-hj] [-f FILE] QUERY

Extract data from cp2k output

Options:
    -h --help
    -f --file=FILE    cp2k output file to read [default: -]
    -j --json         produce JSON output instead of pretty printed python objects

"""
from docopt import docopt

from cp2k.parser import CP2KOutputParser
from cp2k.tools import smart_open

if __name__ == '__main__':
    arguments = docopt(__doc__)

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
