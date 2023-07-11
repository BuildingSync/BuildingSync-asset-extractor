"""
*********************************************************************************************************
:copyright (c) BuildingSync®, Copyright (c) 2015-2022, Alliance for Sustainable Energy, LLC,
and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

(1) Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

(2) Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the distribution.

(3) Neither the name of the copyright holder nor the names of any contributors may be used to endorse
or promote products derived from this software without specific prior written permission from the
respective party.

(4) Other than as required in clauses (1) and (2), distributions in any form of modifications or other
derivative works may not use the "BuildingSync" trademark or any other confusingly similar designation
without specific prior written permission from Alliance for Sustainable Energy, LLC.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER(S) AND ANY CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER(S), ANY
CONTRIBUTORS, THE UNITED STATES GOVERNMENT, OR THE UNITED STATES DEPARTMENT OF ENERGY, NOR ANY OF
THEIR EMPLOYEES, BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*********************************************************************************************************
"""
import dataclasses
import json
import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Union

from importlib_resources import files
from lxml import etree
from lxml.etree import ElementTree

from buildingsync_asset_extractor.errors import BSyncProcessorError
from buildingsync_asset_extractor.formatters import Formatter
from buildingsync_asset_extractor.lighting_processing.lighting_processing import (
    LightingData,
    process_buildings_lighting_systems
)
from buildingsync_asset_extractor.types import (
    Asset,
    AssetData,
    AssetDef,
    Section,
    SystemData
)

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.INFO)

# BuildingSync Schema location
BUILDINGSYNC_SCHEMA_URL = "http://buildingsync.net/schemas/bedes-auc/2019"
DEFAULT_ASSETS_DEF_FILE = 'asset_definitions.json'  # in package's config directory


