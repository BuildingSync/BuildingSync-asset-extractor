# BuildingSync Asset Extractor (BAE)

This package processes a BuildingSync file to extract asset information that can then be imported into SEED

## Installation

### Install from PyPI

```bash
pip install buildingsync-asset-extractor
```
### Install from source
[Poetry](https://python-poetry.org/) is required to install buildingsync-asset-extractor.
```bash
# Copy repo
git clone https://github.com/BuildingSync/BuildingSync-asset-extractor.git

# install the package
cd BuildingSync-asset-extractor
poetry install

# Test that it works, you should see a message describing the usage
poetry run buildingsync_asset_extractor
```

## Usage

BuildingSync version 2.4.0.

The pre-importer will identify assets defined in the `asset_definitions.json` file stored in the `config` directory.  There are various methods of calculating assets:

1. `sqft`.  The sqft method will calculate a 'primary' and 'secondary' value for the asset based on the area it serves. This is calculated from the floor areas defined in each `Section` element.  `Conditioned` floor area values will be used if present; `Gross` otherwise.

1. `num`. The num method will sum up all assets of the specified type and return a single overall number.

1. `avg`. The avg method will return an average value for all assets of the specified type found.

1. `avg_sqft`. The avg_sqft method will return a weighted average value for all assets of the specified type found based on the area they serve.

1. `age_oldest`, `age_newest`, `age_average`. The age method will retrieve the 'YearOfManufacture' (or 'YearInstalled' if not present) element of a specified equipment type and return either the oldest or newest, or average age (year) as specified. Average age is calculated by a weighted average using the following (in order): capacity, served space area, regular average.

1. `custom`. Use this method for particular asset that do not fit in the other categories; i.e. Heating Efficiency. Note that a dedicated method may need to be written to support this type of asset.

To test usage:

```bash
	python buildingsync_asset_extractor/main.py
```

This will extract assets from `tests/files/testfile.xml` and save the results to `assets_output.json`

There are 2 methods of initializing the Processor: with either a filename or data

```bash
bp = BSyncProcessor(filename=filename)
```
or

```bash
bp = BSyncProcessor(data=file_data)
```

## Assumptions
1. Assuming 1 building per file
1. Assuming sqft method uses "Conditioned" floor area for calculations. If not present, uses "Gross"

## TODO
1. thermal zones: when spaces are listed within them with spaces (or multiple thermal zones), this would change the average setpoint calculations. Is this an exception or a normal case to handle?

## Assets Definitions File

This file is used to specify what assets to extract from a BuildingSync XML file. By default, the file found in `config/asset_definitions.json` is used, but a custom file can be specified with the `set_asset_defs_file` method in the `BSyncProcessor` class.

There are currently 5 types of assets that can be extracted:

1. sqft: Sqft assets take into account the floor area served by a specific asset and returns 'Primary' and 'Secondary' values.  For example: Primary HVAC System and Secondary HVAC System.

1. avg_sqft: Avg_sqft assets compute a weighted average to get the an average asset value.  For example:  Average Heating Setpoint.

1. num: Num assets count the total number of the specified asset found.  For example, Total number of lighting systems.

1. age_oldest, age_newest, and age_average: These types return the oldest or newest asset, or average age of a specific type.  For example: Oldest Boiler.

1. custom: For asset that need particular handling, such as Heating Efficiency. The current assets that have custom methods are:
	- Heating System Efficiency
	- Cooling System Efficiency
	- Lighting System Efficiency
	- Water Heater Efficiency
	- Heating Fuel Type

The schema for the assets definition JSON file is in `schemas/asset_definitions_schema.json`.

## Extracted Assets File

The schema for the extracted assets JSON file is in `schemas/extracted_assets_schema.json`.

This file lists the extracted assets information in name, value, units triples.  Names will match the `export_name` listed in the asset_definitions JSON file, except for assets of type 'sqft', which will be prepended by 'Primary' and 'Secondary'.

## Developing

### Pre-commit

This project uses `pre-commit <https://pre-commit.com/>`_ to ensure code consistency.
To enable pre-commit on every commit run the following from the command line from within the git checkout of the BuildingSync-asset-extractor

```bash
  pre-commit install
```

To run pre-commit against the files without calling git commit, then run the following. This is useful when cleaning up the repo before committing.

```bash
  pre-commit run --all-files
```
### Testing

	poetry run pytest

## Releasing

```bash
poetry build

# config and push to testpypi
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi

# install from testpypi
pip install --index-url https://test.pypi.org/simple/ buildingsync-asset-extractor
```
If everything looks good, publish to pypi:
```bash
poetry publish
```

If you have environment variables setup for PYPI token username and password:

```bash
poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD
```
