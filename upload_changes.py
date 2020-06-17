#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Upload the changes using Git.
"""

from pathlib import Path
import shutil
import sqlite3
import sys

from git import Repo

import configuration


# File paths.
filenames = ["gc2oc.csv", "gc2oc.csv.gz"]
source_paths = [Path("output", filename) for filename in filenames]
data_repository_path = Path("../gc2oc-data")
destination_paths = [Path(data_repository_path, filename) for filename in filenames]

# Initialize Git object.
repository = Repo(data_repository_path)

# Pull changes from remote to avoid conflicts.
repository.remotes.origin.pull()

# Copy the updated files to the repository.
file_mappings = tuple(zip(source_paths, destination_paths))
for mapping in file_mappings:
    source_path, destination_path = mapping
    shutil.copy(source_path, destination_path)

# Check for changes and abort if nothing changed.
changed_files = [item.a_path for item in repository.index.diff(None)]
if not changed_files:
    print("No changes to commit. Aborting ...")
    sys.exit(0)

# Connect to the database.
connection = sqlite3.connect(configuration.DATABASE_FILE)
cursor = connection.cursor()

# Get the current revision.
revision = list(
    connection.execute(
        "SELECT `revision` FROM `metadata` ORDER BY `revision` DESC LIMIT 1;"
    )
)[0][0]

# Close the database connection.
connection.close()

# Add the changes and commit.
repository.git.add(update=True)
commit_message = f"Update to revision {revision}"
repository.index.commit(commit_message)

# Push the changes.
origin = repository.remote(name="origin")
origin.push()
