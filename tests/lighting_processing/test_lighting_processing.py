"""
*********************************************************************************************************
:copyright (c) BuildingSync®, Copyright (c) 2015-2023, Alliance for Sustainable Energy, LLC,
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

from buildingsync_asset_extractor.lighting_processing.lighting_processing import (
    LightingDataLPD,
    LightingDataPower,
    process_buildings_lighting_systems,
)
from buildingsync_asset_extractor.processor import BSyncProcessor

SECTION_PATH = "/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building/Sections/Section"

linked_section_with_floor_area_percentage = etree.XML("""
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
""")

linked_section_with_floor_area_value = etree.XML("""
    <acc:LinkedSectionID
        IDref="Section-101919600"
        xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
    >
        <acc:FloorAreas>
            <acc:FloorArea>
                <acc:FloorAreaType>Common</acc:FloorAreaType>
                <acc:FloorAreaValue>50.0</acc:FloorAreaValue>
            </acc:FloorArea>
        </acc:FloorAreas>
    </acc:LinkedSectionID>
""")


class TestBSyncProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.testfile = Path(__file__).parents[1] / "files" / "completetest.xml"
        self.no_ns_testfile = Path(__file__).parents[1] / "files" / "testfile2.xml"
        self.output_dir = Path(__file__).parents[1] / "output"
        self.out_file = "testoutput.json"
        self.out_file_2 = "testoutput_2.json"
        self.test_assets_file = Path(__file__).parents[1] / "files" / "test_asset_defs.json"
        self.num_assets_to_extract = 23
        self.num_sections_in_testfile = 3

        # create output dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"TESTFILE: {self.testfile}")
        self.bp = BSyncProcessor(self.testfile)

    def test_process_lighting_method_1(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 1 lighting system
        method_1_ls = etree.XML("""
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:InstalledPower>1.0</acc:InstalledPower>
                <acc:InstalledPower>2.0</acc:InstalledPower>
                <acc:PercentPremisesServed>3.0</acc:PercentPremisesServed>
                <acc:PercentPremisesServed>4.0</acc:PercentPremisesServed>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(method_1_ls)

        # add sections to lighting system
        linked_sections = self.bp.xp(method_1_ls, ".//LinkedPremises/Section")[0]
        linked_sections.append(linked_section_with_floor_area_percentage)
        linked_sections.append(linked_section_with_floor_area_value)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [
            LightingDataPower(
                power=1.0,  # first InstalledPower
                sqft_percent=3.0,  # first PercentPremisesServed
                sqft=7500.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
            ),
            LightingDataPower(
                power=1.0,  # first InstalledPower
                sqft_percent=3.0,  # first PercentPremisesServed
                sqft=50.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
            ),
        ]

    def test_process_lighting_method_2_a(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 2 lighting system
        method_2_ls = etree.XML("""
            <acc:LightingSystem
                xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
                xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019"
            >
                <acc:LampPower>2</acc:LampPower>
                <acc:NumberOfLampsPerLuminaire>3</acc:NumberOfLampsPerLuminaire>
                <acc:NumberOfLuminaires>4</acc:NumberOfLuminaires>
                <acc:PercentPremisesServed>3.0</acc:PercentPremisesServed>
                <auc:Quantity>4</auc:Quantity>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(method_2_ls)

        # add sections to lighting system
        linked_sections = self.bp.xp(method_2_ls, ".//LinkedPremises/Section")[0]
        linked_sections.append(linked_section_with_floor_area_percentage)
        linked_sections.append(linked_section_with_floor_area_value)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [
            LightingDataPower(
                power=96,  # LampPower * NumberOfLampsPerLuminaire * NumberOfLuminaires
                sqft=7500.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=3.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
            ),
            LightingDataPower(
                power=96,  # LampPower * NumberOfLampsPerLuminaire * NumberOfLuminaires
                sqft=50.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=3.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
            ),
        ]

    def test_process_lighting_method_2_b(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 2 lighting system
        method_2_ls = etree.XML("""
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LampPower>2</acc:LampPower>
                <acc:NumberOfLampsPerLuminaire>3</acc:NumberOfLampsPerLuminaire>
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(method_2_ls)

        # add user defined feilds to lighting system
        good_field = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName>Quantity Of Luminaires For</acc:FieldName>
                <acc:FieldValue>2</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        bad_name_feild = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName>irrelevant</acc:FieldName>
                <acc:FieldValue>3</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        bad_value_field = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName>Quantity Of Luminaires For</acc:FieldName>
                <acc:FieldValue>bad value</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        method_2_ls.append(good_field)
        method_2_ls.append(bad_name_feild)
        method_2_ls.append(bad_value_field)

        # add sections to lighting system
        linked_sections = self.bp.xp(method_2_ls, ".//LinkedPremises/Section")[0]
        linked_sections.append(linked_section_with_floor_area_percentage)
        linked_sections.append(linked_section_with_floor_area_value)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [
            LightingDataPower(
                power=12,  # LampPower * NumberOfLampsPerLuminaire * sum of valid/relevant UserDefinedFields
                sqft=7500.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=None,
            ),
            LightingDataPower(
                power=12,  # LampPower * NumberOfLampsPerLuminaire * sum of valid/relevant UserDefinedFields
                sqft=50.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=None,
            ),
        ]

    def test_process_lighting_method_3(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 3 lighting system
        method_3_ls = etree.XML("""
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(method_3_ls)

        # add user defined feilds to lighting system
        good_field = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> Lighting Power Density For </acc:FieldName>
                <acc:FieldValue>1</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        bad_name_feild = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName> irrelevant </acc:FieldName>
                <acc:FieldValue>2</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        bad_value_field = etree.XML("""
            <acc:UserDefinedField xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:FieldName>Lighting Power Density For</acc:FieldName>
                <acc:FieldValue>bad value</acc:FieldValue>
            </acc:UserDefinedField>
        """)
        method_3_ls.append(good_field)
        method_3_ls.append(bad_name_feild)
        method_3_ls.append(bad_value_field)

        # add sections to lighting system
        linked_sections = self.bp.xp(method_3_ls, ".//LinkedPremises/Section")[0]
        linked_sections.append(linked_section_with_floor_area_percentage)
        linked_sections.append(linked_section_with_floor_area_value)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [
            LightingDataLPD(
                lpd=1.0,  # sum of valid/relevant UserDefinedFields
                sqft=7500.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=None,
            ),
            LightingDataLPD(
                lpd=1.0,  # sum of valid/relevant UserDefinedFields
                sqft=50.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
                sqft_percent=None,
            ),
        ]

    def test_process_lighting_method_4_on_section(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get sections and clear it
        section_path = "/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building/Sections"
        sections = self.bp.xp(self.bp.doc, section_path)[0]
        for s in sections:
            sections.remove(s)

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        building_path = "/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building"
        building = self.bp.xp(self.bp.doc, building_path)[0]
        building.append(
            etree.XML("""
            <auc:OccupancyClassification xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019"
            >Assembly-Convention center</auc:OccupancyClassification>
        """),
        )

        # add section
        section = etree.XML("""
            <auc:Section ID="Section-101919600" xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
                <auc:OccupancyClassification>Auditorium</auc:OccupancyClassification>
            </auc:Section>
        """)
        sections.append(section)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [LightingDataLPD(sqft=50000.0, sqft_percent=100, lpd=0.82)]

    def test_process_lighting_no_method_works(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get sections and clear it
        section_path = "/BuildingSync/Facilities/Facility/Sites/Site/Buildings/Building/Sections"
        sections = self.bp.xp(self.bp.doc, section_path)[0]
        for s in sections:
            sections.remove(s)

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add section
        section = etree.XML("""
            <auc:Section ID="Section-101919600" xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
                <auc:OccupancyClassification>Bad Classification</auc:OccupancyClassification>
            </auc:Section>
        """)
        sections.append(section)

        # empty lighting systems
        lighting_system = etree.XML("""
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(lighting_system)

        # add sections to lighting system
        linked_sections = self.bp.xp(lighting_system, ".//LinkedPremises/Section")[0]
        linked_sections.append(
            etree.XML("""
            <acc:LinkedSectionID
                IDref="Section-101919600"
                xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
            >
            </acc:LinkedSectionID>
        """),
        )

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == []

    def test_process_lighting_method_4_on_lightin_section(self) -> None:
        # Set Up #
        self.bp.process_sections()

        # get lighting_systems and clear it
        lighting_systems_path = "/BuildingSync/Facilities/Facility/Systems/LightingSystems"
        lighting_systems = self.bp.xp(self.bp.doc, lighting_systems_path)[0]
        for e in lighting_systems:
            lighting_systems.remove(e)

        # add method 1 lighting system
        method_1_ls = etree.XML("""
            <acc:LightingSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019">
                <acc:LinkedPremises>
                    <acc:Section></acc:Section>
                </acc:LinkedPremises>
            </acc:LightingSystem>
        """)
        lighting_systems.append(method_1_ls)

        # add sections to lighting system
        linked_sections = self.bp.xp(method_1_ls, ".//LinkedPremises/Section")[0]
        linked_sections.append(linked_section_with_floor_area_percentage)

        # Action #
        results = process_buildings_lighting_systems(self.bp)

        # Assertion #
        assert results == [
            LightingDataLPD(
                lpd=1.07,  # first InstalledPower
                sqft_percent=None,  # first PercentPremisesServed
                sqft=7500.0,  # sum of get_linked_section_sqft(...) for each LinkedSectionID
            ),
        ]
