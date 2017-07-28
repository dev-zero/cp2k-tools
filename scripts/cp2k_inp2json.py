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

import pprint
import json

import click

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import dpath

CP2K_INP_GRAMMAR = Grammar(r"""
content  = line*
line = s* instruction? s* comment? s* "\n"?

instruction = section_end / section_start / kv

section_end = "&END" s+ name
section_start = "&" name (s+ value)?
kv = name s* unitspec? values? s* comment?

unitspec = unit s*
unit = "[" s* name s* "]"
values = (value s*)+
value = ~"[A-Z0-9_\-\+\./]+"i

name = ~"[A-Z0-9_\-]+"i

s = ~"[ \t]"

comment  = ~"\#.*"
""")


class CP2KInput2Dict(NodeVisitor):
    def __init__(self, *args, **kwargs):
        super(CP2KInput2Dict, self).__init__(*args, **kwargs)
        self.grammar = CP2K_INP_GRAMMAR
        self._data = {"root": {}}
        self._sections = ["root"]

    # anonymous nodes
    def generic_visit(self, node, visited_children):
        children = [vc for vc in visited_children if vc is not None]

        if len(children) == 1:  # unpack the child
            return children[0]

        return children if children else None

    def visit_content(self, node, _):
        return self._data['root']

    def visit_section_start(self, _, visited_children):
        _, name, value = visited_children

        dpath.util.get(self._data, self._sections)[name] = {}
        self._sections.append(name)

        if value:
            dpath.util.get(self._data, self._sections)['_'] = value

    def visit_section_end(self, _, visited_children):
        _, _, name = visited_children
        current = self._sections.pop()

        if current != name:
            print("uh, oh, closing wrong section")

    def visit_name(self, node, _):
        return node.text.lower()

    def visit_value(self, node, _):
        value = node.text

        try:
            return int(value)
        except:
            pass

        try:
            return float(value)
        except:
            pass

        return node.text

    def visit_unit(self, _, visited_children):
        _, _, name, _, _ = visited_children
        return name

    def visit_unitspec(self, _, visited_children):
        unit, _ = visited_children
        return unit

    def visit_kv(self, _, visited_children):
        k, _, unit, values, _, _ = visited_children

        value = []

        if unit:
            value.append("[%s]" % unit)

        value += values

        if len(value) == 1:
            value = value[0]
        else:
            value = tuple(value)

        dpath.util.get(self._data, self._sections).update({k: value})
        return None  # we don't really use that return value


    def visit_values(self, _, values):
        return values


@click.command()
@click.argument('cp2k-input-file', type=click.File('r'))
@click.option('--python-output/--no-python-output', default=False,
              help="Yield prettified python output instead of json")
def cli(cp2k_input_file, python_output):
    """Convert a CP2K input file to a JSON representation as used in AiiDA and other.
    This is a proof-of-concept, using Parsimonious to implement a PEG-based parser."""
    converter = CP2KInput2Dict()
    data = converter.parse(cp2k_input_file.read())

    if python_output:
        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(data)
    else:
        click.echo(json.dumps(data, sort_keys=True, indent=4))


if __name__ == '__main__':
    cli()
