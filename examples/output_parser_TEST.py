#!/usr/bin/env python3

from cp2k.parser.output import CP2KOutputParser

p = CP2KOutputParser()

with open(os.path.join(os.path.dirname(__file__), "C4H4S_dft-only.out"), "r") as fhandle:
    p.parse(f)
