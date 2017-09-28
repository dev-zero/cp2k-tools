#!/usr/bin/env python3
# vim: set fileencoding=utf-8 ts=8 sw=4 tw=0 :

# Copyright (c) 2017 Tiziano Müller <tiziano.mueller@chem.uzh.ch>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json

import click

from io import BufferedIOBase


def dict2line_iter(nested, ilevel=0):
    """
    Iterator to convert a nested python dict to a CP2K input file.
    """

    indent = ' '*ilevel

    def _keyfunc(keyval):
        """Custom sorting function to get stable CP2K output"""
        key, val = keyval

        # ensure subsection generating entrys are sorted after keywords
        if isinstance(val, dict) or isinstance(val, list):
            # .. by prefixing them with the last possible character before sorting
            return chr(0x10ffff) + key.lower()

        return key.lower()

    for key, val in sorted(nested.items(), key=_keyfunc):
        if isinstance(val, dict):
            if '_' in val:
                yield "{}&{} {}".format(indent, key.upper(), val.pop('_'))
            else:
                yield "{}&{}".format(indent, key.upper())

            for line in dict2line_iter(val, ilevel + 3):
                yield line

            yield "{}&END {}".format(indent, key.upper())

        elif isinstance(val, list):
            # here we have multiple sections (possibly with parameters)
            # and we are going to unfold them again (list of dicts case)
            if isinstance(val[0], dict):
                for listitem in val:
                    for line in dict2line_iter({key: listitem}, ilevel):
                        yield line
            # in the case of list of lists, unpack them as key/value lines
            elif isinstance(val[0], list):
                thiskey = key.upper()

                # if the start special key was used, drop the key completely
                if thiskey == '*':
                    thiskey = ''
                else:
                    thiskey += ' '

                for listitem in val:
                    yield "{}{}{}".format(indent, thiskey, ' '.join(str(v) for v in listitem))
            else:
                yield "{}{} {}".format(indent, key.upper(), ' '.join(str(v) for v in val))

        elif isinstance(val, tuple):
            yield "{}{} {}".format(indent, key.upper(),
                                   ' '.join(str(v) for v in val))

        elif isinstance(val, bool):
            yield "{}{} {}".format(
                indent, key.upper(),
                '.TRUE.' if val else '.FALSE.')

        else:
            yield "{}{} {}".format(indent, key.upper(), val)


def dict2cp2k(data, output=None, parameters={}):  # pylint: disable=locally-disabled, dangerous-default-value
    """
    Convert and write a nested python dict to a CP2K input file.

    Some of this code is either taken from AiiDA or heavily
    inspired from there.

    Writes to a file if a handle or filename is given
    or returns the generated file as a string if not.

    The parameters are passed to a .format() call on the final input string.
    """

    if output:
        if isinstance(output, str):
            with open(output, 'w') as fhandle:
                fhandle.write("\n"
                              .join(dict2line_iter(data))
                              .format(**parameters))
        elif isinstance(output, BufferedIOBase):
            # bytes-like object, need to encode
            output.write("\n"
                         .join(dict2line_iter(data))
                         .format(**parameters)
                         .encode('utf-8'))
        else:
            output.write("\n".join(dict2line_iter(data)))
    else:
        return ("\n"
                .join(dict2line_iter(data))
                .format(**parameters))


@click.command()
@click.argument('cp2k-json-file', type=click.File('r'))
def cli(cp2k_json_file):
    """Convert a CP2K JSON input to a native CP2K input file""" 
    struct = json.load(cp2k_json_file)
    click.echo(dict2cp2k(struct))


if __name__ == '__main__':
    cli()
