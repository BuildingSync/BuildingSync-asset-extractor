from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildingTypeLPD:
    building_type: str
    lpd_by_year: dict[int, Optional[float]]


building_type_to_lpd = [
    BuildingTypeLPD(building_type="Automotive Facility", lpd_by_year={1999: 1.5, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 0.82, 2013: 0.8, 2019: 0.75}),
    BuildingTypeLPD(building_type="Convention Center", lpd_by_year={1999: 1.4, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.08, 2013: 1.01, 2019: 0.64}),
    BuildingTypeLPD(building_type="Court House", lpd_by_year={1999: 1.4, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.05, 2013: 1.01, 2019: 0.79}),
    BuildingTypeLPD(building_type="Dining: Bar Lounge/Leisure", lpd_by_year={1999: 1.5, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 0.99, 2013: 1.01, 2019: 0.8}),
    BuildingTypeLPD(building_type="Dining: Cafeteria/Fast Food", lpd_by_year={1999: 1.8, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 0.9, 2013: 0.9, 2019: 0.76}),
    BuildingTypeLPD(building_type="Dining: Family ", lpd_by_year={1999: 1.9, 2001: 1.6, 2004: 1.6, 2007: 1.6, 2010: 0.89, 2013: 0.95, 2019: 0.71}),
    BuildingTypeLPD(building_type="Dormitory ", lpd_by_year={1999: 1.5, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.61, 2013: 0.57, 2019: 0.53}),
    BuildingTypeLPD(building_type="Exercise Center", lpd_by_year={1999: 1.4, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.88, 2013: 0.84, 2019: 0.72}),
    BuildingTypeLPD(building_type="Fire Station ", lpd_by_year={1999: 1.3, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.71, 2013: 0.671, 2019: 0.56}),
    BuildingTypeLPD(building_type="Gymnasium", lpd_by_year={1999: 1.7, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 1.0, 2013: 0.94, 2019: 0.76}),
    BuildingTypeLPD(building_type="Health Care-Clinic", lpd_by_year={1999: 1.6, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.87, 2013: 0.9, 2019: 0.81}),
    BuildingTypeLPD(building_type="Hospital", lpd_by_year={1999: 1.6, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.21, 2013: 1.05, 2019: 0.96}),
    BuildingTypeLPD(building_type="Hotel", lpd_by_year={1999: 1.7, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 1.0, 2013: 0.87, 2019: 0.56}),
    BuildingTypeLPD(building_type="Library", lpd_by_year={1999: 1.5, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.18, 2013: 1.19, 2019: 0.83}),
    BuildingTypeLPD(building_type="Manufacturing Facility", lpd_by_year={1999: 2.2, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.11, 2013: 1.17, 2019: 0.82}),
    BuildingTypeLPD(building_type="Motel", lpd_by_year={1999: 2.0, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.88, 2013: 0.87, 2019: 0.56}),
    BuildingTypeLPD(building_type="Motion Picture Theater", lpd_by_year={1999: 1.6, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.83, 2013: 0.76, 2019: 0.44}),
    BuildingTypeLPD(building_type="Multi-Family", lpd_by_year={1999: 1.0, 2001: 0.7, 2004: 0.7, 2007: 0.7, 2010: 0.6, 2013: 0.51, 2019: 0.45}),
    BuildingTypeLPD(building_type="Museum", lpd_by_year={1999: 1.6, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 1.06, 2013: 1.02, 2019: 0.55}),
    BuildingTypeLPD(building_type="Office", lpd_by_year={1999: 1.3, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.9, 2013: 0.82, 2019: 0.64}),
    BuildingTypeLPD(building_type="Parking Garage", lpd_by_year={1999: 0.3, 2001: 0.3, 2004: 0.3, 2007: 0.3, 2010: 0.25, 2013: 0.21, 2019: 0.18}),
    BuildingTypeLPD(building_type="Penitentiary", lpd_by_year={1999: 1.2, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.97, 2013: 0.81, 2019: 0.69}),
    BuildingTypeLPD(building_type="Performing Arts Theater", lpd_by_year={1999: 1.5, 2001: 1.6, 2004: 1.6, 2007: 1.6, 2010: 1.39, 2013: 1.39, 2019: 0.84}),
    BuildingTypeLPD(building_type="Police Station", lpd_by_year={1999: 1.3, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.96, 2013: 0.87, 2019: 0.66}),
    BuildingTypeLPD(building_type="Post Office", lpd_by_year={1999: 1.6, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.87, 2013: 0.87, 2019: 0.65}),
    BuildingTypeLPD(building_type="Religious Building", lpd_by_year={1999: 2.2, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.05, 2013: 1.0, 2019: 0.67}),
    BuildingTypeLPD(building_type="Retail", lpd_by_year={1999: 1.9, 2001: 1.5, 2004: 1.5, 2007: 1.5, 2010: 1.4, 2013: 1.26, 2019: 0.84}),
    BuildingTypeLPD(building_type="School/University", lpd_by_year={1999: 1.5, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.99, 2013: 0.87, 2019: 0.72}),
    BuildingTypeLPD(building_type="Sports Arena", lpd_by_year={1999: 1.5, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.78, 2013: 0.91, 2019: 0.76}),
    BuildingTypeLPD(building_type="Town Hall", lpd_by_year={1999: 1.4, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.92, 2013: 0.89, 2019: 0.69}),
    BuildingTypeLPD(building_type="Transportation", lpd_by_year={1999: 1.2, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.77, 2013: 0.7, 2019: 0.5}),
    BuildingTypeLPD(building_type="Warehouse", lpd_by_year={1999: 1.2, 2001: 0.8, 2004: 0.8, 2007: 0.8, 2010: 0.66, 2013: 0.66, 2019: 0.45}),
    BuildingTypeLPD(building_type="Workshop", lpd_by_year={1999: 1.7, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.2, 2013: 1.19, 2019: 0.91}),
]
