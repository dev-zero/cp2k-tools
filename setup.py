#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import os
from setuptools import setup, find_packages

version = '0.0.1'

description = "CP2K input/output mangling tools"
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.md')).read()
except:
    long_description = description

setup(
    name = "cp2k-tools",
    version = version,
    url = 'http://github.com/dev-zero/cp2k-tools',
    license = 'GPL3',
    description = description,
    long_description = long_description,
    author = u'Tiziano Müller',
    author_email = 'tiziano.mueller@chem.uzh.ch',
    packages = find_packages(),
    install_requires = ['setuptools', 'docopt'],
    entry_points = {
        'console_scripts': [
            'oq = cp2k.oq:main',
            'extract_last_frame = cp2k.extract_last_frame:main',
            'generate_input = cp2k.generate_input:main',
        ],
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
