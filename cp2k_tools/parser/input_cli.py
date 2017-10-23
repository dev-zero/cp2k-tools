#!/usr/bin/env python
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
import pprint

import click
from .input import CP2KInputParser


@click.command()
@click.argument('cp2k-input-file', type=click.File('r'))
@click.option('--python-output/--no-python-output', default=False,
              help="Yield prettified python output instead of json")
def cli(cp2k_input_file, python_output):
    """Convert a CP2K input file to a JSON representation as used in AiiDA and other.
    This is a proof-of-concept, using Parsimonious to implement a PEG-based parser."""
    parser = CP2KInputParser()
    data = parser.parse(cp2k_input_file)

    if python_output:
        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(data)
    else:
        click.echo(json.dumps(data, indent=4))


if __name__ == '__main__':
    cli()
