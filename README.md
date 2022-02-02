# BuildingSync Pre-Importer

This package processes a BuildingSync file to extract asset information that can then be imported into SEED

## Installation

### Install from PyPI

```bash
pip install buildingsync-preimporter
```
### Install from source
[Poetry](https://python-poetry.org/) is required to install buildingsync-preimporter.
```bash
# Copy repo
git clone https://github.com/BuildingSync/BuildingSync-preimporter.git

# install the package
cd BuildingSync-preimporter
poetry install

# Test that it works, you should see a message describing the usage
poetry run buildingsync_preimporter
```

## Usage

BuildingSync version 2.4.0.

The pre-importer will identify assets defined in the `asset_definitions.json` file stored in the `config` directory.  There are various methods of calculating assets:

1. `sqft`.  The sqft method will calculate a 'primary' and 'secondary' value for the asset based on the area it serves. This is calculated from the floor areas defined in each `Section` element.  `Conditioned` floor area values will be used if present; `Gross` otherwise.

1. `num`. The num method will sum up all assets of the specified type and return a single overall number.

1. `avg`. The avg method will return an average value for all assets of the specified type found.

1. `avg_sqft`. The avg_sqft method will return a weighted average value for all assets of the specified type found based on the area they serve.

1. `age_oldest` and `age_youngest`. The age method will retrieve the 'YearInstalled' element of a specified equipment type and return either the oldest or youngest, as specified.

To test usage:

```bash
	python buildingsync_preimporter/main.py
```

## Assumptions
1. Assuming 1 building per file
1. Assuming sqft method uses "Conditioned" floor area for calculations. If not, uses "Gross"

## TODO
1. thermal zones: when spaces are listed within them with spaces (or multiple thermal zones), this would change the average setpoint calculations. Is this an exception or a normal case to handle?
1. How to handle User Defined Fields

## Developing

### Pre-commit

This project uses `pre-commit <https://pre-commit.com/>`_ to ensure code consistency.
To enable pre-commit on every commit run the following from the command line from within the git checkout of the
GMT:

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
pip install --index-url https://test.pypi.org/simple/ buildingsync-preimporter
```
If everything looks good, publish to pypi:
```bash
poetry publish
```
