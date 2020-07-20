#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration parameters.
"""

from pathlib import Path


# The base path to use.
BASE_PATH = Path("/home/opencaching/gc2oc")

# The base path for the scripts.
# This should point to the directory containing this configuration file.
BASE_PATH_SCRIPTS = BASE_PATH / "scripts"

# The base path for the data repository.
BASE_PATH_DATA = BASE_PATH / "gc2oc-data"

# The path of the database file (SQLite3).
DATABASE_FILE = BASE_PATH / "gc2oc.db"

# The directory containing the unpacked fulldump.
FULLDUMP_DIRECTORY = BASE_PATH / "fulldump_20200101-1200"

# The OKAPI consumer key to use.
OKAPI_KEY = "OKAPI_KEY"
