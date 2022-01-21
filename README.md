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
