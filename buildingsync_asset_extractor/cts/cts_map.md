 ## Covered Facility Identification Information
| Field | XPath | Notes |
|----------|:-------------:|------:|
| Agency Designated Covered Facility ID | `/BuildingSync/Facilities/Facility/UserDefinedFields/UserDefinedField/FieldValue` | `FieldName` = Agency Designated Covered Facility ID |
| Sub-Agency Acronym | `/BuildingSync/Facilities/Facility/UserDefinedFields/UserDefinedField/FieldValue` | `FieldName` = Sub-Agency Acronym |
| Facility Name | `/BuildingSync/Facilities/Facility/UserDefinedFields/UserDefinedField/FieldValue` | `FieldName` = Facility Name |


 ## Aggregated Findings of Comprehensive Evaluations Estimated Annual Data
 | Field | XPath | Notes |
|----------|:-------------:|------:|
| Evaluation Name | `/BuildingSync/Facilities/Facility/UserDefinedFields/UserDefinedField/FieldValue` | "Evaluation: " + `Facility Name` |
| Evaluation Completion Date | | |
| Retro/Re-Commissioning Assessment | `/auc:BuildingSync/auc:Facilities/auc:Facility/auc:Reports/auc:Report/auc:RetrocommissioningAudit` | if all True|
| Gross Evaluated Square Footage | `/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building/FloorAreas/FloorArea/FloorAreaValue` | where `FloorAreaType` is Gross |
| Estimated Implementation Cost of Measure(s) | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/PackageFirstCost` | |
| Estimated Annual Energy Savings | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/AnnualSavingsSiteEnergy` | |
| Estimated Annual Energy Cost Savings | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/AnnualSavingsCost` | |
| Estimated Annual Water Savings | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/AnnualWaterSavings` | |
| Estimated Annual Water Cost Savings | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/AnnualWaterCostSavings` | |
| Estimated Annual Renewable Electricity Output | | |
| Estimated Annual Renewable Thermal Output | | |
| Estimated Other Annual Ancillary Cost Savings | `/BuildingSync/Facilities/Facility/Reports/Report/Scenarios/Scenario/ScenarioType/PackageOfMeasures/OMCostAnnualSavings` | |

 ## Aggregated Findings of Comprehensive Evaluations Estimated Life-Cycle Data
 | Field | XPath | Notes |
|----------|:-------------:|------:|
| Estimated Life-Cycle Energy Savings | | |
| Estimated Present Value Life-Cycle Energy Cost Savings | | |
| Estimated Life-Cycle Water Savings | | |
| Estimated Present Value Life-Cycle Water Cost Savings | | |
| Estimated Other Present Value Life-Cycle Ancillary Cost Savings | | |


## Potential Conservation Measures (per Technology Category)
 | Field | XPath | Notes |
|----------|:-------------:|------:|
|Boiler Plant Improvements|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/BoilerPlantImprovements`|count of instances|
|Chiller Plant Improvements|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/ChillerPlantImprovements`|count of instances|
|Building Automation Systems / EMCS|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/BuildingAutomationSystems`|count of instances|
|Heating, Ventilating, and Air Conditioning|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/OtherHVAC`|count of instances|
|Lighting Improvements|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/LightingImprovements`|count of instances|
|Building Envelope Modifications|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/BuildingEnvelopeModifications`|count of instances|
|CW / HW / Steam Distribution Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/ChilledWaterHotWaterAndSteamDistributionSystems`|count of instances|
|Electric Motors and Drives|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/OtherElectricMotorsAndDrives`|count of instances|
|Refrigeration|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/Refrigeration`|count of instances|
|Distributed Generation|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/DistributedGeneration`|count of instances|
|Renewable Energy Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/RenewableEnergySystems`|count of instances|
|Energy / Utility Distribution Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/EnergyDistributionSystems`|count of instances|
|Water and Sewer Conservation Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/WaterAndSewerConservationSystems`|count of instances|
|Electrical Peak Shaving / Load Shifting|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/ElectricalPeakShavingLoadShifting`|count of instances|
|Rate Adjustments|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/EnergyCostReductionThroughRateAdjustments`|count of instances|
|Energy Related Process Improvements|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/EnergyRelatedProcessImprovements`|count of instances|
|Advanced Metering Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/AdvancedMeteringSystems`|count of instances|
|Appliance / Plug-load Reductions|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/PlugLoadReductions`|count of instances|
|Service Hot Water (SHW) Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/ServiceHotWaterSystems`|count of instances|
|Conveyance Systems|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/ConveyanceSystems`|count of instances|
|Data Center Energy Conservation Improv|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/DataCenterImprovements`|count of instances|
|Commissioning Measures| ???? |count of instances|
|Other|`/BuildingSync/Facilities/Facility/Measures/Measure/TechnologyCategories/TechnologyCategory/Uncategorized`|count of instances|
