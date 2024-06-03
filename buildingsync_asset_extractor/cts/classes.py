import functools
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from lxml import etree as ETree

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger("")


@dataclass
class Measure:
    technology_category: str
    measure_name: str
    id: str

    def __init__(self, etree: ETree) -> None:
        technology_category = etree.find("./TechnologyCategories/TechnologyCategory", etree.nsmap)[0]

        self.technology_category = technology_category.tag.split("}")[1]
        self.measure_name = technology_category[0].text
        self.id = etree.get("ID")


@dataclass
class PackageOfMeasuresScenario:
    id: str
    etree: ETree
    measures_by_id: dict[str, Measure]


class FacilityAppearance:
    path: Path

    @functools.cached_property
    def cheapest_package_of_measures_scenario(self) -> Optional[PackageOfMeasuresScenario]:
        # get the measures for reference
        measures_by_id = {
            m.get("ID"): Measure(m)
            for m in self.etree.findall("./Measures/Measure", self.etree.nsmap)
        }

        cheapest_package_of_measures_scenario = None
        cheapest_cost = None
        # for each scenario
        for scenario_etree in self.etree.findall("./Reports/Report/Scenarios/Scenario", self.etree.nsmap):
            # only use the package of measures scenarios
            package_of_measures = scenario_etree.find("./ScenarioType/PackageOfMeasures", self.etree.nsmap)
            if package_of_measures is None:
                continue

            # if its the cheapest, use it
            cost = package_of_measures.find("./PackageFirstCost", self.etree.nsmap)
            if cheapest_package_of_measures_scenario is None or (cost is not None and cost < cheapest_cost):
                measure_ids = [m.get("IDref") for m in package_of_measures.findall("./MeasureIDs/MeasureID", self.etree.nsmap)]
                cheapest_package_of_measures_scenario = PackageOfMeasuresScenario(
                    id=scenario_etree.get("ID"),
                    etree=scenario_etree,
                    measures_by_id={k: m for k, m in measures_by_id.items() if k in measure_ids},
                )

        return cheapest_package_of_measures_scenario

    def __init__(self, etree: ETree, path: Path) -> None:
        self.etree = etree
        self.path = path


@dataclass
class Facility:
    """Name of the facility and it's appearances in each file"""
    name: str
    appearances: list[FacilityAppearance] = field(default_factory=list)

    def __iter__(self) -> Iterable[FacilityAppearance]:
        return self.appearances
