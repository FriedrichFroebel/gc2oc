#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Upload the changes using Git. This will overwrite the existing Git history using a
forced push.
"""

import shutil
import sqlite3
import sys

from git import Repo

import configuration


# File paths.
filenames = ["gc2oc.csv", "gc2oc.csv.gz"]
source_paths = [
    configuration.BASE_PATH_SCRIPTS / "output" / filename for filename in filenames
]
destination_paths = [configuration.BASE_PATH_DATA / filename for filename in filenames]
git_config_path = configuration.BASE_PATH_DATA / ".git" / "config"

# Initialize Git object.
repository = Repo(configuration.BASE_PATH_DATA)

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
shutil.rmtree(configuration.BASE_PATH_DATA / ".git")
Repo.init(configuration.BASE_PATH_DATA)
with open(git_config_path, mode="w", encoding="utf8") as outfile:
    outfile.write(git_config)

# Initialize the new Git object.
repository = Repo(configuration.BASE_PATH_DATA)

# Connect to the database.
connection = sqlite3.connect(str(configuration.DATABASE_FILE))
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
