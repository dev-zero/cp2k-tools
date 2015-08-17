#!/usr/bin/env python3

from cp2k.parser.output import CP2KOutputParser

p = CP2KOutputParser()

with open('C4H4S_dft-only.out', 'r') as f:
    p.parse(f)
