#!/usr/bin/env python

"""matrix_include.py

    Read a YAML configuration file and export the matrix.include field that is
    used by GitHub Actions
"""

import os
import yaml
import sys


filename = os.getenv("MATRIX_INCLUDE_FILE", "")
if not filename:
    print("You must set environment variable MATRIX_INCLUDE_FILE")
    print("to the path of the YAML configuration file for matrix.include input.")
    sys.exit(1)

with open(filename, "r") as config_file:
    matrix_include = yaml.safe_load(config_file)

print(matrix_include)

sys.exit(0)
