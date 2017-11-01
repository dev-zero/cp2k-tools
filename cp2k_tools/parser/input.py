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

from collections import OrderedDict

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


CP2K_INP_GRAMMAR = Grammar(r"""
content  = ( cline / section )*

section = section_start section_content section_end

section_start = s* "&" sname (s+ value)? comment? nl
section_end = s* "&" end (s+ value)? comment? nl?
section_content = (kv / cline / section )*

kv = s* name s* unitspec? values? s* comment? nl

unitspec = unit s*
unit = "[" s* name s* "]"
values = (value s*)+
value = ~r"[A-Z0-9_\-\+\./\"\']+"i

name = ~r"[A-Z0-9_\-]+"i
end = ~r"END"i
sname = !end name

s = " " / "\t"
nl = "\r\n" / "\r" / "\n"

comment  = ~r"[#!].*"
cline = s* comment? nl
""")


class CP2KInput2Dict(NodeVisitor):
    def __init__(self, *args, **kwargs):
        super(CP2KInput2Dict, self).__init__(*args, **kwargs)
        self.grammar = CP2K_INP_GRAMMAR

    # anonymous nodes
    def generic_visit(self, node, visited_children):
        children = [vc for vc in visited_children if vc is not None]

        if len(children) == 1:  # unpack the child
            return children[0]

        return children if children else None


    def visit_content(self, _, visited_children):
        # we can't have duplicate sections on the toplevel
        # so we only have to filter comments here
        return OrderedDict([vc for vc in visited_children if vc is not None])


    def visit_section(self, node, visited_children):
        (name, param), entries, _ = visited_children

        content = OrderedDict()

        for child in entries:
            key, value = child

            # DEFAULT_KEYWORDs have to be treated differently since their first
            # name is actually not a key but already a parameter
            # TODO: add more sections with default parameters
            # TODO: maybe delay mangling key names until here
            if name == 'coord' and key not in ['scaled', 'unit']:
                if isinstance(value, tuple):
                    value = (key.title(),) + value
                else:
                    value = (key.title(), value)
                key = '*'

            # if the key already exists we got the same keyword/section multiple times
            if key in content:
                if isinstance(content[key], list):  # if it is already a list, simply append to it
                    content[key].append(value)
                else:  # if not, make it a list
                    content[key] = [content[key], value]
            else:  # and if the key does not exist, assign it
                content[key] = value


        if param is not None:
            content['_'] = param

        return (name, content)


    def visit_section_start(self, _, visited_children):
        _, _, name, value, _, _ = visited_children
        return (name, value)


    def visit_section_content(self, _, visited_children):
        if visited_children is None:
            # a section with no children should be an empty dict
            return []

        if isinstance(visited_children, tuple):
            # a single key/value tuple can be put directly into the list
            return [visited_children]

        return [vc for vc in visited_children if vc is not None]



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
        _, k, _, unit, values, _, _, _ = visited_children

        value = []

        if unit:
            value.append("[%s]" % unit)

        value += values if values else [None]  # handle lone keywords

        if len(value) == 1:
            value = value[0]
        else:
            value = tuple(value)

        return (k, value)


    def visit_values(self, _, values):
        return values


class CP2KInputParser:
    def __init__(self):
        self._parser = CP2KInput2Dict()

    def parse(self, fhandle):
        return self._parser.parse(fhandle.read())
