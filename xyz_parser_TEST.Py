#!/usr/bin/env python3

from cp2k.parser.xyz import XYZParser

p = XYZParser()

with open('CH4-pos-1.xyz', 'r') as f:
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(p.parse(f))
