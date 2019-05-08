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

setup_args = dict(
    name            = name,
    description     = 'A floatview output widget for JupyterLab + GlueViz Visualization with plotly',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version         = version,
    scripts         = glob(pjoin('scripts', '*')),
    packages        = find_packages(),
    author          = 'Project Jupyter contributor',
    author_email    = 'denphi@denphi.com',
    url             = 'https://github.com/denphi/nanohubtools',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'Widgets', 'IPython'],
    classifiers     = [
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
    include_package_data = True,
    install_requires = [
        'floatview>=0.1.11',
        'plotly>=3.8.1',
        'numpy>=1.16.0',
    ],
    extras_require = {
        'test': [
        ],
        'examples': [
            # Any requirements for the examples to run
        ],
        'docs': [
        ],
    },
    entry_points = {
    },
)

if __name__ == '__main__':
    setup(**setup_args)
