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

import click

from cp2k_tools.generator import dict2cp2k


@click.command()
@click.argument('cp2k-json-file', type=click.File('r'))
def cli(cp2k_json_file):
    """Convert a CP2K JSON input to a native CP2K input file"""
    struct = json.load(cp2k_json_file)
    click.echo(dict2cp2k(struct))
