import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union

from lxml.etree import ElementTree

from buildingsync_asset_extractor.lighting_processing.building_occ_class_to_building_type import (
    building_occ_class_to_building_type
)
from buildingsync_asset_extractor.lighting_processing.building_space_type_to_lpd import (
    BuildingSpaceTypeLPD,
    building_space_type_to_lpd
)
from buildingsync_asset_extractor.lighting_processing.building_type_to_lpd import (
    BuildingTypeLPD,
    building_type_to_lpd
)
from buildingsync_asset_extractor.lighting_processing.section_occ_class_to_section_type import (
    section_occ_class_to_section_type
)

if TYPE_CHECKING:
    from buildingsync_asset_extractor.processor import BSyncProcessor


BUILDING_PATH = '/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building'
LIGHTING_SYSTEM_PATH = "/BuildingSync/Facilities/Facility/Systems/LightingSystems/LightingSystem"


@dataclass
class LightingData(abc.ABC):
    sqft: float
    sqft_percent: Optional[float]


@dataclass
class LightingDataLPD(LightingData):
    lpd: float


@dataclass
class LightingDataPower(LightingData):
    power: float


def process_buildings_lighting_systems(bsync_processor: "BSyncProcessor") -> list[LightingData]:
    """Given a bsync_processor with a single building, get all of its lightingData.

    This function is HUGE, and thus broken down into a series of more digestable functions, starting
    with _process_buildings_lighting_systems.
    """
    def _process_buildings_lighting_systems() -> list[LightingData]:
        """Given a bsync_processor with a single building, get each section's LightingData.
        """
        # assert only one building in doc
        buildings = bsync_processor.xp(bsync_processor.doc, BUILDING_PATH)
        if len(buildings) == 1:
            building = buildings[0]
        else:
            raise ValueError(
                f"process_lighting requires a document with a singular building. The given document has {len(buildings)} buildings"
            )

        # get the lighting datas for each section
        lighting_datas: list[LightingData] = []
        sections = bsync_processor.xp(building, './/' + 'Sections/Section')
        for section in sections:
            lighting_datas += process_sections_lighting_systems(section)

        return lighting_datas

    def process_sections_lighting_systems(section: ElementTree) -> list[LightingData]:
        """Get all the section's lightingData.
        """
        lighting_systems: list[ElementTree] = get_sections_lighting_systems(section)

        # if no lighting systems, method_4 on the whole section.
        if len(lighting_systems) == 0:
            sqft = get_section_gross_floor_area(section)
            lpd = method_4(section)
            if lpd is not None:
                return [LightingDataLPD(lpd=lpd, sqft=sqft, sqft_percent=100)]

        # else, compute by each lighting system.
        lighting_datas: list[LightingData] = []
        for lighting_system in lighting_systems:
            sqft_percent = get_lighting_system_sqft_percent(lighting_system)
            sqft = get_lighting_system_sqft(section, lighting_system)

            power = method_1(lighting_system)
            if power is not None:
                lighting_datas.append(LightingDataPower(power=power, sqft=sqft, sqft_percent=sqft_percent))
                continue

            power = method_2(lighting_system)
            if power is not None:
                lighting_datas.append(LightingDataPower(power=power, sqft=sqft, sqft_percent=sqft_percent))
                continue

            lpd = method_3(lighting_system)
            if lpd is not None:
                lighting_datas.append(LightingDataLPD(lpd=lpd, sqft=sqft, sqft_percent=sqft_percent))
                continue

            lpd = method_4(section)
            if lpd is not None:
                lighting_datas.append(LightingDataLPD(lpd=lpd, sqft=sqft, sqft_percent=sqft_percent))
                continue

        # TODO: fill in sqft_percent

        return lighting_datas

    def get_sections_lighting_systems(section: ElementTree) -> list[ElementTree]:
        """Get all the lighting systems linked to the section.
        """
        section_ID = section.get("ID")
        sections_lighting_systems = []

        all_lighting_systems = bsync_processor.xp(bsync_processor.doc, LIGHTING_SYSTEM_PATH)
        for ls in all_lighting_systems:
            linked_sections = bsync_processor.xp(ls, './/' + 'LinkedSectionID')
            linked_section_IDs = [s.get('IDref') for s in linked_sections]

            if section_ID in linked_section_IDs:
                sections_lighting_systems.append(ls)

        return sections_lighting_systems

    def get_lighting_system_sqft_percent(lighting_system: ElementTree) -> Optional[float]:
        """Get lighting systems PercentPremisesServed.
        """
        percent_premises_served = bsync_processor.xp(
            lighting_system, './/' + 'PercentPremisesServed'
        )
        if len(percent_premises_served) > 0:
            return float(percent_premises_served[0].text)
        else:
            return None

    def get_section_gross_floor_area(section: ElementTree) -> float:
        """Get sections gross floor area.
        """
        section_ID = section.get("ID")

        return bsync_processor.sections[section_ID].areas.get("Gross")  # type: ignore

    def get_lighting_system_sqft(section: ElementTree, lighting_system: ElementTree) -> float:
        """Give a section and lighting system, get the sqft the lighting system covers within that section.
        """
        section_ID = section.get("ID")
        all_linked_sections = bsync_processor.xp(lighting_system, './/' + 'LinkedSectionID')
        linked_sections = [ls for ls in all_linked_sections if ls.get('IDref') == section_ID]

        return sum([bsync_processor.compute_sqft(ls) for ls in linked_sections])

    def method_1(lighting_system: ElementTree) -> Optional[float]:
        """return lighting system's InstalledPower.
        """
        installed_powers = bsync_processor.xp(lighting_system, './/' + 'InstalledPower')

        if len(installed_powers) > 0:
            return float(installed_powers[0].text)
        else:
            return None

    def method_2(lighting_system: ElementTree) -> Optional[float]:
        """Lamp Power * # Lamps per Luminaire * # Luminaire * Quantity

        number_of_luminaireses may be taken from user defined fields.
        """
        number_of_luminaireses = bsync_processor.xp(lighting_system, './/' + 'NumberOfLuminaires')
        number_of_lamps_per_luminaires = bsync_processor.xp(lighting_system, './/' + 'NumberOfLampsPerLuminaire')
        lamp_powers = bsync_processor.xp(lighting_system, './/' + 'LampPower')
        quantity_elements = bsync_processor.xp(lighting_system, './/' + 'Quantity')

        # method 2a: Lamp Power * # Lamps per Luminaire * # Luminaire * Quantity
        if (
            len(lamp_powers) > 0 and
            len(number_of_lamps_per_luminaires) > 0 and
            len(number_of_luminaireses) > 0
        ):
            power = float(lamp_powers[0].text) * float(number_of_lamps_per_luminaires[0].text) * float(number_of_luminaireses[0].text)
            if quantity_elements:
                power *= float(quantity_elements[0].text)

            return power

        # method 2b: Lamp Power * # Lamps per Luminaire * # Luminaire
        # where # Luminaire is user defined
        elif (
            len(lamp_powers) > 0 and
            len(number_of_lamps_per_luminaires) > 0
        ):
            # try to get # luminaires a different way
            # UDF: '* Quantity Of Luminaires For *'
            # example: Common Areas Quantity Of Luminaires For Section-101919600
            user_defined_fields = bsync_processor._get_user_defined_feilds(lighting_system)
            user_defined_values = [
                int(value)
                for (name, value) in user_defined_fields
                if 'Quantity Of Luminaires For' in name
                and value.replace(" ", "").isnumeric()
            ]
            qty_val = sum(user_defined_values)

            if qty_val > 0:
                return (
                    int(lamp_powers[0].text) *
                    int(number_of_lamps_per_luminaires[0].text) *
                    qty_val
                )

        return None

    def method_3(lighting_system: ElementTree) -> Optional[float]:
        """Look in UDF for "Lighting Power Density For ..."
        """
        user_defined_fields = bsync_processor._get_user_defined_feilds(lighting_system)
        user_defined_values = [
            int(value) for (name, value)
            in user_defined_fields
            if 'Lighting Power Density For' in name
            and value.replace(" ", "").isnumeric()
        ]
        qty_val = sum(user_defined_values)

        if qty_val > 0:
            return qty_val

        return None

    def method_4(section: ElementTree) -> Optional[float]:
        """Use decision matrix to get lpd from building/section occupancy class and year.
        """
        building = section.getparent().getparent()
        section_occ_class = get_occupancy_classification(section)
        building_occ_class = get_occupancy_classification(building)
        year = get_year(building)

        if year is None:
            return None

        # get section_type and building_type via the dictionaries
        section_type = None if section_occ_class is None else section_occ_class_to_section_type.get(section_occ_class)
        building_type = None if building_occ_class is None else building_occ_class_to_building_type.get(building_occ_class)

        # if we have neither, fail
        if section_type is None and building_type is None:
            return None

        # if we have section type, filter building_space_type_to_lpd by section type.
        possible_lpds: Union[list[BuildingSpaceTypeLPD], list[BuildingTypeLPD]]
        if section_type:
            possible_lpds = building_space_type_to_lpd
            possible_lpds = [x for x in possible_lpds if x.section_type == section_type]

            # if we have building type, filter by it, else filter by other.
            building_types = [x.building_type for x in possible_lpds]
            if building_type in building_types:
                possible_lpds = [x for x in possible_lpds if x.building_type == building_type]
            else:
                possible_lpds = [x for x in possible_lpds if x.building_type == "Other"]

        # If we have just building_type, use Building_Type_to_lpd
        elif building_type:
            possible_lpds = building_type_to_lpd
            possible_lpds = [x for x in possible_lpds if x.building_type == building_type]

        # if none match the criteria, fail
        if len(possible_lpds) == 0:
            return None
        elif len(possible_lpds) == 1:
            lpds = possible_lpds[0].lpd_by_year
        else:
            raise Exception  # we should not have gotten here.

        # get the closest year
        lpds = {year: lpd for (year, lpd) in lpds.items() if lpd is not None}
        lpd_years = sorted(lpds.keys())
        if lpd_years[0] > year:
            best_year = lpd_years[0]
        else:
            lpd_years = [y for y in lpd_years if y <= year]
            best_year = lpd_years[-1]

        return lpds[best_year]

    def get_occupancy_classification(element: ElementTree) -> Optional[str]:
        """Get a building or sections OccupancyClassification"""
        occupancy_classification = bsync_processor.xp(element, './' + 'OccupancyClassification')

        if len(occupancy_classification) > 0:
            return occupancy_classification[0].text
        else:
            return None

    def get_year(building: ElementTree) -> Optional[float]:
        """Get a building's Year."""
        year_of_lastest_retrofit = bsync_processor.xp(building, './/' + 'YearOfLatestRetrofit')
        if len(year_of_lastest_retrofit) > 0:
            return float(year_of_lastest_retrofit[0].text)

        year_of_last_major_remodel = bsync_processor.xp(building, './/' + 'YearOfLastMajorRemodel')
        if len(year_of_last_major_remodel) > 0:
            return float(year_of_last_major_remodel[0].text)

        year_of_construction = bsync_processor.xp(building, './/' + 'YearOfConstruction')
        if len(year_of_construction) > 0:
            return float(year_of_construction[0].text)

        return None

    return _process_buildings_lighting_systems()
