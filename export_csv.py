#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Save the data from the database inside a CSV file.
"""

import gzip
from pathlib import Path
import shutil
import sqlite3

import configuration


# Connect to the database in read-only mode.
connection = sqlite3.connect(f"file:{configuration.DATABASE_FILE}?mode=ro", uri=True)

# Retrieve the data from the database.
revision, last_update_check = list(
    connection.execute(
        "SELECT `revision`, `lastUpdateCheck` FROM `metadata` ORDER BY `revision` DESC"
        + " LIMIT 1;"
    )
)[0]
mapping = []
for row in connection.execute("SELECT `ocCode`, `gcCode` FROM `gc2oc`;"):
    mapping.append(row)

# Close the database connection.
connection.close()

CSV_HEADER = f"""# gc2oc.csv
#
# Provides GC -> OC waypoint translation table based on the data set by the geocache
# owners. It has been retrieved from the OKAPI on {last_update_check} (revision
# {revision}).
#
# The data is provided under the terms of the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Germany (CC BY-NC-ND 3.0 DE) license. See
# https://www.opencaching.de/articles.php?page=impressum#datalicense&locale=EN for more
# information.
#
# File format: gcCode,ocCode
"""

csv_path = Path("output", "gc2oc.csv")
with open(csv_path, mode="w", encoding="utf8") as outfile:
    outfile.write(CSV_HEADER)
    for entry in mapping:
        oc_code, gc_code = entry
        outfile.write(f"{gc_code},{oc_code}\n")

gzip_path = Path("output", "gc2oc.csv.gz")
with open(csv_path, mode="rb") as infile:
    with gzip.open(gzip_path, mode="wb") as outfile:
        shutil.copyfileobj(infile, outfile)
