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
import sys

from lxml import etree

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('logfile.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

# BuildingSync Schema location
BUILDINGSYNC_SCHEMA_URL = "http://buildingsync.net/schemas/bedes-auc/2019"


# Processor class loads an XML file and extracts assets
class BSyncProcessor:

    def __init__(self, filename: str):
        """class instantiator
          :param filename: str, xml to parse
        """
        # takes in a XML file to process

        self.filename = filename
        self.config_filename = 'buildingsync_asset_extractor/config/asset_definitions.json'
        self.namespaces = {}
        self.doc = None
        self.sections = {}
        self.asset_data = {}

        # set namespaces
        self.key = None
        self.set_namespaces()

        # parse file
        self.parse_xml()

    def set_namespaces(self):
        """set namespaces from xml file"""

        with open(self.filename, mode='rb') as file:

            namespaces = {node[0]: node[1] for _, node in etree.iterparse(file, events=['start-ns'])}

            for key, value in namespaces.items():
                # only register the namespace that matches BUILDGINSYNC_SCHEMA_URL
                # NOTE: lxml/xpath is strange: if no named namespace, you have assign it a default
                # otherwise to matches are ever found in the schema with the xpath() method
                if value == BUILDINGSYNC_SCHEMA_URL:
                    self.key = key
                    if self.key != '':
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
        return self.asset_data

    def save(self, filename: str):
        """ save assets data to JSON file
            :param filename: str, filename to save
        """
        with open(filename, 'w') as outfile:
            json.dump(self.asset_data, outfile, indent=4)

        logger.info('Assets saved to {}'.format(filename))

    def parse_xml(self):
        """parse xml file"""
        with open(self.filename, mode='rb') as file:
            self.doc = etree.parse(file)

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
        with open(self.config_filename, mode='rb') as file:
            asset_defs = json.load(file)

        for asset in asset_defs['definitions']:
            logger.debug("...processing {}".format(asset['name']))
            if 'sqft' in asset['type']:
                self.process_sqft_asset(asset, asset['type'])
            elif asset['type'] == 'num':
                self.process_count_asset(asset)
            elif 'age' in asset['type']:
                self.process_age_asset(asset, asset['type'])

        logger.debug('Assets: {}'.format(self.asset_data))

    def process_age_asset(self, asset: dict, process_type: str):
        """ retrieves the 'YearInstalled' element of an equipment type
            returns either the oldest or youngest, as specified.
        """
        results = []
        items = self.xp(self.doc, asset['parent_path'])

        for item in items:
            matches = self.xp(item, './/' + asset['key'])
            if matches:
                # found a match for asset
                years = self.xp(item, './/YearInstalled')
                if years:
                    results.append(years[0].text)

        # get seed name
        keyname = self.clean_name(asset['name'])

        # process results
        value = None
        if process_type.endswith('oldest'):
            s_res = sorted(results, reverse=True)
            if s_res:
                value = s_res[0]
            self.asset_data['oldest_installed_' + keyname] = value
        elif process_type.endswith('youngest'):
            s_res = sorted(results)
            if s_res:
                value = s_res
            self.asset_data['youngest_installed_' + keyname] = value

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

        keyname = self.clean_name(asset['name'])
        # add null key if nothing found
        if not found:
            total = None
        self.asset_data['total_' + keyname] = total

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
                label = match.text
                if label not in results:
                    results[label] = 0

                # get sqft this asset applies to (2 methods)
                if asset['parent_path'].endswith('Section'):
                    # 1: key is within a Section element
                    # within a section, grab ID to retrieve sqft
                    id = item.get('ID')
                    results[label] += self.retrieve_sqft(id)

                else:
                    # 2: assume linked sections
                    linked_sections = self.xp(item, './/' + 'LinkedSectionID')
                    for ls in linked_sections:
                        sqft_total += self.compute_sqft(ls)

                    results[label] += sqft_total

        # store results
        logger.debug("process type: {}".format(process_type))
        if process_type == 'sqft':
            self.format_sqft_results(asset['name'], results)
        elif process_type == 'avg_sqft':
            self.format_avg_sqft_results(asset['name'], results)

    def format_sqft_results(self, name: str, results: list):
        """ return primary and secondary for top 2 results by sqft """

        # filter and sort results
        filtered_res = {k: v for k, v in results.items() if v != 0}
        s_res = dict(sorted(filtered_res.items(), key=lambda kv: kv[1], reverse=True))
        logger.debug('sorted results with zeros removed: {}'.format(s_res))

        # clean the seed keyname
        keyname = self.clean_name(name)
        value = None
        value2 = None

        s_keys = list(s_res.keys())
        if s_keys:
            value = s_keys[0]
        self.asset_data['primary_' + keyname] = value
        if (len(s_keys) > 1):
            value2 = s_keys[1]
        self.asset_data['secondary_' + keyname] = value2

    def format_avg_sqft_results(self, name: str, results: list):
        """ weighted average of results """

        # in this case the result keys will convert to numbers
        # to calculate the weighted average

        # clean the seed keyname
        keyname = self.clean_name(name)
        total = None

        if results:
            total_sqft = sum(results.values())

            running_sum = 0
            for k, v in results.items():
                running_sum += float(k) * v
            total = running_sum / total_sqft

        # add to assets
        self.asset_data[keyname] = total

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
                    tmp_val = child

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
        # print("newpath: {}".format(newpath))
        return element.xpath(newpath, namespaces=self.namespaces)

    def retrieve_sqft(self, section_id: str):
        """ retrieves square footage give the sectionID
            assumes 'Conditioned' if it exists; otherwise uses the 'Gross' floor area
            returns square footage
        """
        if self.sections[section_id] and self.sections[section_id]['areas']:
            areas = self.sections[section_id]['areas']
            if areas['Conditioned']:
                return areas['Conditioned']
            elif areas['Gross']:
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