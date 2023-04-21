from typing import Literal, Optional, get_args

from buildingsync_asset_extractor.errors import BSyncProcessorError
from buildingsync_asset_extractor.types import SystemData

PowerUnits = Literal[
    "W",
    "kW",
    "hp",
    "MW",
    "Btu/hr",
    "cal/h",
    "ft-lbf/h",
    "ft-lbf/min",
    "Btu/s",
    "kBtu/hr",
    "MMBtu/hr",
    "therms/h",
]
POWERUNITSLIST: list[PowerUnits] = list(get_args(PowerUnits))


def unify_units(system_datas: list[SystemData], to_units: Optional[str] = None) -> list[SystemData]:
    if to_units is None:
        to_units = system_datas[0].cap_units
    for sd in system_datas:
        if sd.cap is not None:
            try:
                sd.cap = convert(float(sd.cap), sd.cap_units, to_units)  # type: ignore
                sd.cap_units = to_units
            except BSyncProcessorError:
                pass

    return system_datas


def convert(value: float, original_type: PowerUnits, to: PowerUnits) -> float:
    if original_type not in POWERUNITSLIST:
        raise BSyncProcessorError(f"`{original_type}` not a valid power unit")
    if to not in POWERUNITSLIST:
        raise BSyncProcessorError(f"`{to}` not a valid power unit")

    return value * from_to_table[original_type][to]


