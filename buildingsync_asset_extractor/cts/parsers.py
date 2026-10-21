import logging
from dataclasses import asdict

import pandas as pd
from lxml import etree

from buildingsync_asset_extractor.cts.classes import Facility
from buildingsync_asset_extractor.cts.energy_and_water_conservation_measures import (
    ENERGY_AND_WATER_CONSERVATION_MEASURES,
)
from buildingsync_asset_extractor.cts.measure_type_to_cts_field import technology_category_to_cts_field
from buildingsync_asset_extractor.errors import BSyncProcessorError
from buildingsync_asset_extractor.xml_helpers import element_text, find_element

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger("")

# set log level
logger.setLevel(logging.INFO)


def get_covered_facility_identification_information(facility: Facility) -> pd.Series:
    user_defined_fields_trees = [find_element(fa.etree, "./UserDefinedFields") for fa in facility.appearances]
    user_defined_fields_dicts = [
        parse_user_defined_fields(user_defined_fields_tree) for user_defined_fields_tree in user_defined_fields_trees
    ]
    print(user_defined_fields_dicts)

    data = pd.Series()
    data["Agency Designated Covered Facility ID"] = user_defined_fields_dicts[0]["Agency Designated Covered Facility ID"]
    data["Sub-agency Acronym"] = user_defined_fields_dicts[0]["Sub-agency Acronym"]
    data["Facility Name"] = user_defined_fields_dicts[0]["Facility Name"]
    data["Evaluation Name"] = f"Evaluation: {user_defined_fields_dicts[0]['Facility Name']}"

    return data


def get_aggregated_findings_of_comprehensive_evaluations_estimated_annual_data(facility: Facility) -> pd.Series:
    data = pd.Series()

    # data["Evaluation Completion Date"] =

    # Retro/Re-Commissioning Assessment
    is_retrocommissioned = [fa.etree.find("./Reports/Report/RetrocommissioningAudit", fa.etree.nsmap) for fa in facility.appearances]
    data["Retro/Re-Commissioning Assessment"] = all(x is not None and x.text == "true" for x in is_retrocommissioned)

    # Gross Evaluated Square Footage
    floor_areas = [find_element(fa.etree, "./Sites/Site/Buildings/Building/FloorAreas/FloorArea") for fa in facility.appearances]
    gross_floor_area = [
        float(element_text(find_element(fa, "./FloorAreaValue")))
        for fa in floor_areas
        if find_element(fa, "./FloorAreaType").text == "Gross"
    ]
    data["Gross Evaluated Square Footage"] = sum(gross_floor_area)

    # just sums of scenarios
    package_of_measures_scenario_etrees = [
        facility_appearance.cheapest_package_of_measures_scenario.etree
        for facility_appearance in facility.appearances
        if facility_appearance.cheapest_package_of_measures_scenario
    ]

    def sum_from_package_of_measures_scenarios(xpath: str) -> float:
        trees = [s.find("./ScenarioType/PackageOfMeasures/" + xpath, s.nsmap) for s in package_of_measures_scenario_etrees]

        return sum([float(element_text(t)) for t in trees if t is not None])

    data["Estimated Implementation Cost of Measure(s)"] = sum_from_package_of_measures_scenarios("PackageFirstCost")
    data["Estimated Annual Energy Savings"] = sum_from_package_of_measures_scenarios("AnnualSavingsSiteEnergy")
    data["Estimated Annual Energy Cost Savings"] = sum_from_package_of_measures_scenarios("AnnualSavingsCost")
    data["Estimated Annual Water Savings"] = sum_from_package_of_measures_scenarios("AnnualWaterSavings")
    data["Estimated Annual Water Cost Savings"] = sum_from_package_of_measures_scenarios("AnnualWaterCostSavings")

    # data["Estimated Annual Renewable Electricity Output"] =
    # data["Estimated Annual Renewable Thermal Output"] =

    # just sums of scenarios
    data["Estimated Other Annual Ancillary Cost Savings"] = sum_from_package_of_measures_scenarios(
        "OMCostAnnualSavings",
    )

    return data


def get_aggregated_findings_of_comprehensive_evaluations_estimated_life_cycle_data(_facility: Facility) -> pd.Series:
    data = pd.Series()

    # building sync doesn't have these

    return data


def get_potential_conservation_measures_per_technology_category(facility: Facility) -> pd.Series:
    results = dict.fromkeys(ENERGY_AND_WATER_CONSERVATION_MEASURES, 0)
    results.update(dict.fromkeys(technology_category_to_cts_field.values(), 0))

    # for each measure
    measures = [
        measure
        for facility_appearance in facility.appearances
        if facility_appearance.cheapest_package_of_measures_scenario
        for measure in facility_appearance.cheapest_package_of_measures_scenario.measures_by_id.values()
    ]
    for m in measures:
        # get measure type
        (measure_type, _) = next(
            filter(
                lambda x: asdict(m).items() >= x[1].items(),
                ENERGY_AND_WATER_CONSERVATION_MEASURES.items(),
            ),
            (None, None),
        )

        # account for measure in result
        if measure_type is not None:
            logger.info(
                f"Measure `{m.id}` counted under {measure_type}` and `{technology_category_to_cts_field[m.technology_category]}`",
            )
            results[measure_type] += 1
            results[technology_category_to_cts_field[m.technology_category]] += 1

        else:
            logger.warning(
                f"Measure `{m.id}` unable to be mapped. TechnologyCategory: `{m.technology_category}`, MeasureName: `{m.measure_name}`",
            )

    return pd.Series(results)


def parse_user_defined_fields(user_defined_fields_tree: etree._Element) -> dict[str | None, str | None]:
    return {
        find_element(user_defined_field_tree, "./FieldName").text: find_element(user_defined_field_tree, "./FieldValue").text
        for user_defined_field_tree in user_defined_fields_tree
    }


def get_facility_id(user_defined_fields: dict[str | None, str | None]) -> str:
    facility_id = user_defined_fields["Agency Designated Covered Facility ID"]
    if facility_id is None:
        raise BSyncProcessorError("`Agency Designated Covered Facility ID` user defined field has no value")
    return facility_id
