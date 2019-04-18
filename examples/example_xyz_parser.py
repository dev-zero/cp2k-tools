#!/usr/bin/env python3

from cp2k_tools.parser import XYZParser

if __name__ == '__main__':

    f = open('tests/test_xyz_parser-simple_multiframe_file.xyz', 'r')
    s = f.read()

    print("\nprint them all")
    print("==============")
    frame_nr = 0
    for (natoms, comment, atomiter) in XYZParser.parse_iter(s):
        frame_nr += 1
        print("Frame {:0>4d} => natoms : {}, comment : '{}'".format(frame_nr, natoms, comment))
        for (sym, (x, y, z)) in atomiter:
            print("  {}: {: >30.20f} {:>30.20f} {:>30.20f}".format(sym, x, y, z))
    print("")

    print("get to the last frame as a tuple")
    print("================================")
    for last in XYZParser.parse_iter(s):
        pass
    print(last)
    print("")

    print("get to the last frame but unpacked")
    print("==================================")
    for (last_natoms, last_comment, last_atomiter) in XYZParser.parse_iter(s):
        pass
    print(last_natoms, last_comment, last_atomiter)
    print("")

