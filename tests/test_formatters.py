import unittest
from unittest.mock import MagicMock

import pytest

from buildingsync_asset_extractor.bae_types import SystemData
from buildingsync_asset_extractor.formatters import Formatter
from buildingsync_asset_extractor.lighting_processing.lighting_processing import LightingDataPower


class TestFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.export_asset = MagicMock()
        self.export_asset_units = MagicMock()
        self.formatter = Formatter(self.export_asset, self.export_asset_units)

    def test_format_80_percent_results(self) -> None:
        # SET UP
        system_datas = [SystemData(value="Fuel oil no 1", cap="20.0", cap_units="kBtu/hr")] + [
            SystemData(value="Natural gas", cap="10.0", cap_units="kBtu/hr"),
        ] * 8

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_80_percent_results_different_units(self) -> None:
        # SET UP
        system_datas = [
            SystemData(value="Fuel oil no 1", cap="1", cap_units="Btu/hr"),
            SystemData(value="Natural gas", cap="1", cap_units="kBtu/hr"),
        ]

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_80_percent_results_use_sqft(self) -> None:
        # SET UP
        system_datas = [SystemData(value="Fuel oil no 1", sqft=20), SystemData(value="Natural gas", sqft=80)]

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_custom_avg_results(self) -> None:
        # SET UP
        system_datas = [
            SystemData(value="1.0", cap="3.0", cap_units="kBtu/hr"),
            SystemData(value="1.0", cap="2.0", cap_units="kBtu/hr"),
            SystemData(value="3.0", cap="5.0", cap_units="kBtu/hr"),
        ]

        # ACTION
        self.formatter.format_custom_avg_results("Heating System Efficiency", system_datas, "Thermal Efficiency")

        # ASSERT
        self.export_asset.assert_called_with("Heating System Efficiency", 2.0)
        self.export_asset_units.assert_called_with("Heating System Efficiency", "Thermal Efficiency")

    def test_format_custom_avg_different_units(self) -> None:
        # SET UP
        system_datas = [
            SystemData(value="1.0", cap="3.0", cap_units="kBtu/hr"),
            SystemData(value="1.0", cap="2.0", cap_units="kBtu/hr"),
            SystemData(value="3.0", cap="5.0", cap_units="W"),
        ]

        # ACTION
        self.formatter.format_custom_avg_results("Heating System Efficiency", system_datas, "Thermal Efficiency")

        # ASSERT
        (name, value) = self.export_asset.call_args.args
        assert name == "Heating System Efficiency"
        assert value == pytest.approx(1.0068010770219646)
        self.export_asset_units.assert_called_with("Heating System Efficiency", "Thermal Efficiency")

    def test_format_lighting_results_sums_percent_served_area(self) -> None:
        results = [
            LightingDataPower(power=100.0, sqft=1000.0, sqft_percent=50.0),
            LightingDataPower(power=100.0, sqft=2000.0, sqft_percent=50.0),
        ]

        self.formatter.format_lighting_results("Lighting System Efficiency", results, "W/ft2")

        self.export_asset.assert_called_once_with("Lighting System Efficiency", pytest.approx(200.0 / 1500.0))
        self.export_asset_units.assert_called_once_with("Lighting System Efficiency", "W/ft2")

    def test_format_lighting_results_zero_power(self) -> None:
        results = [LightingDataPower(power=0.0, sqft=1000.0, sqft_percent=50.0)]

        self.formatter.format_lighting_results("Lighting System Efficiency", results, "W/ft2")

        self.export_asset.assert_called_once_with("Lighting System Efficiency", 0.0)
        self.export_asset_units.assert_called_once_with("Lighting System Efficiency", "W/ft2")

    def test_format_lighting_results_zero_served_area(self) -> None:
        results = [LightingDataPower(power=0.0, sqft=1000.0, sqft_percent=0.0)]

        self.formatter.format_lighting_results("Lighting System Efficiency", results, "W/ft2")

        self.export_asset.assert_called_once_with("Lighting System Efficiency", "unknown")
        self.export_asset_units.assert_called_once_with("Lighting System Efficiency", "W/ft2")
