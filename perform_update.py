#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Update the changed data into the database file.
"""

from datetime import datetime
import json
import requests
import sqlite3

import configuration


# Connect to the database.
connection = sqlite3.connect(configuration.DATABASE_FILE)
cursor = connection.cursor()

# Get the current revision.
revision = list(
    connection.execute(
        "SELECT `revision` FROM `metadata` ORDER BY `revision` DESC LIMIT 1;"
    )
)[0][0]

# Handle all changes.
count = 0
while True:
    # Request the changelog.
    url = (
        "https://www.opencaching.de/okapi/services/replicate/changelog"
        + f"?since={revision}&consumer_key={configuration.OKAPI_KEY}"
    )
    data = requests.get(url).content
    try:
        json_data = json.loads(data)
    except json.decoder.JSONDecodeError as error:
        # If the content could not be parsed as JSON, print the content itself and
        # stop by re-raising the exception afterwards.
        print(f"Got JSON decode error when parsing JSON from {url}.")
        print("Response content:")
        print("=" * 80)
        print(data)
        print("=" * 80)
        raise error

    # Retrieve the main variables.
    changelog = json_data["changelog"]
    revision = json_data["revision"]
    more = json_data["more"]

    # Handle the changelog entries.
    for entry in changelog:
        # Only save geocaches.
        if entry["object_type"] != "geocache":
            continue

        # Retrieve the basic entry data.
        oc_code = entry["object_key"]["code"]
        change_type = entry["change_type"]

        if change_type == "delete":
            # Create a deletion query.
            query = "DELETE FROM `gc2oc` WHERE `ocCode` = ?;"
            parameters = (oc_code,)
        elif change_type == "replace":
            # Create an update query.
            query = "INSERT OR REPLACE INTO `gc2oc` (`ocCode`, `gcCode`) VALUES (?,?);"
            data = entry["data"]

            # Skip if this not an update regarding the GC code or the GC code is empty.
            if "gc_code" not in data:
                continue
            gc_code = data["gc_code"]
            # We might want to handle this in the future, but it should not do any real
            # harm for now (at least within `cmanager`). There we are checking the
            # other way round anyway before presenting the match itself.
            if not gc_code:
                continue

            parameters = (oc_code, gc_code)

        # Perform the query itself.
        cursor.execute(query, parameters)
        count += 1

    # Break if we have no more updates.
    if not more:
        break

print(f"{count} elements have been updated.")


# Write the metadata.
generated_at = datetime.today().strftime("%Y-%m-%dT%H:%M:%S%z")
cursor.execute("DELETE FROM `metadata`;")
query = "INSERT INTO `metadata` (`revision`, `lastUpdateCheck`) VALUES (?,?);"
cursor.execute(query, (revision, generated_at))

# Commit the data.
connection.commit()

# Try to reduce the database size.
cursor.execute("VACUUM;")
connection.commit()

# Close the database connection.
connection.close()
