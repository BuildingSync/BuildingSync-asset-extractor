import tempfile
import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from buildingsync_asset_extractor.cts import building_sync_to_cts
from buildingsync_asset_extractor.cts.cts import aggregate_facilities

BLANK_CTS_FILE_PATH = (
    Path(__file__).parents[2] /
    "buildingsync_asset_extractor" / "cts" /
    "CTS Comprehensive Evaluation Upload Template_20240312_021125.xlsx"
)
BLANK_CTS = pd.read_excel(BLANK_CTS_FILE_PATH, sheet_name="Evaluation Upload Template")

PRIMARYSCHOOL_1_FILE_PATH = Path(__file__).parents[1] / "files" / "PrimarySchool-1.xml"
PRIMARYSCHOOL_2_FILE_PATH = Path(__file__).parents[1] / "files" / "PrimarySchool-2.xml"
OFFICE_3_FILE_PATH = Path(__file__).parents[1] / "files" / "Office-3.xml"


class TestCTS(unittest.TestCase):
    def test_aggregate_facilities(self) -> None:
        # Action
        facilities = aggregate_facilities([PRIMARYSCHOOL_1_FILE_PATH, PRIMARYSCHOOL_2_FILE_PATH, OFFICE_3_FILE_PATH])

        # Assertion
        assert len(facilities["PSC MD0300ZZ"].appearances) == 2
        assert len(facilities["GSA ABC123"].appearances) == 1

    def test_cts(self) -> None:
        # Action
        with tempfile.TemporaryDirectory() as temp_dir:
            building_sync_to_cts([PRIMARYSCHOOL_1_FILE_PATH, PRIMARYSCHOOL_2_FILE_PATH, OFFICE_3_FILE_PATH], Path(temp_dir) / "output.xlsx")
            populated_cts = pd.read_excel(Path(temp_dir) / "output.xlsx")

        # Assertion
        assert len(populated_cts.index) == 5
        assert_frame_equal(populated_cts[0:3], BLANK_CTS)  # top 3 row template
