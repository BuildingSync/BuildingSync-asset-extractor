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

from buildingsync_asset_extractor.processor import BSyncProcessor


class TestBSyncProcessor(unittest.TestCase):
    def setUp(self):
        self.testfile = Path(__file__).parent / 'files' / 'completetest.xml'
        self.no_ns_testfile = Path(__file__).parent / 'files' / 'testfile2.xml'
        self.output_dir = Path(__file__).parent / 'output'
        self.out_file = 'testoutput.json'
        self.out_file_2 = 'testoutput_2.json'
        self.test_assets_file = Path(__file__).parent / 'files' / 'test_asset_defs.json'
        self.num_assets_to_extract = 18
        self.num_sections_in_testfile = 3

        # create output dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("TESTFILE: {}".format(self.testfile))
        self.bp = BSyncProcessor(self.testfile)

    def test_initialize_and_parse(self):
        ns = self.bp.get_namespaces()
        print('namespaces: {}'.format(ns))
        self.assertIn('auc', ns)

        doc = self.bp.get_doc()
        self.assertIsNotNone(doc)

    def test_return_asset_definitions(self):
        self.bp.set_asset_defs_file(self.test_assets_file)
        defs = self.bp.get_asset_defs()
        self.assertEqual(len(defs), self.num_assets_to_extract - 1)

    def test_extract(self):
        filename = self.output_dir / self.out_file_2
        if filename.exists():
            filename.unlink()
        self.bp.set_asset_defs_file(self.test_assets_file)
        self.bp.extract()
        sections = self.bp.get_sections()
        # print("SECTIONS: {}".format(sections))
        self.assertEqual(len(sections), self.num_sections_in_testfile)

        assets = self.bp.get_assets()
        self.assertEqual(len(assets), self.num_assets_to_extract)

        # test that assets of each type were calculated
        # CUSTOM
        LSE = next((item for item in assets if item["name"] == "Lighting System Efficiency"), None)
        self.assertTrue(isinstance(LSE['value'], float))
        self.assertLessEqual(LSE['value'], 2)
        self.assertEqual(LSE['units'], 'W/ft2')

        HSE = next((item for item in assets if item["name"] == "Heating System Efficiency"), None)
        self.assertTrue(isinstance(HSE['value'], float))
        self.assertLess(HSE['value'], 70)
        self.assertGreater(HSE['value'], 69)
        self.assertEqual(HSE['units'], 'Thermal Efficiency')

        HSAA = next((item for item in assets if item["name"] == "Heating System Average Age"), None)
        self.assertTrue(isinstance(HSAA['value'], str))
        self.assertEqual(HSAA['value'], '2010')

        HFT = next((item for item in assets if item["name"] == "Heating Fuel Type"), None)
        self.assertTrue(isinstance(HFT['value'], str))
        self.assertEqual(HFT['value'], 'Fuel oil no 1')

        CSE = next((item for item in assets if item["name"] == "Cooling System Efficiency"), None)
        self.assertTrue(isinstance(CSE['value'], float))
        self.assertEqual(CSE['value'], 3.0)
        self.assertEqual(CSE['units'], 'COP')

        WHE = next((item for item in assets if item["name"] == "Hot Water System Efficiency"), None)
        self.assertEqual(WHE['value'], 'mixed')

        WHFT = next((item for item in assets if item["name"] == "Hot Water System Fuel Type"), None)
        self.assertEqual(WHFT['value'], 'mixed')

        # count
        cnt = next((item for item in assets if item["name"] == "Number of Lighting Systems"), None)
        self.assertTrue(isinstance(cnt['value'], int))
        self.assertEqual(cnt['value'], 2)
        # avg_sqft
        # TODO: need to get better testfile with this information in it
        # avgHeat = next((item for item in assets if item["name"] == "Average Heating Setpoint"), None)
        # self.assertEqual(avgHeat['value'], 71.5)

        # age
        age = next((item for item in assets if item["name"] == "Heating System Oldest"), None)
        self.assertTrue(isinstance(age['value'], str))
        self.assertEqual(age['value'], '2010')

        filename = self.output_dir / self.out_file_2
        self.bp.save(filename)

    def test_extract_data(self):
        self.testfile = Path(__file__).parent / 'files' / 'testfile.xml'
        with open(self.testfile, mode='rb') as file:
            file_data = file.read()

        self.bp2 = BSyncProcessor(data=file_data)
        self.bp2.set_asset_defs_file(self.test_assets_file)
        self.bp2.extract()
        sections = self.bp2.get_sections()
        self.assertEqual(len(sections), self.num_sections_in_testfile)

        assets = self.bp2.get_assets()
        self.assertEqual(len(assets), self.num_assets_to_extract)

        # test 1 asset
        age = next((item for item in assets if item["name"] == "Heating System Oldest"), None)
        self.assertEqual(age['value'], '2010')

    def test_set_asset_defs(self):
        self.bp.set_asset_defs_file(self.test_assets_file)
        self.bp.extract()
        assets = self.bp.get_assets()
        self.assertEqual(len(assets), self.num_assets_to_extract)

    def test_extract_no_ns(self):
        # test that assets from files without a namespace prefix can be extracted
        self.bp2 = BSyncProcessor(self.no_ns_testfile)
        self.bp2.set_asset_defs_file(self.test_assets_file)
        self.bp2.extract()
        sections = self.bp2.get_sections()
        self.assertEqual(len(sections), self.num_sections_in_testfile)

        assets = self.bp2.get_assets()
        self.assertEqual(len(assets), self.num_assets_to_extract)
        # test that assets of each type were calculated
        # num
        cnt = next((item for item in assets if item["name"] == "Number of Lighting Systems"), None)
        self.assertTrue(isinstance(cnt['value'], int))
        self.assertEqual(cnt['value'], 2)
        # avg_sqft
        # TODO: need to get better testfile with this information in it
        # avgHeat = next((item for item in assets if item["name"] == "Average Heating Setpoint"), None)
        # self.assertEqual(avgHeat['value'], 71.5)

        # age
        age = next((item for item in assets if item["name"] == "Heating System Oldest"), None)
        self.assertEqual(age['value'], '2010')

    def test_save(self):
        filename = self.output_dir / self.out_file
        if filename.exists():
            filename.unlink()
        self.bp.save(filename)
        self.assertTrue(filename.exists())
