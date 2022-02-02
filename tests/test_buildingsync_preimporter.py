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
from shutil import rmtree

from buildingsync_preimporter import __version__
from buildingsync_preimporter.processor import BSyncProcessor


class TestBSyncProcessor(unittest.TestCase):
    def setUp(self):
        self.testfile = Path(__file__).parent / 'files' / 'testfile.xml'
        self.output_dir = Path(__file__).parent / 'output'
        self.out_file = 'testoutput.json'

        # create output dir
        if self.output_dir.exists():
            rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

        print("TESTFILE: {}".format(self.testfile))
        self.bp = BSyncProcessor(self.testfile)

    def test_version(self):
        assert __version__ == '0.1.0'

    def test_initialize_and_parse(self):
        ns = self.bp.get_namespaces()
        print('namespaces: {}'.format(ns))
        self.assertIn('auc', ns)

        doc = self.bp.get_doc()
        self.assertIsNotNone(doc)

    def test_extract(self):
        num_assets_to_extract = 8
        num_sections_in_testfile = 3

        self.bp.extract()
        sections = self.bp.get_sections()
        self.assertEqual(len(sections), num_sections_in_testfile)

        assets = self.bp.get_assets()
        self.assertEqual(len(assets), num_assets_to_extract)
        self.assertIn('primary_lamp', assets)

    def test_save(self):
        filename = self.output_dir / self.out_file
        self.bp.save(filename)
        self.assertTrue(filename.exists())
