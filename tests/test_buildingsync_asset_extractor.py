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

import pytest
from lxml import etree

from buildingsync_asset_extractor.bae_types import Asset, AssetDef
from buildingsync_asset_extractor.processor import BSyncProcessor

EMPTY_ASSET: Asset = Asset(name="", value=None)

hvac_system_1 = etree.XML("""
    <auc:HVACSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019" xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
        <auc:HeatingAndCoolingSystems>
        <auc:HeatingSources>
            <auc:HeatingSource>
                <auc:OutputCapacity>1.0</auc:OutputCapacity>
                <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                <auc:PrimaryFuel>Natural gas</auc:PrimaryFuel>
            </auc:HeatingSource>
            <auc:HeatingSource>
                <auc:OutputCapacity>2.0</auc:OutputCapacity>
                <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                <auc:PrimaryFuel>Natural gas</auc:PrimaryFuel>
            </auc:HeatingSource>
        </auc:HeatingSources>
        </auc:HeatingAndCoolingSystems>
    </auc:HVACSystem>
""")

hvac_system_2 = etree.XML("""
    <auc:HVACSystem xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019" xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
        <auc:HeatingAndCoolingSystems>
        <auc:HeatingSources>
            <auc:HeatingSource>
                <auc:OutputCapacity>3.0</auc:OutputCapacity>
                <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                <auc:PrimaryFuel>Natural gas</auc:PrimaryFuel>
            </auc:HeatingSource>
            <auc:HeatingSource>
                <auc:OutputCapacity>4.0</auc:OutputCapacity>
                <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                <auc:PrimaryFuel>Electricity</auc:PrimaryFuel>
            </auc:HeatingSource>
        </auc:HeatingSources>
        </auc:HeatingAndCoolingSystems>
    </auc:HVACSystem>
""")


class TestBSyncProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.testfile = Path(__file__).parent / "files" / "completetest.xml"
        self.no_ns_testfile = Path(__file__).parent / "files" / "testfile2.xml"
        self.output_dir = Path(__file__).parent / "output"
        self.out_file = "testoutput.json"
        self.out_file_2 = "testoutput_2.json"
        self.test_assets_file = Path(__file__).parent / "files" / "test_asset_defs.json"
        self.num_assets_to_extract = 31
        self.num_sections_in_testfile = 3

        # create output dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"TESTFILE: {self.testfile}")
        self.bp = BSyncProcessor(self.testfile)

    def test_initialize_and_parse(self) -> None:
        ns = self.bp.get_namespaces()
        print(f"namespaces: {ns}")
        assert "auc" in ns

        doc = self.bp.get_doc()
        assert doc is not None

    def test_return_asset_definitions(self) -> None:
        self.bp.set_asset_defs_file(self.test_assets_file)
        defs = self.bp.get_asset_defs()
        assert len(defs) == self.num_assets_to_extract - 10

    def test_extract(self) -> None:  # noqa: PLR0915
        filename = self.output_dir / self.out_file_2
        if filename.exists():
            filename.unlink()
        self.bp.set_asset_defs_file(self.test_assets_file)
        self.bp.extract()
        sections = self.bp.get_sections()
        # print("SECTIONS: EMPTY_ASSET".format(sections))
        assert len(sections) == self.num_sections_in_testfile

        assets = self.bp.get_assets()
        print(f"ASSETS: {assets}")
        assert len(assets) == self.num_assets_to_extract

        # test that assets of each type were calculated
        # CUSTOM
        lighting_system_efficiency: Asset = next((item for item in assets if item.name == "Lighting System Efficiency"), EMPTY_ASSET)
        assert isinstance(lighting_system_efficiency.value, float)
        assert lighting_system_efficiency.value <= 2
        lighting_system_efficiency_units: Asset = next(
            (item for item in assets if item.name == "Lighting System Efficiency Units"),
            EMPTY_ASSET,
        )
        assert lighting_system_efficiency_units.value == "W/ft2"

        heating_system_efficiency: Asset = next((item for item in assets if item.name == "Heating System Efficiency"), EMPTY_ASSET)
        assert isinstance(heating_system_efficiency.value, float)
        assert heating_system_efficiency.value < 70
        assert heating_system_efficiency.value > 69
        heating_system_efficiency_units: Asset = next(
            (item for item in assets if item.name == "Heating System Efficiency Units"),
            EMPTY_ASSET,
        )
        assert heating_system_efficiency_units.value == "Thermal Efficiency"

        heating_system_average_age: Asset = next((item for item in assets if item.name == "Heating System Average Age"), EMPTY_ASSET)
        assert isinstance(heating_system_average_age.value, str)
        assert heating_system_average_age.value == "2010"

        heating_fuel_type: Asset = next((item for item in assets if item.name == "Heating Fuel Type"), EMPTY_ASSET)
        assert isinstance(heating_fuel_type.value, str)
        assert heating_fuel_type.value == "Fuel oil no 1"

        cooling_system_efficiency: Asset = next((item for item in assets if item.name == "Cooling System Efficiency"), EMPTY_ASSET)
        assert isinstance(cooling_system_efficiency.value, float)
        assert cooling_system_efficiency.value == 3.0
        cooling_system_efficiency_units: Asset = next(
            (item for item in assets if item.name == "Cooling System Efficiency Units"),
            EMPTY_ASSET,
        )
        assert cooling_system_efficiency_units.value == "COP"

        hot_water_system_efficiency: Asset = next((item for item in assets if item.name == "Hot Water System Efficiency"), EMPTY_ASSET)
        assert hot_water_system_efficiency.value == "mixed"

        how_water_system_fuel_type: Asset = next((item for item in assets if item.name == "Hot Water System Fuel Type"), EMPTY_ASSET)
        assert how_water_system_fuel_type.value == "mixed"

        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value == 202200.0

        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value == "kBtu/hr"

        domestic_hot_water: Asset = next(
            (item for item in assets if item.name == "Domestic HotWater System Electrification Potential"),
            EMPTY_ASSET,
        )
        assert domestic_hot_water.value == 0

        domestic_hot_water_units: Asset = next(
            (item for item in assets if item.name == "Domestic HotWater System Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert domestic_hot_water_units.value is None

        cooling_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Cooling Electrification Potential"),
            EMPTY_ASSET,
        )
        assert cooling_electrification_potential.value == 1000.0

        cooling_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Cooling Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert cooling_electrification_potential_units.value == "kBtu/hr"

        cooking_system_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Cooking System Electrification Potential"),
            EMPTY_ASSET,
        )
        assert cooking_system_electrification_potential.value == 2400.0

        cooking_system_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Cooking System Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert cooking_system_electrification_potential_units.value == "kBtu/hr"

        # count
        lighting_systems: Asset = next((item for item in assets if item.name == "Number of Lighting Systems"), EMPTY_ASSET)
        assert isinstance(lighting_systems.value, int)
        assert lighting_systems.value == 2
        # avg_sqft
        # TODO: need to get better testfile with this information in it
        # avgHeat = next((item for item in assets if item.name == "Average Heating Setpoint"), None)
        # self.assertEqual(avgHeat.value, 71.5)

        # age
        heating_system_oldest: Asset = next((item for item in assets if item.name == "Heating System Oldest"), EMPTY_ASSET)
        assert isinstance(heating_system_oldest.value, str)
        assert heating_system_oldest.value == "2010"

        filename = self.output_dir / self.out_file_2
        self.bp.save(filename)

    def test_extract_data(self) -> None:
        self.testfile = Path(__file__).parent / "files" / "testfile.xml"
        with open(self.testfile, mode="rb") as file:
            file_data = file.read()

        self.bp2 = BSyncProcessor(data=file_data)
        self.bp2.set_asset_defs_file(self.test_assets_file)
        self.bp2.extract()
        sections = self.bp2.get_sections()
        assert len(sections) == self.num_sections_in_testfile

        assets = self.bp2.get_assets()
        assert len(assets) == self.num_assets_to_extract

        # test 1 asset
        age: Asset = next((item for item in assets if item.name == "Heating System Oldest"), EMPTY_ASSET)
        assert age.value == "2010"

    def test_set_asset_defs(self) -> None:
        self.bp.set_asset_defs_file(self.test_assets_file)
        self.bp.extract()
        assets = self.bp.get_assets()
        assert len(assets) == self.num_assets_to_extract

    def test_extract_no_ns(self) -> None:
        # test that assets from files without a namespace prefix can be extracted
        self.bp2 = BSyncProcessor(self.no_ns_testfile)
        self.bp2.set_asset_defs_file(self.test_assets_file)
        self.bp2.extract()
        sections = self.bp2.get_sections()
        assert len(sections) == self.num_sections_in_testfile

        assets = self.bp2.get_assets()
        assert len(assets) == self.num_assets_to_extract
        # test that assets of each type were calculated
        # num
        cnt: Asset = next((item for item in assets if item.name == "Number of Lighting Systems"), EMPTY_ASSET)
        assert isinstance(cnt.value, int)
        assert cnt.value == 2
        # avg_sqft
        # TODO: need to get better testfile with this information in it
        # avgHeat = next((item for item in assets if item.name == "Average Heating Setpoint"), None)
        # self.assertEqual(avgHeat.value, 71.5)

        # age
        age: Asset = next((item for item in assets if item.name == "Heating System Oldest"), EMPTY_ASSET)
        assert age.value == "2010"

    def test_save(self) -> None:
        filename = self.output_dir / self.out_file
        if filename.exists():
            filename.unlink()
        self.bp.save(filename)
        assert filename.exists()


