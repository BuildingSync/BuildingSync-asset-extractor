
import logging
from pathlib import Path

import pandas as pd
from lxml import etree
from styleframe import StyleFrame

from buildingsync_asset_extractor.cts.classes import (
    Facility,
    FacilityAppearance
)
from buildingsync_asset_extractor.cts.parsers import (
    get_aggregated_findings_of_comprehensive_evaluations_estimated_annual_data,
    get_aggregated_findings_of_comprehensive_evaluations_estimated_life_cycle_data,
    get_covered_facility_identification_information,
    get_potential_conservation_measures_per_technology_category,
    parse_user_defined_fields
)

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger("")

# set log level
logger.setLevel(logging.INFO)

BLANK_CTS_FILE_PATH = Path(__file__).parent / "CTS Comprehensive Evaluation Upload Template_20240312_021125.xlsx"


def log_facilities(facility_by_id: dict[str, Facility]) -> None:
    for facility_name, facility in facility_by_id.items():
        logger.info(f"{facility_name}:")
        logger.info("\tfound in:")
        for appearance in facility.appearances:
            logger.info(f"\t\t-{appearance.path}")
            cpoms = appearance.cheapest_package_of_measures_scenario
            if cpoms:
                logger.info(f"\t\t\tusing cheapest package of measures: {cpoms.id} (measures: {list(cpoms.measures_by_id.keys())})")


def aggregate_facilities(files: list[Path]) -> dict[str, Facility]:
    facility_by_id: dict[str, Facility] = {}

    # for each file, get the facilities in the file
    for f in files:
        file_etree = etree.parse(f)
        facility_etrees = file_etree.findall("/Facilities/Facility", namespaces=file_etree.getroot().nsmap)

        # for each facility in the file, add it to facility_by_id
        for facility_etree in facility_etrees:
            user_defined_fields_tree = facility_etree.find("./UserDefinedFields", facility_etree.nsmap)
            facility_id = parse_user_defined_fields(user_defined_fields_tree)["Agency Designated Covered Facility ID"]

            facility = facility_by_id.get(facility_id, Facility(facility_id))
            facility.appearances.append(FacilityAppearance(facility_etree, f))
            facility_by_id[facility_id] = facility

    log_facilities(facility_by_id)

    return facility_by_id


def building_sync_to_cts(files: list[Path], out_file: Path) -> None:
    # import blank template
    df = pd.read_excel(BLANK_CTS_FILE_PATH, sheet_name="Evaluation Upload Template")

    # for each facility, fill in a row
    facility_by_id = aggregate_facilities(files)
    for i, (facility_name, facility) in enumerate(facility_by_id.items()):
        df.loc[3 + i] = to_cts_row(facility)

    # write back out
    sf = StyleFrame.read_excel_as_template(BLANK_CTS_FILE_PATH, df=df, sheet_name="Evaluation Upload Template")
    writer = sf.to_excel(out_file, row_to_add_filters=0)
    writer.close()


def to_cts_row(facility: Facility) -> pd.Series:
    return pd.concat([
        get_covered_facility_identification_information(facility),
        get_aggregated_findings_of_comprehensive_evaluations_estimated_annual_data(facility),
        get_aggregated_findings_of_comprehensive_evaluations_estimated_life_cycle_data(facility),
        get_potential_conservation_measures_per_technology_category(facility),
    ])
