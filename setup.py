#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from setuptools import setup, find_packages

version = '0.0.2'

description = "CP2K input/output mangling tools"
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.md')).read()
except:
    long_description = description

setup(
    name="cp2k-tools",
    version=version,
    url='http://github.com/dev-zero/cp2k-tools',
    license='GPL3',
    description=description,
    long_description=long_description,
    author=u'Tiziano Müller',
    author_email='tiziano.mueller@chem.uzh.ch',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'docopt',
        'parsimonious>=0.8',
        'click>=6.7',
        'regex>=2017.09.23',
        'numpy>=1.13.3',
        ],
    entry_points={
        'console_scripts': [
            'oq = cp2k_tools.cli:oq',
            'extract_last_frame = cp2k_tools.cli:extract_last_frame',
            'generate_input = cp2k_tools.cli:generate_input',
            'cp2k_inp2json = cp2k_tools.parser.input_cli:cli'
        ],
    },
    scripts=[
        'scripts/cp2k_bs2csv.py',
        'scripts/cp2k_json2inp.py',
        'scripts/cp2k_pdos.py',
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
