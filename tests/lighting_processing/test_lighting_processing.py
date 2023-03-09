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
import unittest
from pathlib import Path

from lxml import etree

from buildingsync_asset_extractor.processor import BSyncProcessor

linked_section_with_floor_area_percentage = etree.XML('''
    <acc:LinkedSectionID
        IDref="Section-69928578013460"
        xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
    >
        <acc:FloorAreas>
            <acc:FloorArea>
                <acc:FloorAreaType>Common</acc:FloorAreaType>
                <acc:FloorAreaPercentage>50.0</acc:FloorAreaPercentage>
            </acc:FloorArea>
        </acc:FloorAreas>
    </acc:LinkedSectionID>
''')

linked_section_with_floor_area_value = etree.XML('''
    <acc:LinkedSectionID
        IDref="Section-69928578013460"
        xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
    >
        <acc:FloorAreas>
            <acc:FloorArea>
                <acc:FloorAreaType>Common</acc:FloorAreaType>
                <acc:FloorAreaValue>50.0</acc:FloorAreaValue>
            </acc:FloorArea>
        </acc:FloorAreas>
    </acc:LinkedSectionID>
''')


class TestBSyncProcessor(unittest.TestCase):
    def setUp(self):
        self.testfile = Path(__file__).parents[1] / 'files' / 'completetest.xml'
        self.no_ns_testfile = Path(__file__).parents[1] / 'files' / 'testfile2.xml'
        self.output_dir = Path(__file__).parents[1] / 'output'
        self.out_file = 'testoutput.json'
        self.out_file_2 = 'testoutput_2.json'
        self.test_assets_file = Path(__file__).parents[1] / 'files' / 'test_asset_defs.json'
        self.num_assets_to_extract = 23
        self.num_sections_in_testfile = 3

        # create output dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("TESTFILE: {}".format(self.testfile))
        self.bp = BSyncProcessor(self.testfile)

    def test_process_lighting_method_1(self):
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 1 lighting system
        method_1_ls = etree.XML('''
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:InstalledPower> 1.0 </acc:InstalledPower>
                <acc:InstalledPower> 2.0 </acc:InstalledPower>
                <acc:PercentPremisesServed> 3.0 </acc:PercentPremisesServed>
                <acc:PercentPremisesServed> 4.0 </acc:PercentPremisesServed>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        ''')
        lighting_systems.append(method_1_ls)

        # add sections to lighting system
        section = self.bp.xp(method_1_ls, './/LinkedPremises/Section')[0]
        section.append(linked_section_with_floor_area_percentage)
        section.append(linked_section_with_floor_area_value)

        # Action #
        results = self.bp.process_lighting(asset={
            "parent_path": lighting_systems_path + "/LightingSystem",
            'export_name': 'Lighting System Efficiency',
        })

        # Assertion #
        [method_1_results] = results
        assert method_1_results == {
            'power': 1.0,  # first InstalledPower
            'sqft_percent': 3.0,  # first PercentPremisesServed
            'sqft': 7550.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
        }

    def test_process_lighting_method_2_a(self):
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 2 lighting system
        method_2_ls = etree.XML('''
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LampPower> 2 </acc:LampPower>
                <acc:NumberOfLampsPerLuminaire> 3 </acc:NumberOfLampsPerLuminaire>
                <acc:NumberOfLuminaires> 4 </acc:NumberOfLuminaires>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        ''')
        lighting_systems.append(method_2_ls)

        # add sections to lighting system
        section = self.bp.xp(method_2_ls, './/LinkedPremises/Section')[0]
        section.append(linked_section_with_floor_area_percentage)
        section.append(linked_section_with_floor_area_value)

        # Action #
        results = self.bp.process_lighting(asset={
            "parent_path": lighting_systems_path + "/LightingSystem",
            'export_name': 'Lighting System Efficiency',
        })

        # Assertion #
        [method_2_ls] = results
        assert method_2_ls == {
            'power': 24,  # LampPower * NumberOfLampsPerLuminaire * NumberOfLuminaires
            'sqft': 7550.0  # sum of get_linked_section_sqft(...) for each LinkedSectionID
        }

    def test_process_lighting_method_2_b(self):
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 2 lighting system
        method_2_ls = etree.XML('''
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LampPower> 2 </acc:LampPower>
                <acc:NumberOfLampsPerLuminaire> 3 </acc:NumberOfLampsPerLuminaire>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        ''')
        lighting_systems.append(method_2_ls)

        # add user defined feilds to lighting system
        good_field = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> Quantity Of Luminaires For </acc:FieldName>
                <acc:FieldValue> 2 </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        bad_name_feild = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> irrelevant </acc:FieldName>
                <acc:FieldValue> 3 </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        bad_value_field = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> Quantity Of Luminaires For </acc:FieldName>
                <acc:FieldValue> bad value </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        method_2_ls.append(good_field)
        method_2_ls.append(bad_name_feild)
        method_2_ls.append(bad_value_field)

        # add sections to lighting system
        section = self.bp.xp(method_2_ls, './/LinkedPremises/Section')[0]
        section.append(linked_section_with_floor_area_percentage)
        section.append(linked_section_with_floor_area_value)

        # Action #
        results = self.bp.process_lighting(asset={
            "parent_path": lighting_systems_path + "/LightingSystem",
            'export_name': 'Lighting System Efficiency',
        })

        # Assertion #
        [method_2_ls] = results
        assert method_2_ls == {
            'power': 12,  # LampPower * NumberOfLampsPerLuminaire * sum of valid/relevant UserDefinedFields
            'sqft': 7550.0  # sum of get_linked_section_sqft(...) for each LinkedSectionID
        }

    def test_process_lighting_method_3(self):
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 3 lighting system
        method_3_ls = etree.XML('''
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        ''')
        lighting_systems.append(method_3_ls)

        # add user defined feilds to lighting system
        good_field = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> Lighting Power Density For </acc:FieldName>
                <acc:FieldValue> 1 </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        bad_name_feild = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> irrelevant </acc:FieldName>
                <acc:FieldValue> 2 </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        bad_value_field = etree.XML('''
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> Lighting Power Density For </acc:FieldName>
                <acc:FieldValue> bad value </acc:FieldValue>
            </acc:UserDefinedField>
        ''')
        method_3_ls.append(good_field)
        method_3_ls.append(bad_name_feild)
        method_3_ls.append(bad_value_field)

        # add sections to lighting system
        section = self.bp.xp(method_3_ls, './/LinkedPremises/Section')[0]
        section.append(linked_section_with_floor_area_percentage)
        section.append(linked_section_with_floor_area_value)

        # Action #
        results = self.bp.process_lighting(asset={
            "parent_path": lighting_systems_path + "/LightingSystem",
            'export_name': 'Lighting System Efficiency',
        })

        # Assertion #
        [method_3_results] = results
        assert method_3_results == {
            'lpd': 1.0,  # sum of valid/relevant UserDefinedFields
            'sqft': 7550.0  # sum of get_linked_section_sqft(...) for each LinkedSectionID
        }
