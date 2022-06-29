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
import json
import logging
import re
from io import BytesIO
from typing import Optional

from importlib_resources import files
from lxml import etree

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
                 filename: Optional[str] = None,
                 data: Optional[str] = None,
                 asset_defs_filename: Optional[str] = None,
                 logger_level: Optional[str] = 'INFO'):
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
            raise "You must provide either a filename or xml data"
        self.parse_xml()

        self.initialize_vars(asset_defs_filename)

    def initialize_vars(self, asset_defs_filename):
        # use default asset definitions file unless otherwise specified
        if asset_defs_filename:
            self.config_filename = asset_defs_filename
            # open abs path
            with open(self.config_filename, mode='rb') as file:
                self.asset_defs = json.load(file)['asset_definitions']
        else:
            self.config_filename = DEFAULT_ASSETS_DEF_FILE
            # open with importlib.resources
            file = files('buildingsync_asset_extractor.config').joinpath(self.config_filename).read_text()
            self.asset_defs = json.loads(file)['asset_definitions']

        self.namespaces = {}
        self.sections = {}
        self.asset_data = {'assets': []}
        # TODO: do we want to round answers?
        self.round_digits = 5

        # set namespaces
        self.key = None
        self.set_namespaces()

    def set_asset_defs_file(self, asset_defs_filename: str):
        # set and parse
        self.config_filename = asset_defs_filename
        with open(self.config_filename, mode='rb') as file:
            self.asset_defs = json.load(file)['asset_definitions']

    def get_asset_defs(self):
        """ return asset definitions array """
        return self.asset_defs

    def set_namespaces(self):
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
            raise Exception('No namespace was found in this file. Please modify your file and try again.')

    def get_namespaces(self):
        """ return namespaces """
        return self.namespaces

    def get_doc(self):
        """ return parsed xml doc """
        return self.doc

    def get_sections(self):
        """ return sections """
        return self.sections

    def get_assets(self):
        """ return asset data """
        return self.asset_data['assets']

    def save(self, filename: str):
        """ save assets data to JSON file
            :param filename: str, filename to save
        """
        with open(filename, 'w') as outfile:
            json.dump(self.asset_data, outfile, indent=4)

        logger.info('Assets saved to {}'.format(filename))

    def parse_xml(self):
        """parse xml file"""
        self.doc = etree.parse(BytesIO(self.file_data))

    def convert_to_ns(self, path: str):
        """ modify the path to include the namespace (ns) prefix specified in the xml file
            :param path: str, xml xpath
            returns modified path
        """
        # print('original  path: {}'.format(path))
        parts = path.split('/')
        for i, p in enumerate(parts):
            if p != "" and p != ".":
                parts[i] = self.key + p

        newpath = "/".join(parts)

        if not newpath.startswith('/') and not newpath.startswith('.'):
            newpath = self.key + newpath

        return newpath

    def process_sections(self):
        """process Sections to get sqft info to calculate primary and secondary sqft served
           Grab breakdown within each section (Gross, Tenant, Unconditioned, etc)
        """
        # TODO: add try blocks
        r = self.xp(self.doc, '/BuildingSync/Facilities/Facility/Sites/Site/' +
                    'Buildings/Building/Sections/Section')
        for item in r:
            id = item.get('ID')
            self.sections[id] = {}

            self.sections[id]['type'] = None
            types = self.xp(item, './SectionType')
            if types:
                self.sections[id]['type'] = types[0].text

            self.sections[id]['areas'] = {}

            fas = self.xp(item, './FloorAreas/FloorArea')
            for fa in fas:
                fatype = None
                faval = 0

                for child in fa:
                    if child.tag.endswith('FloorAreaType'):
                        fatype = child.text
                    elif child.tag.endswith('FloorAreaValue'):
                        faval = float(child.text)
                if fatype is not None:
                    self.sections[id]['areas'][fatype] = faval

        logger.debug("Sections set to: {}".format(self.sections))

    def extract(self):
        """extract and flatten assets data"""

        # first retrieve areas
        self.process_sections()

        # process json file
        for asset in self.asset_defs:
            logger.debug("...processing {}".format(asset['name']))
            if 'sqft' in asset['type']:
                self.process_sqft_asset(asset, asset['type'])
            elif asset['type'] == 'num':
                self.process_count_asset(asset)
            elif 'age' in asset['type']:
                self.process_age_asset(asset, asset['type'])
            elif 'custom' in asset['type']:
                self.process_custom_asset(asset)

        logger.debug('Assets: {}'.format(self.asset_data))

    def export_asset(self, name: str, value, units: str):
        """ export asset to asset_data """
        # first round if value is a float
        if isinstance(value, float):
            value = round(value, self.round_digits)

        self.asset_data['assets'].append({'name': name, 'value': value, 'units': units})

    def process_age_asset(self, asset: dict, process_type: str):
        """ retrieves, in order, either 'YearOfManufacture' or YearInstalled' element of an equipment type
            returns either the oldest or newest, as specified.
            for weighted average processing order: 1) installed power (not implemented), 2) capacity, 3) served space area
        """
        results = []
        items = self.xp(self.doc, asset['parent_path'])

        for item in items:
            matches = self.xp(item, './/' + asset['key'])
            for m in matches:
                res = {}
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
                    res['value'] = match.text
                    if process_type.endswith('average'):
                        # check for capacity
                        cap, cap_units = self.get_capacity(match)
                        res['cap'] = cap
                        res['cap_units'] = cap_units
                        # check for sqft
                        sqft_total = 0
                        # EEK this will vary wildly
                        hvac_system = item.getparent().getparent().getparent()
                        linked_sections = self.xp(hvac_system, './/' + 'LinkedSectionID')
                        for ls in linked_sections:
                            sqft_total += self.compute_sqft(ls)
                        res['sqft'] = sqft_total

                    results.append(res)
        logger.debug(f"RESULTS for {asset['export_name']}: {results}")
        self.format_age_results(asset['export_name'], results, process_type)

    def format_age_results(self, name: str, results: list, process_type):
        # process results
        value = None
        if process_type.endswith('oldest'):
            res_vals = [sub['value'] for sub in results if sub['value']]
            # print(f"res_vals: {res_vals}")
            s_res = sorted(res_vals)
            # print(f"s_res: {s_res}")
            if s_res:
                value = s_res[0]
            self.export_asset(name, str(value), None)

        elif process_type.endswith('newest'):
            res_vals = [sub['value'] for sub in results if sub['value']]
            s_res = sorted(res_vals, reverse=True)
            if s_res:
                value = s_res
            self.export_asset(name, str(value), None)

        elif process_type.endswith('average'):
            self.format_custom_avg_results(name, results)

    def process_count_asset(self, asset: dict):
        """ process count asset """

        total = 0
        found = None
        items = self.xp(self.doc, asset['parent_path'])
        for item in items:
            matches = self.xp(item, './/' + asset['key'])
            if matches:
                total += len(matches)
                found = 1

        # add null key if nothing found
        if not found:
            total = None
        self.export_asset(asset['export_name'], total, asset['units'])

    def process_sqft_asset(self, asset: dict, process_type: str):
        """ process sqft asset
            either a ranking by total sqft or a weighted average
        """
        results = {}
        items = self.xp(self.doc, asset['parent_path'])

        for item in items:
            sqft_total = 0
            matches = self.xp(item, './/' + asset['key'])

            # special processing for UDFs
            if asset['key'].endswith('UserDefinedField'):
                matches = self.find_udf_values(matches, asset['name'])

            for match in matches:
                # get asset label and initialize results array in not done already
                if isinstance(match, str):
                    label = match
                else:
                    label = match.text
                if label not in results:
                    results[label] = 0

                sqft_total = self.get_linked_section_sqft(item)
                results[label] += sqft_total

        # store results
        logger.debug("process type: {}".format(process_type))
        logger.debug(f"RESULTS for {asset['export_name']}: {results}")
        if process_type == 'sqft':
            self.format_sqft_results(asset['export_name'], results, asset['units'])
        elif process_type == 'avg_sqft':
            self.format_avg_sqft_results(asset['export_name'], results, asset['units'])

    def process_custom_asset(self, asset: dict):
        # use this to make a 'switch statement for all custom assets'
        # making this super explicit for now.
        # This function should contain all of the little variations
        # Functions downstream should be more generic
        name_of_units_field = {
            'AnnualHeatingEfficiency': 'AnnualHeatingEfficiencyUnits',
            'AnnualCoolingEfficiency': 'AnnualCoolingEfficiencyUnits',
            'PrimaryFuel':  None,
            'WaterHeaterEfficiency': 'WaterHeaterEfficiencyType',
            'LightingSystemEfficiency': None
        }

        custom_assets = {
            'AnnualHeatingEfficiency': lambda: self.process_system(asset, name_of_units_field[asset['name']]),
            'AnnualCoolingEfficiency': lambda: self.process_system(asset, name_of_units_field[asset['name']]),
            'PrimaryFuel': lambda: self.process_system(asset, name_of_units_field[asset['name']]),
            'WaterHeaterEfficiency': lambda: self.process_system(asset, name_of_units_field[asset['name']]),
            'LightingSystemEfficiency': lambda: self.process_lighting(asset, name_of_units_field[asset['name']])
        }

        # these will get formated with the 80% function (rest will use custom avg)
        assets_80_percent = ['PrimaryFuel']
        assets_lighting = ['LightingSystemEfficiency']

        results = custom_assets.get(asset['name'], lambda: "Error")()
        if isinstance(results, str) and 'Error' in results:
            logger.warn(f"Custom Processing for {asset['name']} has not been implemented. Asset will be ignored.")

        if asset['name'] in assets_80_percent:
            self.format_80_percent_results(asset['export_name'], results, name_of_units_field[asset['name']])
        elif asset['name'] in assets_lighting:
            self.format_lighting_results(asset['export_name'], results, 'W/ft2')
        else:
            self.format_custom_avg_results(asset['export_name'], results)

    def get_plant(self, item):
        # TODO: condenser plant?
        plant = None
        the_type = self.get_heat_cool_type(item.tag)
        if the_type is not None:
            plantIDmatch = self.xp(item, './/' + 'Source' + the_type + 'PlantID')
            if len(plantIDmatch) > 0:
                # print(f"found a plant ID match: {plantIDmatch[0].attrib['IDref']}")
                plants = self.xp(self.doc, "//" + the_type + "Plant[@ID = '" + plantIDmatch[0].attrib['IDref'] + "']")
                # print(f"found {len(plants)} plant matches!")
                if len(plants) > 0:
                    plant = plants[0]

        return plant

    def get_heat_cool_type(self, asset):
        the_type = None
        logger.debug(f"GETTING HEAT COOL TYPE FOR ASSET: {asset}")
        if 'Heating' in asset:
            the_type = 'Heating'
        if 'Cooling' in asset:
            the_type = 'Cooling'
        return the_type

    def hvac_search(self, item: dict, asset: dict):
        """ Perform a 2-level search
            1. First look in HeatingAndCoolingSystems/<type>Sources/<type>Source
            2. If not there, look for a plant ID and look in there
            Can be reused for several assets
        """
        # method 1: find within HeatingAndCoolingSystems or DomesticHotWaterSystems
        matches = self.xp(item, './/' + asset['key'])
        # expects 0 or 1 match
        # print(f"number of matches for {item}: {len(matches)}")
        if len(matches) == 0:
            # method 2: follow Source<type>PlantID and look in there
            plant = self.get_plant(item)
            if plant is not None:
                # now get asset key within this element
                matches = self.xp(plant, './/' + asset['key'])

        return matches

    def process_lighting(self, asset: dict, units_keyname):
        """ Process Lighting Efficiency asset
        method 1: InstalledPower * PercentPremisesServed
        method 2: Lamp Power * # Lamps per Luminaire * # Luminaire * Quantity
        method 3: Look in UDF for "Lighting Power Density For ..."
        method 4: Lookup table based on LightingSystemType / BallastType (todo)
        """
        results = []
        matches = []
        items = self.xp(self.doc, asset['parent_path'])

        for item in items:
            res = {}
            # method 1
            matches = self.xp(item, './/' + 'InstalledPower')
            if len(matches) > 0:
                res['power'] = float(matches[0].text)
                pmatches = self.xp(item, './/' + 'PercentPremisesServed')
                if len(pmatches) > 0:
                    res['sqft_percent'] = float(pmatches[0].text)

                # check sqft (LinkedPremises & LinkedSectionID)
                res['sqft'] = self.get_linked_section_sqft(item)

            if len(matches) == 0:
                # method 2
                matches = self.xp(item, './/' + 'LampPower')
                lmatches = self.xp(item, './/' + 'NumberOfLampsPerLuminaire')
                if len(matches) > 0 and len(lmatches) > 0:
                    # get # luminaires & quantity
                    nmatches = self.xp(item, './/' + 'NumberOfLuminaires')
                    if len(nmatches) > 0:
                        qmatches = self.xp(item, './/' + 'Quantity')
                        res['power'] = float(matches[0].text) * float(lmatches[0].text) * float(nmatches[0].text)
                        if len(qmatches) > 0:
                            res['power'] = res['power'] * float(qmatches[0].text)
                        res['sqft'] = self.get_linked_section_sqft(item)
                    else:
                        # try to get # luminaires a different way
                        # UDF: '* Quantity Of Luminaires For *'
                        # example: Common Areas Quantity Of Luminaires For Section-101919600
                        match_str = 'Quantity Of Luminaires For'

                        umatches = self.xp(item, './/' + 'UserDefinedField')
                        qty_val = 0
                        for match in umatches:
                            keep = 0
                            tmp_val = 0
                            for child in list(match):
                                if child.tag.endswith('FieldName') and match_str in child.text:
                                    keep = 1
                                if child.tag.endswith('FieldValue'):
                                    try:
                                        tmp_val = int(child.text)
                                    except Exception:
                                        pass

                            if keep == 1:
                                qty_val += tmp_val

                        if qty_val > 0:
                            # print(f"QUANTITY OF LUMINAIRES: {qty_val}")
                            res['power'] = res['power'] = float(matches[0].text) * float(lmatches[0].text) * qty_val
                            res['sqft'] = self.get_linked_section_sqft(item)

                if len(res) == 0:
                    # method 3: UDF for Lighting Power Density
                    udf_match_str = 'Lighting Power Density For'

                    matches = self.xp(item, './/' + 'UserDefinedField')
                    qty_val = 0
                    for match in matches:
                        keep = 0
                        tmp_val = 0
                        for child in list(match):
                            if child.tag.endswith('FieldName') and udf_match_str in child.text:
                                keep = 1
                            if child.tag.endswith('FieldValue'):
                                try:
                                    tmp_val = float(child.text)
                                except Exception:
                                    pass

                        if keep == 1:
                            qty_val += tmp_val

                    if qty_val > 0:
                        # print(f"LPD: {qty_val}")
                        res['lpd'] = qty_val
                        res['sqft'] = self.get_linked_section_sqft(item)

            # append if not empty
            if res:
                results.append(res)

        logger.debug(f"RESULTS for {asset['export_name']}: {results}")
        return results

    def process_system(self, asset: dict, units_keyname):
        """ Process Heating/Cooling and DomesticHotWater System Assets
            order to check in:
            3) 1 SPECIAL CASE - Heating Efficiency: check under HeatingSource/HeatingSourceType/Furnace
            and use ThermalEfficiency with units of "Thermal Efficiency"
        """
        results = []
        matches = []
        items = self.xp(self.doc, asset['parent_path'])

        for item in items:

            matches = self.hvac_search(item, asset)
            # special case for Efficiency (3rd priority)
            if 'Efficiency' in asset['name'] and len(matches) == 0:
                # look for ThermalEfficiency under HeatingSourceType/<type>
                matches = self.xp(item, './/' + 'ThermalEfficiency')

            # this should be same for all methods
            for match in matches:
                units = None
                if units_keyname is not None:
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

                results.append({'value': match.text, 'units': units, 'cap': cap, 'cap_units': cap_units, 'sqft': sqft_total})

        logger.debug(f"RESULTS for {asset['export_name']}: {results}")
        return results

    def get_linked_section_sqft(self, item: dict):
        """ Find LinkedPremises at the right level (2 down from Systems)
            and calculate total sqft from the sections returned
        """
        sqft_total = 0
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
                # print(f"INDEX of Systems: {sys_idx}")
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

    def get_capacity(self, el: dict):
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

    def remap_results(self, results: list):
        """ Remap results from a list of dictionaries to 4 lists """
        try:
            values = [sub['value'] if sub['value'] is None else float(sub['value']) for sub in results]
        except ValueError:
            values = [sub['value'] for sub in results]

        capacities = [sub['cap'] if sub['cap'] is None else float(sub['cap']) for sub in results]
        cap_units = [sub['cap_units'] for sub in results]
        sqfts = [sub['sqft'] if sub['sqft'] is None else float(sub['sqft']) for sub in results]

        return values, capacities, cap_units, sqfts

    def format_80_percent_results(self, name: str, results: list, units: str):
        """ format 80% rule results
            the "primary" type returned must at least serve 80% of the area by
            1. Capacity
            2. Served space area
        """
        if len(results) == 0:
            # export None
            self.export_asset(name, None, None)
            return

        values, capacities, cap_units, sqfts = self.remap_results(results)

        # if only 1 asset, we'll call it primary!
        if len(values) == 1:
            self.export_asset(name, values[0], units)
            return

        if None not in capacities and len(set(cap_units)) <= 1:
            # capacity method
            # add all capacities
            # pick largest one and make sure it's 80% of total
            found = 0
            total = sum(capacities)
            if total > 0:
                primaries = {}
                for res in results:
                    if res['value'] not in primaries:
                        primaries[res['value']] = 0
                    primaries[res['value']] += float(res['cap'])

                for p in primaries:
                    if float(primaries[p])/total >= 0.8:
                        # this fuel meets the 80% threshold by capacity
                        found = 1
                        self.export_asset(name, p, units)
                        return

            if found == 0:
                # nothing matched this criteria, return 'Mixed'
                self.export_asset(name, 'mixed', units)
                return

        if None not in sqfts:
            # sqft method
            total = sum(sqfts)
            found = 0
            if total > 0:
                primaries = {}
                for res in results:
                    if res['value'] not in primaries:
                        primaries[res['value']] = 0
                    primaries[res['value']] += res['sqft']

                for p in primaries:
                    if float(primaries[p])/total >= 0.8:
                        # this fuel meets the 80% threshold by capacity
                        found = 1
                        self.export_asset(name, p, units)
                        return

            if found == 0:
                # nothing matched this criteria, return 'Mixed'
                self.export_asset(name, 'mixed', units)
                return

        # still here? return unknown
        self.export_asset(name, 'unknown', units)
        return

    def format_lighting_results(self, name: str, results: list, units: str):
        """ custom processing for lighting efficiency
            1. if 'lpd' is present, average the values
            2. else if percentpremisesserved
            3. otherwise regular sqft
        """
        if len(results) == 0:
            # export None
            self.export_asset(name, None, None)
            return

        # check method 1
        has_lpd = 1
        for r in results:
            try:
                r['lpd']
            except Exception:
                has_lpd = 0

        # for weighted average, re-find Watts from LPD and LinkedPremises and divide by total sqft
        if has_lpd:
            value = 0
            total_sqft = 0
            for r in results:
                value += r['lpd'] * r['sqft']
                total_sqft += r['sqft']
            if value > 0:
                value = value / total_sqft

            self.export_asset(name, value, units)
            return

        # check method 2
        # need both PercentPremises AND LinkedPremises for this
        # running sum of all watts / running sum of all fractions of sqft
        has_perc = 1
        for r in results:
            try:
                r['sqft_percent']
                r['sqft']
            except Exception:
                has_perc = 0
        if has_perc:
            power = 0
            sqft_total = 0
            for r in results:
                power += power
                sqft_total = r['sqft_percent'] / 100 * r['sqft']
            if power > 0:
                value = power / sqft_total
            self.export_asset(name, value, units)
            return

        # check method 3
        sqfts = [sub['sqft'] if sub['sqft'] is None else float(sub['sqft']) for sub in results]
        if None not in sqfts:
            # sqft methods
            remapped_power = [sub['power'] for sub in results]
            remapped_sqft = [sub['sqft'] for sub in results]
            top = sum(remapped_power)
            bottom = sum(remapped_sqft)
            if bottom > 0:
                value = top / bottom
                self.export_asset(name, value, units)
                return

        # can't calculate
        self.export_asset(name, 'unknown', units)
        return

    def format_custom_avg_results(self, name: str, results: list):
        """ format weighted average
            1. Ensure all units are the same
            2. Attempt to calculate with installed power (NOT IMPLEMENTED)
            3. Attempt to calculate with capacity (cap)
            4. Attempt to calculate with served space area (sqrt)
        """

        if len(results) == 0:
            # export None
            self.export_asset(name, None, None)
            return

        # 1 - check units
        units = None
        if 'units' in results[0].keys():
            units = results[0]['units']
        for res in results:
            if 'units' in res.keys() and res['units'] != units:
                # export "mixed" since we can't convert units
                self.export_asset(name, 'mixed', None)
                return

        values, capacities, cap_units, sqfts = self.remap_results(results)

        # print(f"values: {values}")
        # print(f"capacities: {capacities}")
        # print(f"length: {len(set(cap_units)) <= 1}")

        # 2 - capacity
        # check that there are capacities for all and the units are all the same
        if None not in capacities and len(set(cap_units)) == 1:
            # capacity methods
            cap_total = 0
            eff_total = 0
            for res in results:
                cap_total = cap_total + float(res['cap'])
                eff_total = eff_total + (float(res['value']) * float(res['cap']))
            total = eff_total / cap_total

            # special case for average age: take the floor since partial year doesn't make sense
            if name.lower().endswith('age'):
                total = str(int(total))

            self.export_asset(name, total, units)
            return

        elif None not in sqfts:
            # sqft methods
            remapped_res = {sub['value']: sub['sqft'] for sub in results}
            self.format_avg_sqft_results(name, remapped_res, units)
            return
        else:
            # just average
            total = sum(values)/len(values)
            # special case for average age: take the floor since partial year doesn't make sense
            if name.lower().endswith('age'):
                total = int(total)
            self.export_asset(name, total, units)
            return

    def format_sqft_results(self, name: str, results: list, units: str):
        """ return primary and secondary for top 2 results by sqft """
        # NOTE: this is the only method that modifies the export name '
        # by appending 'primary' and 'secondary'

        # filter and sort results
        filtered_res = {k: v for k, v in results.items() if v != 0}
        s_res = dict(sorted(filtered_res.items(), key=lambda kv: kv[1], reverse=True))
        logger.debug('sorted results with zeros removed: {}'.format(s_res))

        value = None
        value2 = None

        s_keys = list(s_res.keys())
        if s_keys:
            value = s_keys[0]
        self.export_asset('Primary ' + name, value, units)
        if (len(s_keys) > 1):
            value2 = s_keys[1]
        self.export_asset('Secondary ' + name, value2, units)

    def format_avg_sqft_results(self, name: str, results: list, units: str):
        """ weighted average of results """

        # in this case the result keys will convert to numbers
        # to calculate the weighted average

        total = None

        if results:
            total_sqft = sum(results.values())

            running_sum = 0
            for k, v in results.items():
                running_sum += float(k) * v
            if running_sum > 0 and total_sqft > 0:
                total = running_sum / total_sqft

        # special case for average age: take the floor since partial year doesn't make sense
        if name.lower().endswith('age') and total is not None:
            total = str(int(total))

        # add to assets
        self.export_asset(name, total, units)

    def find_udf_values(self, matches: list, name: str):
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

    def clean_name(self, name: str):
        """ clean keyname """
        name = name.replace('HVAC', 'Hvac').replace(' ', '')
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def xp(self, element: dict, path: str):
        """use xpath function and specify namespace
        Returns results of xpath operation
        """
        newpath = self.convert_to_ns(path)
        return element.xpath(newpath, namespaces=self.namespaces)

    def retrieve_sqft(self, section_id: str):
        """ retrieves square footage given the sectionID
            assumes 'Conditioned' if it exists; otherwise uses the 'Gross' floor area
            returns square footage
        """
        if section_id in self.sections and 'areas' in self.sections[section_id]:
            areas = self.sections[section_id]['areas']
            if 'Conditioned' in areas:
                return areas['Conditioned']
            elif 'Gross' in areas:
                return areas['Gross']

        raise Exception('Error retrieving section sqft...No Conditioned area or Gross area found for section {}'.format(section_id))

    def compute_sqft(self, section: dict):
        """ compute square footage by either percentage or value method
            returns sum of squarefootages the asset is applied to in the LinkedSection
            the type of floor area to use in the calculation should be specified with "FloorAreaType" element.
        """
        sid = section.get('IDref')
        sqft = 0
        floor_areas = self.xp(section, './/FloorAreas/FloorArea')
        for f in floor_areas:
            # get types and percentages and add to running total
            the_type = self.xp(f, './/FloorAreaType')[0].text
            # this could be percentage or value
            percent = self.xp(f, './/FloorAreaPercentage')
            if percent:
                logger.debug('type: {}, section: {}, areas: {}'.format(the_type, sid, self.sections[sid]['areas']))
                sqft += float(percent[0].text) * self.sections[sid]['areas'][the_type] / 100
            else:
                # get value instead
                val = self.xp(f, './/FloorAreaValue')
                if val:
                    sqft += float(val[0].text)

        return sqft

    @classmethod
    def get_default_asset_defs(cls):
        assets_defs_filename = DEFAULT_ASSETS_DEF_FILE
        file = files('buildingsync_asset_extractor.config').joinpath(assets_defs_filename).read_text()
        return json.loads(file)['asset_definitions']