# Processor class loads an XML file and extracts assets
class BSyncProcessor:

    def __init__(self,
                 filename: Optional[Union[Path, str]] = None,
                 data: Optional[bytes] = None,
                 asset_defs_filename: Optional[str] = None,
                 logger_level: Optional[str] = 'INFO') -> None:
        """class instantiator
          :param filename: str, xml to parse
          :param asset_defs_filename: Optional(str), asset definition abs filepath
        """
        # set logger
        ll = logging.INFO
        if logger_level == 'DEBUG':
            ll = logging.DEBUG
        logger.setLevel(ll)

        # takes in a XML file to process
        if filename:
            logger.debug("Filename passed into BAE constructor")
            self.filename = filename
            with open(self.filename, mode='rb') as file:
                self.file_data = file.read()
        elif data:
            logger.debug("Data passed into BAE constructor")
            self.file_data = data
        else:
            # no data. handle
            raise BSyncProcessorError("You must provide either a filename or xml data")
        self.parse_xml()

        self.initialize_vars(asset_defs_filename)

        self.formatter = Formatter(self.export_asset, self.export_asset_units)

    def initialize_vars(self, asset_defs_filename: Optional[str]) -> None:
        # use default asset definitions file unless otherwise specified
        self.asset_defs: list[AssetDef]
        if asset_defs_filename:
            self.config_filename = asset_defs_filename
            # open abs path
            with open(self.config_filename, mode='rb') as f:
                self.asset_defs = [
                    AssetDef(**asset_def)
                    for asset_def in json.load(f)['asset_definitions']
                ]
        else:
            self.config_filename = DEFAULT_ASSETS_DEF_FILE
            # open with importlib.resources
            file = files('buildingsync_asset_extractor.config').joinpath(self.config_filename).read_text()
            self.asset_defs = [
                AssetDef(**asset_def)
                for asset_def in json.loads(file)['asset_definitions']
            ]

        self.namespaces: dict[str, str] = {}
        self.sections: dict[Any, Section] = {}  # Section by ID
        self.asset_data = AssetData(assets=[])
        # TODO: do we want to round answers?
        self.round_digits = 5

        # set namespaces
        self.key: Optional[str] = None
        self.set_namespaces()

    def set_asset_defs_file(self, asset_defs_filename: Union[Path, str]) -> None:
        # set and parse
        self.config_filename = str(asset_defs_filename)
        with open(self.config_filename, mode='rb') as file:
            self.asset_defs = [
                AssetDef(**asset_def)
                for asset_def in json.load(file)['asset_definitions']
            ]

    def get_asset_defs(self) -> list[AssetDef]:
        """ return asset definitions array """
        return self.asset_defs

    def set_namespaces(self) -> None:
        """set namespaces from xml file"""

        context = etree.XML(self.file_data)
        namespaces = context.xpath('//namespace::*')

        for key, value in namespaces:

            # only register the namespace that matches BUILDGINSYNC_SCHEMA_URL
            # NOTE: lxml/xpath is strange: if no named namespace, you have assign it a default
            # otherwise to matches are ever found in the schema with the xpath() method
            if value == BUILDINGSYNC_SCHEMA_URL:
                self.key = key
                if self.key != '' and self.key is not None:
                    self.namespaces[key] = value
                    etree.register_namespace(key, value)
                    # also add the colon
                    self.key = self.key + ":"
                else:
                    # make up a prefix since it's blank and assign it the key
                    key = 'auc'
                    self.namespaces[key] = value
                    etree.register_namespace(key, value)
                    self.key = 'auc:'
                break
        logger.debug("Namespaces set to: {}".format(self.namespaces))
        if not namespaces:
            raise BSyncProcessorError('No namespace was found in this file. Please modify your file and try again.')

    def get_namespaces(self) -> dict[str, str]:
        """ return namespaces """
        return self.namespaces

    def get_doc(self) -> etree:
        """ return parsed xml doc """
        return self.doc

    def get_sections(self) -> dict[str, Section]:
        """ return sections """
        return self.sections

    def get_assets(self) -> list[Asset]:
        """ return asset data """
        return self.asset_data.assets

    def save(self, filename: Union[Path, str]) -> None:
        """ save assets data to JSON file
            :param filename: str, filename to save
        """
        with open(filename, 'w') as outfile:
            json.dump(dataclasses.asdict(self.asset_data), outfile, indent=4)

        logger.info('Assets saved to {}'.format(filename))

    def parse_xml(self) -> None:
        """parse xml file"""
        self.doc: etree = etree.parse(BytesIO(self.file_data))

    def convert_to_ns(self, path: str) -> str:
        """ modify the path to include the namespace (ns) prefix specified in the xml file
            :param path: str, xml xpath
            returns modified path
        """
        if self.key is None:
            raise BSyncProcessorError("key not set")

        parts = path.split('/')
        for i, p in enumerate(parts):
            if p != "" and p != ".":
                parts[i] = self.key + p

        newpath = "/".join(parts)

        if not newpath.startswith('/') and not newpath.startswith('.'):
            newpath = self.key + newpath

        return newpath

    def process_sections(self) -> None:
        """process Sections to get sqft info to calculate primary and secondary sqft served
           Grab breakdown within each section (Gross, Tenant, Unconditioned, etc)
        """
        # TODO: add try blocks
        r = self.xp(self.doc, '/BuildingSync/Facilities/Facility/Sites/Site/' +
                    'Buildings/Building/Sections/Section')
        for item in r:
            id = item.get('ID')
            self.sections[id] = Section(
                type=None,
                areas={},
            )

            types = self.xp(item, './SectionType')
            if types:
                self.sections[id].type = types[0].text

            fas = self.xp(item, './FloorAreas/FloorArea')
            for fa in fas:
                fatype = None
                faval = 0.0

                for child in fa:
                    if child.tag.endswith('FloorAreaType'):
                        fatype = child.text
                    elif child.tag.endswith('FloorAreaValue'):
                        faval = float(child.text)
                if fatype is not None:
                    self.sections[id].areas[fatype] = faval

        logger.debug("Sections set to: {}".format(self.sections))

    def extract(self) -> None:
        """extract and flatten assets data"""

        # first retrieve areas
        self.process_sections()

        # process json file
        for asset in self.asset_defs:
            logger.debug("...processing {}".format(asset.name))
            if 'sqft' in asset.type:
                self.process_sqft_asset(asset, asset.type)
            elif asset.type == 'num':
                self.process_count_asset(asset)
            elif 'age' in asset.type:
                self.process_age_asset(asset, asset.type)
            elif 'custom' in asset.type:
                self.process_custom_asset(asset)

        logger.debug('Assets: {}'.format(self.asset_data))

    def export_asset(self, name: str, value: Any) -> None:
        """ export asset to asset_data """
        # first round if value is a float
        if isinstance(value, float):
            value = round(value, self.round_digits)

        self.asset_data.assets.append(Asset(name, value))

    def export_asset_units(self, name: str, value: Optional[str]) -> None:
        """ export an asset's units
            append "Units" to name and save units name """
        if value != "No units":
            self.asset_data.assets.append(Asset(name=name + ' Units', value=value))

    def get_units(self, results: Union[list[SystemData], list[LightingData]]) -> Optional[str]:
        """ attempt to get units or return mixed if multiple units are listed """
        units = None
        if len(results) > 0:
            if isinstance(results[0], SystemData) and results[0].units is not None:
                units = results[0].units
            for res in results:
                if isinstance(res, SystemData) and res.units is not None and res.units != units:
                    # export "mixed" since we can't convert units, no units
                    units = 'mixed'
        return units

    def get_plant(self, item: ElementTree) -> Optional[ElementTree]:
        # TODO: condenser plant?
        plant = None
        the_type = self.get_heat_cool_type(item.tag)
        if the_type is not None:
            plantIDmatch = self.xp(item, './/' + 'Source' + the_type + 'PlantID')
            if len(plantIDmatch) > 0:
                # logger.debug(f"found a plant ID match: {plantIDmatch[0].attrib['IDref']}")
                plants = self.xp(self.doc, "//" + the_type + "Plant[@ID = '" + plantIDmatch[0].attrib['IDref'] + "']")
                # logger.debug(f"found {len(plants)} plant matches!")
                if len(plants) > 0:
                    plant = plants[0]

        return plant

    def get_heat_cool_type(self, asset: str) -> Optional[str]:
        the_type = None
        logger.debug(f"GETTING HEAT COOL TYPE FOR ASSET: {asset}")
        if 'Heating' in asset:
            the_type = 'Heating'
        if 'Cooling' in asset:
            the_type = 'Cooling'
        return the_type

    def hvac_search(self, item: ElementTree, asset: AssetDef) -> list[ElementTree]:
        """ Perform a 2-level search
            1. First look in HeatingAndCoolingSystems/<type>Sources/<type>Source
            2. If not there, look for a plant ID and look in there
            Can be reused for several assets
        """
        # method 1: find within HeatingAndCoolingSystems or DomesticHotWaterSystems
        matches = self.xp(item, './/' + asset.key)
        # expects 0 or 1 match
        # logger.debug(f"number of matches for {item}: {len(matches)}")
        if len(matches) == 0:
            # method 2: follow Source<type>PlantID and look in there
            plant = self.get_plant(item)
            if plant is not None:
                # now get asset key within this element
                matches = self.xp(plant, './/' + asset.key)

        return matches

    def process_age_asset(self, asset: AssetDef, process_type: str) -> None:
        """ retrieves, in order, either 'YearOfManufacture' or YearInstalled' element of an equipment type
            returns either the oldest or newest, as specified.
            for weighted average processing order: 1) installed power (not implemented), 2) capacity, 3) served space area
        """
        results: list[SystemData] = []
        items = self.xp(self.doc, asset.parent_path)

        for item in items:
            matches = self.xp(item, './/' + asset.key)
            for m in matches:
                # priority 1: YearOfManufacture
                years = self.xp(m, './/YearOfManufacture')
                if len(years) == 0:
                    # priority 2: YearInstalled
                    years = self.xp(m, './/YearInstalled')
                if len(years) == 0:
                    # SPECIAL Case for HVAC HeatingSource / CoolingSource Equipment: can find plantID and look for
                    # YearInstalled there
                    if m.tag.endswith('HeatingSource') or m.tag.endswith('CoolingSource'):
                        plant = self.get_plant(m)
                        if plant is not None:
                            years = self.xp(plant, './/YearInstalled')

                if years:
                    match = years[0]
                    res = SystemData(
                        value=match.text,
                    )
                    if process_type.endswith('average'):
                        # check for capacity
                        cap, cap_units = self.get_capacity(match)
                        res.cap = cap
                        res.cap_units = cap_units
                        # check for sqft
                        sqft_total = 0.0
                        # EEK this will vary wildly
                        hvac_system = item.getparent().getparent().getparent()
                        linked_sections = self.xp(hvac_system, './/' + 'LinkedSectionID')
                        for ls in linked_sections:
                            sqft_total += self.compute_sqft(ls)
                        res.sqft = sqft_total

                    results.append(res)
        logger.debug(f"RESULTS for {asset.export_name}: {results}")

        # set units
        units: Optional[str] = "No units"
        if asset.export_units:
            units = None

        self.formatter.format_age_results(asset.export_name, results, process_type, units)

    def process_count_asset(self, asset: AssetDef) -> None:
        """ process count asset """
        # if there are keys, total is num of keys
        # else total is None
        items = self.xp(self.doc, asset.parent_path)
        all_matches = [self.xp(item, './/' + asset.key) for item in items]
        all_matches = [matches for matches in all_matches if matches]
        if all_matches == []:
            total = None
        else:
            total = sum([len(m) for m in all_matches])

        # set units
        units: Optional[str] = "No units"
        if asset.export_units is True:
            units = None
            if asset.units is not None:
                units = asset.units

        self.export_asset(asset.export_name, total)
        self.export_asset_units(asset.export_name, units)

    def process_sqft_asset(self, asset: AssetDef, process_type: str) -> None:
        """ process sqft asset
            either a ranking by total sqft or a weighted average
        """
        results: dict[str, float] = {}
        items = self.xp(self.doc, asset.parent_path)

        for item in items:
            sqft_total = 0.0
            matches = self.xp(item, './/' + asset.key)

            # special processing for UDFs
            if asset.key.endswith('UserDefinedField'):
                matches = self.find_udf_values(matches, asset.name)

            for match in matches:
                # get asset label and initialize results array in not done already
                if isinstance(match, str):
                    label = match
                else:
                    label = match.text
                if label not in results:
                    results[label] = 0.0

                sqft_total = self.get_linked_section_sqft(item)
                results[label] += sqft_total

        # store results
        logger.debug("process type: {}".format(process_type))
        logger.debug(f"RESULTS for {asset.export_name}: {results}")

        # set units
        units: Optional[str] = "No units"
        if asset.export_units:
            units = None
            if asset.units is not None:
                units = asset.units

        if process_type == 'sqft':
            self.formatter.format_sqft_results(asset.export_name, results, units)
        elif process_type == 'avg_sqft':
            self.formatter.format_avg_sqft_results(asset.export_name, results, units)

    def process_custom_asset(self, asset: AssetDef) -> None:
        # use this to make a 'switch statement for all custom assets'
        # making this super explicit for now.
        # This function should contain all of the little variations
        # Functions downstream should be more generic
        name_of_units_field = {
            'AnnualHeatingEfficiency': 'AnnualHeatingEfficiencyUnits',
            'AnnualCoolingEfficiency': 'AnnualCoolingEfficiencyUnits',
            'WaterHeaterEfficiency': 'WaterHeaterEfficiencyType'
        }

        # get name of units field to calculate
        units_to_export = None
        if asset.name in name_of_units_field:
            # found the name holding the units field
            units_to_export = name_of_units_field[asset.name]

        custom_assets: dict[str, Callable[[], Union[list[SystemData], list[LightingData]]]] = {
            'AnnualHeatingEfficiency': lambda: self.process_system(asset, units_to_export),
            'AnnualCoolingEfficiency': lambda: self.process_system(asset, units_to_export),
            'PrimaryFuel': lambda: self.process_system(asset, units_to_export),
            'ElectrificationPotential': lambda: self.process_system(asset, units_to_export),
            'WaterHeaterEfficiency': lambda: self.process_system(asset, units_to_export),
            'LightingSystemEfficiency': lambda: process_buildings_lighting_systems(self)
        }

        # these will get formated with the 80% function and lighting respectively (rest will use custom avg)
        assets_80_percent = ['PrimaryFuel']
        assets_lighting = ['LightingSystemEfficiency']

        results: Union[list[SystemData], list[LightingData]]
        if asset.name in custom_assets:
            results = custom_assets[asset.name]()
        else:
            logger.warn(f"Custom Processing for {asset.name} has not been implemented. Asset will be ignored.")
            results = []  # type: ignore

        # calculate actual units
        units: Optional[str] = "No units"
        if asset.export_units:
            if asset.units is not None:
                units = asset.units
            else:
                units = self.get_units(results)

        if asset.name in assets_80_percent:
            self.formatter.format_80_percent_results(asset.export_name, results, units)  # type: ignore
        elif asset.name in assets_lighting:
            self.formatter.format_lighting_results(asset.export_name, results, units)  # type: ignore
        elif asset.name == "ElectrificationPotential":
            self.formatter.format_electrification_pontential(asset.export_name, results, units)  # type: ignore
        else:
            self.formatter.format_custom_avg_results(asset.export_name, results, units)  # type: ignore

    def process_system(self, asset: AssetDef, units_keyname: Optional[str]) -> list[SystemData]:
        """ Process Heating/Cooling and DomesticHotWater System Assets
            order to check in:
            3) 1 SPECIAL CASE - Heating Efficiency: check under HeatingSource/HeatingSourceType/Furnace
            and use ThermalEfficiency with units of "Thermal Efficiency"
        """
        results: list[SystemData] = []
        matches = []
        items = self.xp(self.doc, asset.parent_path)

        for item in items:

            matches = self.hvac_search(item, asset)
            # special case for Efficiency (3rd priority)
            if 'Efficiency' in asset.name and len(matches) == 0:
                # look for ThermalEfficiency under HeatingSourceType/<type>
                matches = self.xp(item, './/' + 'ThermalEfficiency')

            # this should be same for all methods
            for match in matches:
                units = None
                if units_keyname is not None and units_keyname != "No units":
                    unit_match = self.xp(match.getparent(), './/' + units_keyname)

                    if len(unit_match) > 0:
                        units = unit_match[0].text
                    elif 'ThermalEfficiency' in match.tag:
                        # special case for Heating Efficiency
                        units = "Thermal Efficiency"

                # check for capacity
                cap, cap_units = self.get_capacity(match)

                # check sqft (LinkedPremises & LinkedSectionID
                sqft_total = self.get_linked_section_sqft(item)

                results.append(
                    SystemData(
                        value=match.text,
                        units=units,
                        cap=cap,
                        cap_units=cap_units,
                        sqft=sqft_total
                    )
                )

        logger.debug(f"RESULTS for {asset.export_name}: {results}")
        return results

    def get_linked_section_sqft(self, item: ElementTree) -> float:
        """ Find LinkedPremises at the right level (2 down from Systems)
            and calculate total sqft from the sections returned
        """
        if self.key is None:
            raise BSyncProcessorError("key not set")

        sqft_total = 0.0
        linked_sections = []
        path = self.doc.getpath(item)
        paths = path.split('/')

        # get sqft this asset applies to (2 methods)
        if paths[-1].endswith('Section'):
            # 1: key is within a Section element
            # within a section, grab ID to retrieve sqft
            id = item.get('ID')
            sqft_total += self.retrieve_sqft(id)

        else:
            # 2: assume LinkedPremises section within this path

            # special case for Systems (recurse up to 2 levels past "Systems")
            if 'Systems' in path:
                system = item
                sys_idx = paths.index(self.key + 'Systems') if self.key + 'Systems' in paths else -1
                # logger.debug(f"INDEX of Systems: {sys_idx}")
                if sys_idx > 0:
                    # get_parent() recurse backwards to 2 levels past Systems
                    diff = len(paths) - 1 - (sys_idx + 2)
                    for x in range(diff):
                        system = system.getparent()

                logger.debug(f"Assuming linked premises is in element: {self.doc.getpath(system)}")
                linked_sections = self.xp(system, './/' + 'LinkedSectionID')

            else:
                linked_sections = self.xp(item, './/' + 'LinkedSectionID')

            for ls in linked_sections:
                sqft_total += self.compute_sqft(ls)

        return sqft_total

    def get_capacity(self, el: etree) -> Tuple[Optional[str], Optional[str]]:
        """ Capacity order:
        1) HVACSystem/HeatingAndCoolingSystems/HeatingSources/HeatingSource/Capacity and CapacityUnits
        2) HVACSystem/HeatingAndCoolingSystems/HeatingSources/HeatingSource/OutputCapacity (deprecation soon)
        3) HVACSystem/HeatingPlants/HeatingPlant/<tech>/Capacity and CapacityUnits
        4) HVACSystem/HeatingPlants/HeatingPlant/<tech>/OutputCapacity (deprecation soon)
        """
        cap = None
        cap_units = None
        path = el.getparent()
        # for ThermalEfficiency, need to go up 3 levels
        if 'ThermalEfficiency' in el.tag:
            path = path.getparent().getparent()

        # prefer Capacity over OutputCapacity as it will be deprecated
        matches = self.xp(path, './/' + 'Capacity')
        if len(matches) == 0:
            matches = self.xp(path, './/' + 'OutputCapacity')
        if matches:
            # expects 0 or 1
            for idx, match in enumerate(matches):
                cap = match.text
                unit_match = self.xp(path, './/' + 'CapacityUnits')
                if len(unit_match) > 0:
                    cap_units = unit_match[0].text
                elif 'ThermalEfficiency' in el.tag:
                    cap_units = 'Thermal Efficiency'
        return cap, cap_units

    def find_udf_values(self, matches: list[ElementTree], name: str) -> list[Optional[str]]:
        """ processes a list of UDF matches
            retrieves the FieldValue whose FieldName matches the name passed in
            returns an array of values
        """
        results = []
        for match in matches:
            keep = 0
            tmp_val = None
            for child in list(match):
                if child.tag.endswith('FieldName') and child.text == name:
                    keep = 1
                if child.tag.endswith('FieldValue'):
                    tmp_val = child.text

            if keep == 1:
                results.append(tmp_val)

        return results

    def clean_name(self, name: str) -> str:
        """ clean keyname """
        name = name.replace('HVAC', 'Hvac').replace(' ', '')
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def xp(self, element: ElementTree, path: str) -> list[ElementTree]:
        """use xpath function and specify namespace
        Returns results of xpath operation
        """
        newpath = self.convert_to_ns(path)
        return element.xpath(newpath, namespaces=self.namespaces)

    def retrieve_sqft(self, section_id: str) -> float:
        """ retrieves square footage given the sectionID
            assumes 'Conditioned' if it exists; otherwise uses the 'Gross' floor area
            returns square footage
        """
        if section_id in self.sections:
            areas = self.sections[section_id].areas
            if 'Conditioned' in areas:
                return areas['Conditioned']
            elif 'Gross' in areas:
                return areas['Gross']

        raise BSyncProcessorError(
            'Error retrieving section sqft...No Conditioned area or Gross area found for section {}'.format(section_id)
        )

    def compute_sqft(self, section: ElementTree) -> float:
        """ compute square footage by either percentage or value method
            returns sum of squarefootages the asset is applied to in the LinkedSection
            the type of floor area to use in the calculation should be specified with "FloorAreaType" element.
        """
        sid = section.get('IDref')
        sqft = 0.0
        floor_areas = self.xp(section, './/FloorAreas/FloorArea')
        for f in floor_areas:
            # get types and percentages and add to running total
            the_type = self.xp(f, './/FloorAreaType')[0].text
            # this could be percentage or value
            percent = self.xp(f, './/FloorAreaPercentage')
            if percent and the_type in self.sections[sid].areas:
                logger.debug('type: {}, section: {}, areas: {}'.format(the_type, sid, self.sections[sid].areas))
                sqft += float(percent[0].text) * self.sections[sid].areas[the_type] / 100
            else:
                # get value instead
                val = self.xp(f, './/FloorAreaValue')
                if val:
                    sqft += float(val[0].text)

        return sqft

    @classmethod
    def get_default_asset_defs(cls) -> list[AssetDef]:
        assets_defs_filename = DEFAULT_ASSETS_DEF_FILE
        file = files('buildingsync_asset_extractor.config').joinpath(assets_defs_filename).read_text()
        return [
            AssetDef(**asset_def)
            for asset_def in json.loads(file)['asset_definitions']
        ]

    def _get_user_defined_feilds(self, element: etree.Element) -> list[Tuple[str, str]]:
        """Return (name, value) tuples of UserDefinedFields in element.
        """
        res = []
        user_defined_feilds = self.xp(element, './/' + 'UserDefinedField')

        for user_defined_feild in user_defined_feilds:
            name = next(iter(self.xp(user_defined_feild, './/' + 'FieldName')), None)
            value = next(iter(self.xp(user_defined_feild, './/' + 'FieldValue')), None)

            if name is not None and name.text and value is not None and value.text:
                res.append((name.text, value.text))

        return res