from_to_table: dict["PowerUnits", dict["PowerUnits", float]] = {
    'W': {
        'W': 1.0,
        'kW': 0.001,
        'hp': 0.00134102,
        'MW': 1e-06,
        'Btu/hr': 3.41214163,
        'cal/h': 859.84522786,
        'ft-lbf/h': 2655.2237374,
        'ft-lbf/min': 44.253728960000004,
        'Btu/s': 0.00094781,
        'kBtu/hr': 3.41214163,
        'MMBtu/hr': 3.41e-06,
        'therms/h': 3.412e-05,
    },
    'kW': {
        'W': 1000.0,
        'kW': 1.0,
        'hp': 1.3410199999999999,
        'MW': 0.001,
        'Btu/hr': 3412.14163,
        'cal/h': 859845.22786,
        'ft-lbf/h': 2655223.7374,
        'ft-lbf/min': 44253.72896,
        'Btu/s': 0.9478099999999999,
        'kBtu/hr': 3412.14163,
        'MMBtu/hr': 0.0034100000000000003,
        'therms/h': 0.03412,
    },
    'hp': {
        'W': 745.7010335416325,
        'kW': 0.7457010335416325,
        'hp': 1.0,
        'MW': 0.0007457010335416325,
        'Btu/hr': 2544.4375400814306,
        'cal/h': 641187.4751010425,
        'ft-lbf/h': 1980003.0852634562,
        'ft-lbf/min': 33000.05142354327,
        'Btu/s': 0.7067828966010946,
        'kBtu/hr': 2544.4375400814306,
        'MMBtu/hr': 0.002542840524376967,
        'therms/h': 0.0254433192644405,
    },
    'MW': {
        'W': 1000000.0,
        'kW': 1000.0,
        'hp': 1341.02,
        'MW': 1.0,
        'Btu/hr': 3412141.63,
        'cal/h': 859845227.86,
        'ft-lbf/h': 2655223737.4,
        'ft-lbf/min': 44253728.96,
        'Btu/s': 947.81,
        'kBtu/hr': 3412141.63,
        'MMBtu/hr': 3.41,
        'therms/h': 34.12,
    },
    'Btu/hr': {
        'W': 0.2930710704408832,
        'kW': 0.0002930710704408832,
        'hp': 0.00039301416688263316,
        'MW': 2.930710704408832e-07,
        'Btu/hr': 1.0,
        'cal/h': 251.99576134241534,
        'ft-lbf/h': 778.1692629798606,
        'ft-lbf/min': 12.969487717307913,
        'Btu/s': 0.0002777756912745735,
        'kBtu/hr': 1.0,
        'MMBtu/hr': 9.993723502034118e-07,
        'therms/h': 9.999584923442933e-06,
    },
    'cal/h': {
        'W': 0.0011629999999986276,
        'kW': 1.1629999999986277e-06,
        'hp': 1.5596062599981595e-06,
        'MW': 1.1629999999986277e-09,
        'Btu/hr': 0.0039683207156853174,
        'cal/h': 1.0,
        'ft-lbf/h': 3.088025206592556,
        'ft-lbf/min': 0.051467086780419266,
        'Btu/s': 1.1023030299986992e-06,
        'kBtu/hr': 0.0039683207156853174,
        'MMBtu/hr': 3.965829999995321e-09,
        'therms/h': 3.968155999995317e-08,
    },
    'ft-lbf/h': {
        'W': 0.00037661609675846065,
        'kW': 3.766160967584607e-07,
        'hp': 5.050497180750309e-07,
        'MW': 3.766160967584607e-10,
        'Btu/hr': 0.0012850674622776517,
        'cal/h': 0.32383155353302245,
        'ft-lbf/h': 1.0,
        'ft-lbf/min': 0.016666666667922055,
        'Btu/s': 3.569605026686366e-07,
        'kBtu/hr': 0.0012850674622776517,
        'MMBtu/hr': 1.284260889946351e-09,
        'therms/h': 1.2850141221398677e-08,
    },
    'ft-lbf/min': {
        'W': 0.022596965803805564,
        'kW': 2.2596965803805564e-05,
        'hp': 3.0302983082219338e-05,
        'MW': 2.2596965803805563e-08,
        'Btu/hr': 0.07710404773085137,
        'cal/h': 19.429893210517825,
        'ft-lbf/h': 59.99999999548061,
        'ft-lbf/min': 1.0,
        'Btu/s': 2.1417630158504952e-05,
        'kBtu/hr': 0.07710404773085137,
        'MMBtu/hr': 7.705565339097697e-08,
        'therms/h': 7.710084732258458e-07,
    },
    'Btu/s': {
        'W': 1055.0637786054167,
        'kW': 1.0550637786054167,
        'hp': 1.414861628385436,
        'MW': 0.0010550637786054166,
        'Btu/hr': 3600.0270412846457,
        'cal/h': 907191.5551218071,
        'ft-lbf/h': 2801430.389424041,
        'ft-lbf/min': 46690.506493917565,
        'Btu/s': 1.0,
        'kBtu/hr': 3600.0270412846457,
        'MMBtu/hr': 0.003597767485044471,
        'therms/h': 0.03599877612601682,
    },
    'kBtu/hr': {
        'W': 0.2930710704408832,
        'kW': 0.0002930710704408832,
        'hp': 0.00039301416688263316,
        'MW': 2.930710704408832e-07,
        'Btu/hr': 1.0,
        'cal/h': 251.99576134241534,
        'ft-lbf/h': 778.1692629798606,
        'ft-lbf/min': 12.969487717307913,
        'Btu/s': 0.0002777756912745735,
        'kBtu/hr': 1.0,
        'MMBtu/hr': 9.993723502034118e-07,
        'therms/h': 9.999584923442933e-06,
    },
    'MMBtu/hr': {
        'W': 293255.1319648094,
        'kW': 293.2551319648094,
        'hp': 393.26099706744867,
        'MW': 0.29325513196480935,
        'Btu/hr': 1000628.0439882698,
        'cal/h': 252154025.76539588,
        'ft-lbf/h': 778657987.5073314,
        'ft-lbf/min': 12977633.126099706,
        'Btu/s': 277.95014662756597,
        'kBtu/hr': 1000628.0439882698,
        'MMBtu/hr': 1.0,
        'therms/h': 10.005865102639294,
    },
    'therms/h': {
        'W': 29308.323563892147,
        'kW': 29.30832356389215,
        'hp': 39.30304806565065,
        'MW': 0.02930832356389215,
        'Btu/hr': 100004.15093786636,
        'cal/h': 25200622.15298945,
        'ft-lbf/h': 77820156.4302462,
        'ft-lbf/min': 1297002.6072684643,
        'Btu/s': 27.778722157092616,
        'kBtu/hr': 100004.15093786636,
        'MMBtu/hr': 0.09994138335287223,
        'therms/h': 1.0,
    }
}
