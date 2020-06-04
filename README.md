# Mapper for Geocaching.com and Opencaching.de

This is a collection of tools to retrieve the GC -> OC code mappings used on the Opencaching.de site.

## Usage

### Requirements

Make sure you have

* Python 3 (at least version 3.6)
* [requests](https://github.com/requests/requests)

installed on your device.

### Preparations

1. Retrieve an OKAPI key and [download a database snapshot](https://www.opencaching.de/okapi/services/replicate/fulldump.html).
2. Unpack the downloaded file into a directory starting with `fulldump` (to ignore it on commit by default).
3. Rename the `configuration-example.py` file to `configuration.py`. Edit the file and change the parameters to match your setup.
4. Run `python3 -m load_fulldump` to load the data from the fulldump into the database.

### Running

1. Run `python3 -m perform_update` to update the database. This needs to be executed at least every 10 days, but should not be used with less than 5 minutes apart.
2. Run `python3 -m export_csv` to create the CSV file with the mapping.

## Development Tasks

### Code Style

After installing [black](https://github.com/psf/black), you should be able to run `black .` from the root directory of this repository to apply auto-formatting.

To check formatting itself, use `flake8 --max-line-length 88 *.py` after installing [flake8](https://gitlab.com/pycqa/flake8).

## License

The tools inside this repository are licensed under the MIT License (see the `LICENSE.md` file for details).

The actual data retrieved from the OKAPI follows the [Opencaching.de data license](https://www.opencaching.de/articles.php?page=impressum&locale=EN), which means you can use them under the terms of the Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Germany (CC BY-NC-ND 3.0 DE) license.
