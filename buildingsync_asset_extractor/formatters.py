from dataclasses import dataclass
from typing import Literal, Optional, Union

from buildingsync_asset_extractor.converter import convert
from buildingsync_asset_extractor.eletric_fuel_types import electric_fuel_types
from buildingsync_asset_extractor.errors import BSyncProcessorError
from buildingsync_asset_extractor.types import SystemData


@dataclass
class ElectrificationPontential:
    value: Union[None, Literal["unknown"], float]
    units: Optional[str]


def format_electrification_pontential(system_datas: list[SystemData], units: Optional[str]) -> ElectrificationPontential:
    """Sum capacities of non-electric systems.

    covert all possible system data cap type to given units or, if units none, the first sd's units.
    """
    # If no SystemDatas, then None
    if len(system_datas) == 0:
        return ElectrificationPontential(None, units)

    # if no non electric SystemDatas, then 0
    system_datas = [
        sd for sd in system_datas
        if sd.value not in electric_fuel_types
        and sd.cap is not None
    ]
    if len(system_datas) == 0:
        return ElectrificationPontential(0, units)

    # if no unit, set units to first system data's
    if units is None:
        units = system_datas[0].cap_units

    # try to convert cap to same power unit
    for sd in system_datas:
        if sd.cap is not None:
            try:
                sd.cap = convert(float(sd.cap), sd.cap_units, units)  # type: ignore
                sd.cap_units = units
            except BSyncProcessorError:
                pass

    # if all non electric SystemData have same cap unit, sum
    cap_units = {sd.cap_units for sd in system_datas}
    if len(cap_units) <= 1:
        value = sum([float(sd.cap) for sd in system_datas if sd.cap is not None])
        return ElectrificationPontential(value, units)

    # else unknown
    return ElectrificationPontential("unknown", None)