class TestElectrificationPotential(unittest.TestCase):
    def setUp(self) -> None:
        self.testfile = Path(__file__).parent / "files" / "completetest.xml"
        print(f"TESTFILE: {self.testfile}")
        self.bp = BSyncProcessor(self.testfile)

        # only try and get heating EP
        self.heating_source_path = (
            "/BuildingSync/Facilities/Facility/Systems/HVACSystems/HVACSystem/HeatingAndCoolingSystems/HeatingSources/HeatingSource"
        )
        self.bp.asset_defs = [
            AssetDef(
                parent_path=self.heating_source_path,
                key="PrimaryFuel",
                name="ElectrificationPotential",
                export_name="Heating Electrification Potential",
                type="custom",
                export_units=True,
            ),
        ]

        # get hvac_systems and clear it
        hvac_systems_path = "/BuildingSync/Facilities/Facility/Systems/HVACSystems"
        self.hvac_systems = self.bp.xp(self.bp.doc, hvac_systems_path)[0]
        for hvac_system in self.hvac_systems:
            self.hvac_systems.remove(hvac_system)

    def test_extract_heating_source_electrification_potential(self) -> None:
        # add in new ones with multipule heating sources.
        self.hvac_systems.append(hvac_system_1)
        self.hvac_systems.append(hvac_system_2)

        # ACTION
        self.bp.extract()
        assets = self.bp.get_assets()

        # ASSERT
        assert len(assets) == 2
        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value == 6.0
        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value == "kBtu/hr"

    def test_extract_heating_source_electrification_potential_different_export_unit(self) -> None:
        # SET UP
        self.bp.asset_defs[0].units = "W"

        # add in new ones with multipule heating sources.
        self.hvac_systems.append(hvac_system_1)
        self.hvac_systems.append(hvac_system_2)

        # ACTION
        self.bp.extract()
        assets = self.bp.get_assets()

        # ASSERT
        assert len(assets) == 2
        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value == pytest.approx(1758.42642)
        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value == "W"

    def test_extract_heating_source_electrification_potential_different_units(self) -> None:
        # add in new ones with multiple heating sources.
        hvac_system_1 = etree.XML("""
            <auc:HVACSystem
                xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
                xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
                <auc:HeatingAndCoolingSystems>
                <auc:HeatingSources>
                    <auc:HeatingSource>
                        <auc:OutputCapacity>1.0</auc:OutputCapacity>
                        <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                        <auc:PrimaryFuel>Natural gas</auc:PrimaryFuel>
                    </auc:HeatingSource>
                    <auc:HeatingSource>
                        <auc:OutputCapacity>2.0</auc:OutputCapacity>
                        <auc:CapacityUnits>W</auc:CapacityUnits>
                        <auc:PrimaryFuel>Natural gas</auc:PrimaryFuel>
                    </auc:HeatingSource>
                </auc:HeatingSources>
                </auc:HeatingAndCoolingSystems>
            </auc:HVACSystem>
        """)
        self.hvac_systems.append(hvac_system_1)

        # ACTION
        self.bp.extract()
        assets = self.bp.get_assets()

        # ASSERT
        assert len(assets) == 2
        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value == pytest.approx(1.00682)
        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value == "kBtu/hr"

    def test_extract_heating_source_electrification_no_heating_sources(self) -> None:
        # ACTION
        self.bp.extract()
        assets = self.bp.get_assets()

        # ASSERT
        assert len(assets) == 2
        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value is None
        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value is None

    def test_extract_heating_source_electrification_all_electric_heating_sources(self) -> None:
        self.bp.asset_defs[0].units = "kBtu/hr"

        hvac_system_1 = etree.XML("""
            <auc:HVACSystem
                xmlns:acc="http://buildingsync.net/schemas/bedes-auc/2019"
                xmlns:auc="http://buildingsync.net/schemas/bedes-auc/2019">
                <auc:HeatingAndCoolingSystems>
                <auc:HeatingSources>
                    <auc:HeatingSource>
                        <auc:OutputCapacity>1.0</auc:OutputCapacity>
                        <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                        <auc:PrimaryFuel>Hydrothermal</auc:PrimaryFuel>
                    </auc:HeatingSource>
                    <auc:HeatingSource>
                        <auc:OutputCapacity>2.0</auc:OutputCapacity>
                        <auc:CapacityUnits>kBtu/hr</auc:CapacityUnits>
                        <auc:PrimaryFuel>Solar</auc:PrimaryFuel>
                    </auc:HeatingSource>
                </auc:HeatingSources>
                </auc:HeatingAndCoolingSystems>
            </auc:HVACSystem>
        """)
        self.hvac_systems.append(hvac_system_1)

        # ACTION
        self.bp.extract()
        assets = self.bp.get_assets()

        # ASSERT
        assert len(assets) == 2
        heating_electrification_potential: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential.value == 0
        heating_electrification_potential_units: Asset = next(
            (item for item in assets if item.name == "Heating Electrification Potential Units"),
            EMPTY_ASSET,
        )
        assert heating_electrification_potential_units.value == "kBtu/hr"
