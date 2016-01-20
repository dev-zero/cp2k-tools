
class XYZParser:
    @staticmethod
    def parse_iter(string):
        """Generates nested tuples for frames in XYZ files.

        Args:
            string: a string containing XYZ-structured text

        Yields:
            tuple: `(natoms, comment, atomiter)` for each frame
            in the XYZ data where `atomiter` is an iterator yielding a
            nested tuple `(symbol, (x, y, z))` for each entry.

        Raises:
            TypeError: If the number of atoms specified for the frame does not match
                the number of atom entries in the file.

        Examples:
            >>> print(len(list(XYZParser.parse_iter('''
            ... 5
            ... no comment
            ...  C         5.0000000000        5.0000000000        5.0000000000
            ...  H         5.6401052216        5.6401052216        5.6401052216
            ...  H         4.3598947806        4.3598947806        5.6401052208
            ...  H         4.3598947806        5.6401052208        4.3598947806
            ...  H         5.6401052208        4.3598947806        4.3598947806
            ... 5
            ... no comment
            ...  C         5.0000000000        5.0000000000        5.0000000000
            ...  H         5.6401902064        5.6401902064        5.6401902064
            ...  H         4.3598097942        4.3598097942        5.6401902063
            ...  H         4.3598097942        5.6401902063        4.3598097942
            ...  H         5.6401902063        4.3598097942        4.3598097942
            ... 5
            ... no comment
            ...  C         5.0000000000        5.0000000000        5.0000000000
            ...  H         5.6401902064        5.6401902064        5.6401902064
            ...  H         4.3598097942        4.3598097942        5.6401902063
            ...  H         4.3598097942        5.6401902063        4.3598097942
            ...  H         5.6401902063        4.3598097942        4.3598097942
            ... '''))))
            3
        """

        class BlockIterator(object):
            """
            An iterator for wrapping the iterator returned by `match.finditer`
            to extract the required fields directly from the match object
            """
            def __init__(self, it, natoms):
                self._it = it
                self._natoms = natoms
                self._catom = 0

            def __iter__(self):
                return self

            def __next__(self):
                try:
                    match = next(self._it)
                except StopIteration:
                    # if we reached the number of atoms declared, everything is well
                    # and we re-raise the StopIteration exception
                    if self._catom == self._natoms:
                        raise
                    else:
                        # otherwise we got too less entries
                        raise TypeError("Number of atom entries ({}) is smaller "
                            "than the number of atoms ({})".format(
                                self._catom, self._natoms))

                self._catom += 1

                if self._catom > self._natoms:
                    raise TypeError("Number of atom entries ({}) is larger "
                        "than the number of atoms ({})".format(
                            self._catom, self._natoms))

                return (
                    match.group('sym'),
                    (
                        float(match.group('x')),
                        float(match.group('y')),
                        float(match.group('z'))
                        ))

            def next(self):
                """
                The iterator method expected by python 2.x,
                implemented as python 3.x style method.
                """
                return self.__next__()

        import re

        pos_regex = re.compile(r"""
^                                                                             # Linestart
[ \t]*                                                                        # Optional white space
(?P<sym>[A-Za-z]+[A-Za-z0-9]*)\s+                                             # get the symbol
(?P<x> [\-|\+]?  ( \d*[\.]\d+  | \d+[\.]?\d* )  ([E | e][+|-]?\d+)? ) [ \t]+  # Get x
(?P<y> [\-|\+]?  ( \d*[\.]\d+  | \d+[\.]?\d* )  ([E | e][+|-]?\d+)? ) [ \t]+  # Get y
(?P<z> [\-|\+]?  ( \d*[\.]\d+  | \d+[\.]?\d* )  ([E | e][+|-]?\d+)? )         # Get z
""", re.X | re.M)
        pos_block_regex = re.compile(r"""
                                                            # First line contains an integer
                                                            # and only an integer: the number of atoms
^[ \t]* (?P<natoms> [0-9]+) [ \t]*[\n]                      # End first line
^[ \t]* (?P<comment>.*) [\n]                                # The second line is a comment
(?P<positions>                                              # This is the block of positions
    (
        (
            \s*                                             # White space in front of the element spec is ok
            (
                [A-Za-z]+[A-Za-z0-9]*                       # Element spec
                (
                   \s+                                      # White space in front of the number
                   [\- | \+ ]?                              # Plus or minus in front of the number (optional)
                    (\d*                                    # optional decimal in the beginning .0001 is ok, for example
                    [\.]                                    # There has to be a dot followed by
                    \d+)                                    # at least one decimal
                    |                                       # OR
                    (\d+                                    # at least one decimal, followed by
                    [\.]?                                   # an optional dot
                    \d*)                                    # followed by optional decimals
                    ([E | e][+|-]?\d+)?                     # optional exponents E+03, e-05
                ){3}                                        # I expect three float values
                |
                \#                                          # If a line is commented out, that is also ok
            )
            .*                                              # I do not care what is after the comment or the position spec
            |                                               # OR
            \s*                                             # A line only containing white space
         )
        [\n]                                                # line break at the end
    )+
)                                                           # A positions block should be one or more lines
                    """, re.X | re.M)

        for block in pos_block_regex.finditer(string):
            natoms = int(block.group('natoms'))
            yield (
                natoms,
                block.group('comment'),
                BlockIterator(
                    pos_regex.finditer(block.group('positions')),
                    natoms)
                )

    @staticmethod
    def parse(fh_or_string):
        if hasattr(fh_or_string, 'read'):
            s = fh_or_string.read()
        else:
            s = fh_or_string

        return [{ 'natoms': natoms,
                    'comment': comment,
                    'atoms': list(atomiter)
                    } for (natoms, comment,  atomiter) in XYZParser.parse_iter(s)]
