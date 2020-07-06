#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Upload the changes using Git. This will overwrite the existing Git history using a
forced push.
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
git_config_path = data_repository_path / ".git" / "config"

# Initialize Git object.
repository = Repo(data_repository_path)

# Pull changes from remote to avoid conflicts.
repository.remotes.origin.pull()

# Save the old Git configuration.
with open(git_config_path, mode="r", encoding="utf8") as infile:
    git_config = infile.read()

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

# Delete the old Git directory, then re-initialize the repository and apply the old
# configuration.
shutil.rmtree(data_repository_path / ".git")
Repo.init(data_repository_path)
with open(git_config_path, mode="w", encoding="utf8") as outfile:
    outfile.write(git_config)

# Initialize the new Git object.
repository = Repo(data_repository_path)

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
# We have to add all files of the root directory of the repository. Note that we cannot
# use `.` here as this would add the `.git` directory as well, which results in an FSCK
# error with Git on push.
repository.index.add("*")
commit_message = f"Update to revision {revision}"
repository.index.commit(commit_message)

# Push the changes.
repository.git.push(force=True)
