import tempfile
import unittest
from pathlib import Path

import pandas as pd

from buildingsync_asset_extractor.cts import building_sync_to_cts

BLANK_CTS_FILE_PATH = (
    Path(__file__).parents[2] /
    "buildingsync_asset_extractor" / "cts" /
    "CTS Comprehensive Evaluation Upload Template_20240312_021125.xlsx"
)
blank_cts = pd.read_excel(BLANK_CTS_FILE_PATH, sheet_name="Evaluation Upload Template")


class TestCTS(unittest.TestCase):
    def test_cts(self) -> None:
        # Action
        with tempfile.TemporaryDirectory() as temp_dir:
            building_sync_to_cts([], Path(temp_dir) / "output.xlsx")
            populated_cts = pd.read_excel(Path(temp_dir) / "output.xlsx")

        # Assertion
        diff = pd.concat([blank_cts, populated_cts]).drop_duplicates(keep=False)
        assert list(diff.index) == [3]  # only data is different
        data = diff.loc[3]

        assert data["Facility Name"] == "boo!"
