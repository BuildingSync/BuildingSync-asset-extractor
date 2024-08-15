# CHANGELOG

## Version 0.2.0

- Added Export to CTS format functionality
- Unit conversion updates
- Lock pandas version to be compatible with SEED
- Compatible with BuildingSync version 2.4.0

## Version 0.1.14

- Updated error handling

## Version 0.1.13

- Add Electrification Potential Asset
- Update Process Lighting
- Major code cleanup/refactoring

## Version 0.1.12

Updated lxml dependency to 4.9.1

## Version 0.1.11

- Better units handling (distinction between predefined units and calculated units)
- added "export_units" key to asset definition schema to indicate fields that will get a generated associated units field

## Version 0.1.10

Revise how asset units are handled

## Version 0.1.9

Add new Heating, Cooling, WaterHeating, and LightingSystems assets

## Version 0.1.8

Fix bug in section floor area type checking

## Version 0.1.7

Update constructor to accept a filename or direct xml data

## Version 0.1.6

Fix logger

## Version 0.1.5

Adding class method for accessing default asset definitions

## Version 0.1.4

- Modify asset definitions array returned form get_asset_defs()
- Set logger default level to info

## Version 0.1.3

Modify assets array returned from get_assets()

## Version 0.1.2

Fix access to default asset_definitions.json file

## Version 0.1.1

Changes to output structure and schema

## Version 0.1.0

Initial Release of the BuildingSync Asset Extractor
