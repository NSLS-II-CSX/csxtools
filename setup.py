from __future__ import (absolute_import, division, print_function)

import sys
import warnings


try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

from distutils.core import setup

setup(
    name='csxtools',
    version="0.0.0",
    author='Brookhaven National Laboratory',
    packages=['csxtools'],
)
