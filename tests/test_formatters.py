import unittest
from unittest.mock import MagicMock

import pytest

from buildingsync_asset_extractor.formatters import Formatter
from buildingsync_asset_extractor.types import SystemData


class TestFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.export_asset = MagicMock()
        self.export_asset_units = MagicMock()
        self.formatter = Formatter(self.export_asset, self.export_asset_units)

    def test_format_80_percent_results(self) -> None:
        # SET UP
        system_datas = \
            [SystemData(value='Fuel oil no 1', cap='20.0', cap_units='kBtu/hr')] + \
            [SystemData(value='Natural gas', cap='10.0', cap_units='kBtu/hr')] * 8

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_80_percent_results_different_units(self) -> None:
        # SET UP
        system_datas = \
            [SystemData(value='Fuel oil no 1', cap='100.0', cap_units='kBtu/hr')] + \
            [SystemData(value='Natural gas', cap='1', cap_units='kW')]

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_80_percent_results_use_sqft(self) -> None:
        # SET UP
        system_datas = \
            [SystemData(value='Fuel oil no 1', sqft=20)] + \
            [SystemData(value='Natural gas', sqft=80)]

        # ACTION
        self.formatter.format_80_percent_results("Heating Fuel Type", system_datas, None)

        # ASSERT
        self.export_asset.assert_called_with("Heating Fuel Type", "Natural gas")
        self.export_asset_units.assert_called_with("Heating Fuel Type", None)

    def test_format_custom_avg_results(self) -> None:
        # SET UP
        system_datas = [
            SystemData(value='1.0', cap='3.0', cap_units='kBtu/hr'),
            SystemData(value='1.0', cap='2.0', cap_units='kBtu/hr'),
            SystemData(value='3.0', cap='5.0', cap_units='kBtu/hr')
        ]

        # ACTION
        self.formatter.format_custom_avg_results("Heating System Efficiency", system_datas, "Thermal Efficiency")

        # ASSERT
        self.export_asset.assert_called_with("Heating System Efficiency", 2.0)
        self.export_asset_units.assert_called_with("Heating System Efficiency", "Thermal Efficiency")

    def test_format_custom_avg_different_units(self) -> None:
        # SET UP
        system_datas = [
            SystemData(value='1.0', cap='3.0', cap_units='kBtu/hr'),
            SystemData(value='1.0', cap='2.0', cap_units='kBtu/hr'),
            SystemData(value='3.0', cap='5.0', cap_units='W')
        ]

        # ACTION
        self.formatter.format_custom_avg_results("Heating System Efficiency", system_datas, "Thermal Efficiency")

        # ASSERT
        (name, value) = self.export_asset.call_args.args
        assert name == "Heating System Efficiency"
        assert value == pytest.approx(2.9941557)
        self.export_asset_units.assert_called_with("Heating System Efficiency", "Thermal Efficiency")
