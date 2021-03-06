#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
from os.path import join as pjoin


from setupbase import (
    create_cmdclass, install_npm, ensure_targets,
    find_packages, combine_commands, ensure_python,
    get_version, HERE
)

from setuptools import setup


# The name of the project
name = 'nanohubtools'

# Ensure a valid python version
ensure_python('>=3.3')

# Get our version
version = get_version(pjoin(name, '_version.py'))

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = {
    'name'            : name,
    'description'     : 'A set of tools to run nanoHubtools',
    'long_description_content_type' : 'text/markdown',
    'long_description':long_description,
    'version'         : version,
    'scripts'         : glob(pjoin('scripts', '*')),
    'packages'        : find_packages(),
    'data_files'      : [('assets', [
                            'nanohubtools/assets/crystal1.png',
                            'nanohubtools/assets/crystal2.png',
                            'nanohubtools/assets/crystal3.png',
                            'nanohubtools/assets/crystal4.png',
                            'nanohubtools/assets/crystal5.png',
                            'nanohubtools/assets/crystal6.png',
                            'nanohubtools/assets/crystal7.png',
                            'nanohubtools/assets/crystal8.png',
                            'nanohubtools/assets/crystal9.png',
                            'nanohubtools/assets/crystal10.png',
                            'nanohubtools/assets/crystal11.png',
                            'nanohubtools/assets/crystal12.png',
                            'nanohubtools/assets/bravais1.png',
                            'nanohubtools/assets/bravais2.png',
                            'nanohubtools/assets/bravais3.png',
                            'nanohubtools/assets/bravais4.png',
                            'nanohubtools/assets/bravais5.png',
                            'nanohubtools/assets/bravais6.png',
                            'nanohubtools/assets/bravais7.png',
                            'nanohubtools/assets/potential1.png',
                            'nanohubtools/assets/potential2.png',
                            'nanohubtools/assets/potential3.png',
                            'nanohubtools/assets/potential4.png',
                            'nanohubtools/assets/potential5.png',
                            'nanohubtools/assets/potential6.png',
                            'nanohubtools/assets/potential7.png',
                            'nanohubtools/assets/potential8.png',
                            'nanohubtools/assets/pot_desc1.png',
                            'nanohubtools/assets/pot_desc2.png',
                            'nanohubtools/assets/pot_desc3.png',
                            'nanohubtools/assets/pot_desc4.png',
                            'nanohubtools/assets/pot_desc5.png',
                            'nanohubtools/assets/pot_desc6.png',
                            'nanohubtools/assets/pot_desc7.png',
                            'nanohubtools/assets/pot_desc8.png',
                            'nanohubtools/assets/pot_desc9.png',
                            'nanohubtools/assets/pot_desc10.png',
                            'nanohubtools/assets/pot_desc11.png',
                        ])],
    'author'          : 'Project Jupyter contributor',
    'author_email'    : 'denphi@denphi.com',
    'url'             : 'https://github.com/denphi/nanohubtools',
    'license'         : 'BSD',
    'platforms'       : "Linux, Mac OS X, Windows",
    'keywords'        : ['Jupyter', 'Widgets', 'IPython'],
    'classifiers'     : [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Jupyter',
    ],
    'include_package_data' : True,
    'install_requires' : [
        'floatview>=0.1.11',
        'plotly>=4.1.0',
        'numpy>=1.16.0',
        'hublib>=0.9.94',
    ],
    'extras_require' : {
        'test': [
        ],
        'examples': [
            # Any requirements for the examples to run
        ],
        'docs': [
        ],
    },
    'entry_points' : {
    },
}

if __name__ == '__main__':
    setup(**setup_args)
