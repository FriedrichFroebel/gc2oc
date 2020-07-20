#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Load the data from a fulldump into a database file.
"""

import json
import sqlite3

import configuration


# Delete the existing database file.
database_path = configuration.DATABASE_FILE
if database_path.exists():
    database_path.unlink()

# Connect to the database.
connection = sqlite3.connect(str(configuration.DATABASE_FILE))
cursor = connection.cursor()

# Create the database tables.
structure_file = configuration.BASE_PATH_SCRIPTS / "templates" / "structure.sql"
with open(structure_file, encoding="utf8") as infile:
    queries = infile.read().split(";")
    for query in queries:
        query = query.strip()
        if not query:
            continue
        query = f"{query};"
        cursor.execute(query)
    connection.commit()

# Load the list of data files from the fulldump.
dump_path = configuration.FULLDUMP_DIRECTORY
with open(dump_path / "index.json", encoding="utf8") as infile:
    json_data = json.load(infile)
    files = json_data["data_files"]
    revision = json_data["revision"]
    generated_at = json_data["meta"]["generated_at"]

query = "INSERT INTO `metadata` (`revision`, `lastUpdateCheck`) VALUES (?,?);"
cursor.execute(query, (revision, generated_at))

# Prepare the query to insert the cache data.
query = "INSERT INTO `gc2oc` (`ocCode`, `gcCode`) VALUES (?,?);"

# Handle each data file from the fulldump.
for filename in files:
    print(f"Loading file {filename} into database ...")
    filename = dump_path / filename

    # Load the JSON data.
    with open(filename, encoding="utf8") as infile:
        json_data = json.load(infile)

    # Add to database.
    for line in json_data:
        # Only save geocaches.
        if line["object_type"] != "geocache":
            continue
        # As we are creating a fresh database, we can skip deletion requests.
        if line["change_type"] == "delete":
            continue

        # Retrieve the data from the JSON dictionary.
        data = line["data"]
        oc_code = data["code"]
        gc_code = data["gc_code"]

        # Skip not set GC codes.
        if not gc_code:
            continue

        # Run the query with the current parameter set.
        cursor.execute(query, (oc_code, gc_code))

# Save the data.
connection.commit()

# Try to reduce the database size.
cursor.execute("VACUUM;")
connection.commit()

# Close the database connection.
connection.close()
