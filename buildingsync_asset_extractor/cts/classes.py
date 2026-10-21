import functools
import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from lxml.etree import _Element

from buildingsync_asset_extractor.xml_helpers import element_tag, element_text, find_element

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger("")


@dataclass
class Measure:
    technology_category: str
    measure_name: str | None
    id: str | None

    def __init__(self, etree: _Element) -> None:
        technology_category = find_element(etree, "./TechnologyCategories/TechnologyCategory")[0]

        self.technology_category = element_tag(technology_category).split("}")[1]
        self.measure_name = technology_category[0].text
        self.id = etree.get("ID")


@dataclass
class PackageOfMeasuresScenario:
    id: str | None
    etree: _Element
    measures_by_id: dict[str | None, Measure]


class FacilityAppearance:
    path: Path

    @functools.cached_property
    def cheapest_package_of_measures_scenario(self) -> PackageOfMeasuresScenario | None:
        # get the measures for reference
        measures_by_id = {m.get("ID"): Measure(m) for m in self.etree.findall("./Measures/Measure", self.etree.nsmap)}

        cheapest_package_of_measures_scenario = None
        cheapest_cost = None
        # for each scenario
        for scenario_etree in self.etree.findall("./Reports/Report/Scenarios/Scenario", self.etree.nsmap):
            # only use the package of measures scenarios
            package_of_measures = scenario_etree.find("./ScenarioType/PackageOfMeasures", self.etree.nsmap)
            if package_of_measures is None:
                continue

            # if its the cheapest, use it
            cost_etree = package_of_measures.find("./PackageFirstCost", self.etree.nsmap)
            cost = None if cost_etree is None else float(element_text(cost_etree))
            if cheapest_package_of_measures_scenario is None or (cost is not None and (cheapest_cost is None or cost < cheapest_cost)):
                cheapest_cost = cost
                measure_ids = [m.get("IDref") for m in package_of_measures.findall("./MeasureIDs/MeasureID", self.etree.nsmap)]
                cheapest_package_of_measures_scenario = PackageOfMeasuresScenario(
                    id=scenario_etree.get("ID"),
                    etree=scenario_etree,
                    measures_by_id={k: m for k, m in measures_by_id.items() if k in measure_ids},
                )

        return cheapest_package_of_measures_scenario

    def __init__(self, etree: _Element, path: Path) -> None:
        self.etree = etree
        self.path = path


@dataclass
class Facility:
    """Name of the facility and it's appearances in each file"""

    name: str
    appearances: list[FacilityAppearance] = field(default_factory=list)

    def __iter__(self) -> Iterator[FacilityAppearance]:
        return iter(self.appearances)
