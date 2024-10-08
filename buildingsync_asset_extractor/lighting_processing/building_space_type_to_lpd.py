from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildingSpaceTypeLPD:
    building_type: str
    section_type: str
    lpd_by_year: dict[int, Optional[float]]


building_space_type_to_lpd = [
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Atrium",
        lpd_by_year={1999: 1.3, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: None, 2013: None, 2019: 0.49},
    ),
    BuildingSpaceTypeLPD(
        building_type="Auditorium",
        section_type="Audience Seating Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.79, 2013: 0.63, 2019: 0.61},
    ),
    BuildingSpaceTypeLPD(
        building_type="Convention center",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 0.5, 2001: 0.7, 2004: 0.7, 2007: 0.7, 2010: 0.82, 2013: 0.82, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Exercise Center",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 0.5, 2001: 0.3, 2004: 0.3, 2007: 0.3, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Gymnasium",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 0.5, 2001: 0.4, 2004: 0.4, 2007: 0.4, 2010: 0.43, 2013: 0.65, 2019: 0.23},
    ),
    BuildingSpaceTypeLPD(
        building_type="Motion picture theater",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 1.3, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.14, 2013: 1.14, 2019: 0.27},
    ),
    BuildingSpaceTypeLPD(
        building_type="Penitentiary",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 1.9, 2001: 0.7, 2004: 0.7, 2007: 0.7, 2010: 0.43, 2013: 0.28, 2019: 0.67},
    ),
    BuildingSpaceTypeLPD(
        building_type="Performing arts theater",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 1.8, 2001: 2.6, 2004: 2.6, 2007: 2.6, 2010: 2.43, 2013: 2.43, 2019: 1.16},
    ),
    BuildingSpaceTypeLPD(
        building_type="Religious building",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 3.2, 2001: 1.7, 2004: 1.7, 2007: 1.7, 2010: 1.53, 2013: 1.53, 2019: 0.72},
    ),
    BuildingSpaceTypeLPD(
        building_type="Sports arena",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 0.5, 2001: 0.4, 2004: 0.4, 2007: 0.4, 2010: 0.43, 2013: 0.43, 2019: 0.33},
    ),
    BuildingSpaceTypeLPD(
        building_type="Transportation",
        section_type="Audience Seating Area",
        lpd_by_year={1999: None, 2001: 0.5, 2004: 0.5, 2007: 0.5, 2010: 0.54, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Audience Seating Area",
        lpd_by_year={1999: 1.6, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: None, 2013: 0.43, 2019: 0.23},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Banking Activity Area",
        lpd_by_year={1999: 2.4, 2001: 1.5, 2004: 1.5, 2007: 1.5, 2010: 1.38, 2013: 1.01, 2019: 0.61},
    ),
    BuildingSpaceTypeLPD(
        building_type="Penitentiary",
        section_type="Classroom/Lecture Hall / Training Room",
        lpd_by_year={1999: 1.4, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.34, 2013: 1.34, 2019: 0.89},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Classroom/Lecture Hall / Training Room",
        lpd_by_year={1999: 1.6, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.24, 2013: 1.24, 2019: 0.71},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Conference/Meeting / Multipurpose Room",
        lpd_by_year={1999: 1.5, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.23, 2013: 1.23, 2019: 0.97},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Confinement Cells",
        lpd_by_year={1999: 1.1, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 1.1, 2013: 0.81, 2019: 0.7},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Copy/Print Room",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 0.72, 2019: 0.31},
    ),
    BuildingSpaceTypeLPD(
        building_type="Facility for the visually impaired",
        section_type="Corridor",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.66, 2013: 0.92, 2019: 0.71},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hospital",
        section_type="Corridor",
        lpd_by_year={1999: 1.6, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.89, 2013: 0.99, 2019: 0.71},
    ),
    BuildingSpaceTypeLPD(
        building_type="Manufacturing facility",
        section_type="Corridor",
        lpd_by_year={1999: 0.5, 2001: 0.5, 2004: 0.5, 2007: 0.5, 2010: 0.41, 2013: 0.41, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Corridor",
        lpd_by_year={1999: 0.7, 2001: 0.5, 2004: 0.5, 2007: 0.5, 2010: 0.66, 2013: 0.66, 2019: 0.41},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Courtroom",
        lpd_by_year={1999: 2.1, 2001: 1.9, 2004: 1.9, 2007: 1.9, 2010: 1.72, 2013: 1.72, 2019: 1.2},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Judges' Chambers",
        lpd_by_year={1999: 1.1, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.17, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Computer Room",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 1.71, 2019: 0.94},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hotel",
        section_type="Dining Area",
        lpd_by_year={1999: 1.0, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 0.82, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Motel",
        section_type="Dining Area",
        lpd_by_year={1999: 1.2, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.88, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Penitentiary",
        section_type="Dining Area",
        lpd_by_year={1999: 1.4, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.07, 2013: 0.96, 2019: 0.42},
    ),
    BuildingSpaceTypeLPD(
        building_type="Facility for the visually impaired",
        section_type="Dining Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 2.65, 2019: 1.27},
    ),
    BuildingSpaceTypeLPD(
        building_type="Bar/lounge or leisure dining",
        section_type="Dining Area",
        lpd_by_year={1999: 1.2, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.31, 2013: 1.07, 2019: 0.86},
    ),
    BuildingSpaceTypeLPD(
        building_type="Cafeteria or fast food dining",
        section_type="Dining Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 0.65, 2019: 0.4},
    ),
    BuildingSpaceTypeLPD(
        building_type="Family dining",
        section_type="Dining Area",
        lpd_by_year={1999: 2.2, 2001: 2.1, 2004: 2.1, 2007: 2.1, 2010: 0.89, 2013: 0.89, 2019: 0.6},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Dining Area",
        lpd_by_year={1999: 1.4, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 0.65, 2013: 0.65, 2019: 0.43},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Electrical/Mechanical Room",
        lpd_by_year={1999: 1.3, 2001: 1.5, 2004: 1.5, 2007: 1.5, 2010: 0.95, 2013: 0.42, 2019: 0.43},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Emergency Vehicle Garage",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 0.56, 2019: 0.52},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Food Preparation Area",
        lpd_by_year={1999: 2.2, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.99, 2013: 1.21, 2019: 1.09},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Guest Room",
        lpd_by_year={1999: 2.5, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 1.11, 2013: 0.91, 2019: 0.41},
    ),
    BuildingSpaceTypeLPD(
        building_type="Classroom (school)",
        section_type="Laboratory ",
        lpd_by_year={1999: None, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.28, 2013: 1.43, 2019: 1.11},
    ),
    BuildingSpaceTypeLPD(
        building_type="Police station",
        section_type="Laboratory ",
        lpd_by_year={1999: 1.8, 2001: None, 2004: None, 2007: None, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other ",
        section_type="Laboratory",
        lpd_by_year={1999: 1.8, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.81, 2013: 1.81, 2019: 1.33},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Laundry/Washing Area",
        lpd_by_year={1999: 0.7, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: 0.6, 2013: 0.6, 2019: 0.53},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Loading Dock, Interior",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 0.47, 2019: 0.88},
    ),
    BuildingSpaceTypeLPD(
        building_type="Facility for the visually impaired",
        section_type="Lobby",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 1.8, 2019: 1.69},
    ),
    BuildingSpaceTypeLPD(
        building_type="Elevator",
        section_type="Lobby",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.64, 2013: 0.64, 2019: 0.65},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hotel",
        section_type="Lobby",
        lpd_by_year={1999: 1.7, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 1.06, 2013: 1.06, 2019: 0.51},
    ),
    BuildingSpaceTypeLPD(
        building_type="Motion picture theater",
        section_type="Lobby",
        lpd_by_year={1999: 0.8, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.52, 2013: 0.59, 2019: 0.23},
    ),
    BuildingSpaceTypeLPD(
        building_type="Performing arts theater",
        section_type="Lobby",
        lpd_by_year={1999: 1.2, 2001: 3.3, 2004: 3.3, 2007: 3.3, 2010: 2.0, 2013: 2.0, 2019: 1.25},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Lobby",
        lpd_by_year={1999: 1.8, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 0.9, 2013: 0.9, 2019: 0.84},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Locker Room",
        lpd_by_year={1999: None, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: 0.75, 2013: 0.75, 2019: 0.52},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hospital / Healthcare facility",
        section_type="Lounge / Breakroom",
        lpd_by_year={1999: 1.4, 2001: 0.8, 2004: 0.8, 2007: 0.8, 2010: 1.07, 2013: 0.92, 2019: 0.42},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Lounge / Breakroom",
        lpd_by_year={1999: 1.4, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.73, 2013: 0.73, 2019: 0.59},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Office",
        lpd_by_year={1999: 1.43, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 1.07, 2013: 1.07, 2019: 0.67},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Parking Area",
        lpd_by_year={1999: 0.2, 2001: 0.2, 2004: 0.2, 2007: 0.2, 2010: 0.19, 2013: 0.19, 2019: 0.15},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Pharmacy Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 1.68, 2019: 1.66},
    ),
    BuildingSpaceTypeLPD(
        building_type="Facility for the visually impaired",
        section_type="Restroom",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 1.21, 2019: 1.26},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Restroom",
        lpd_by_year={1999: 1.0, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: None, 2013: 0.98, 2019: 0.63},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Sales Area",
        lpd_by_year={1999: 2.1, 2001: 2.1, 2004: 1.7, 2007: 1.7, 2010: 1.68, 2013: 1.44, 2019: 1.05},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Seating Area, General",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 0.54, 2019: 0.23},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Stairway",
        lpd_by_year={1999: 0.9, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: 0.69, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Stairwell",
        lpd_by_year={1999: 0.9, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: None, 2013: 0.69, 2019: 0.49},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Storage Room",
        lpd_by_year={1999: 0.7, 2001: 0.55, 2004: 0.55, 2007: 0.55, 2010: 0.63, 2013: 0.83, 2019: 0.42},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hospital",
        section_type="Storage Room",
        lpd_by_year={1999: 2.9, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Museum",
        section_type="Storage Room",
        lpd_by_year={1999: 1.4, 2001: 0.8, 2004: 0.8, 2007: 0.8, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Vehicular Maintenance Area / Automotive",
        lpd_by_year={1999: 1.4, 2001: 0.7, 2004: 0.7, 2007: 0.7, 2010: 0.67, 2013: 0.67, 2019: 0.6},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Workshop",
        lpd_by_year={1999: 2.5, 2001: 1.9, 2004: 1.9, 2007: 1.9, 2010: 1.59, 2013: 1.59, 2019: 1.26},
    ),
    BuildingSpaceTypeLPD(
        building_type="Facility for the Visually Impaired",
        section_type="Chapel",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 2.21, 2019: 0.7},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Recreation room/common livingroom",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: None, 2013: 2.41, 2019: 1.77},
    ),
    BuildingSpaceTypeLPD(
        building_type="Convention Center",
        section_type="Exhibit Space",
        lpd_by_year={1999: 3.3, 2001: 1.3, 2004: 1.3, 2007: 1.3, 2010: 1.45, 2013: 1.45, 2019: 0.61},
    ),
    BuildingSpaceTypeLPD(
        building_type="Dormitory",
        section_type="Living Quarters",
        lpd_by_year={1999: 1.9, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.38, 2013: 0.38, 2019: 0.5},
    ),
    BuildingSpaceTypeLPD(
        building_type="Fire Station",
        section_type="Engine Room",
        lpd_by_year={1999: 0.9, 2001: 0.8, 2004: 0.8, 2007: 0.8, 2010: 0.56, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Sleeping Quarters",
        lpd_by_year={1999: 1.1, 2001: 0.3, 2004: 0.3, 2007: 0.3, 2010: 0.25, 2013: 0.22, 2019: 0.23},
    ),
    BuildingSpaceTypeLPD(
        building_type="Gymnasium / Fitness Center",
        section_type="Exercise area",
        lpd_by_year={1999: 1.1, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 0.72, 2013: 0.72, 2019: 0.9},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Playing area",
        lpd_by_year={1999: 1.9, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.2, 2013: 1.2, 2019: 0.85},
    ),
    BuildingSpaceTypeLPD(
        building_type="Hospital / Healthcare Facility",
        section_type="Emergency",
        lpd_by_year={1999: 2.8, 2001: 2.7, 2004: 2.7, 2007: 2.7, 2010: 2.26, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Exam/treatment",
        lpd_by_year={1999: 1.6, 2001: 1.5, 2004: 1.5, 2007: 1.5, 2010: 1.66, 2013: 1.66, 2019: 1.4},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Imaging / radiology",
        lpd_by_year={1999: 0.4, 2001: 0.4, 2004: 0.4, 2007: 0.4, 2010: 1.32, 2013: 1.51, 2019: 0.94},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Medical supply",
        lpd_by_year={1999: 3.0, 2001: 1.4, 2004: 1.4, 2007: 1.4, 2010: 1.27, 2013: 0.74, 2019: 0.62},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Nursery",
        lpd_by_year={1999: 1.0, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: 0.88, 2013: 0.88, 2019: 0.92},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Nurse’s station",  # noqa: RUF001
        lpd_by_year={1999: 1.8, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.87, 2013: 0.71, 2019: 1.17},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Operating room",
        lpd_by_year={1999: 7.6, 2001: 2.2, 2004: 2.2, 2007: 2.2, 2010: 1.89, 2013: 2.48, 2019: 2.26},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Patient room",
        lpd_by_year={1999: 1.2, 2001: 0.7, 2004: 0.7, 2007: 0.7, 2010: 0.62, 2013: 0.62, 2019: 0.68},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Pharmacy",
        lpd_by_year={1999: 2.3, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.14, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Physical therapy",
        lpd_by_year={1999: 1.9, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 0.91, 2013: 0.91, 2019: 0.91},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Recovery",
        lpd_by_year={1999: 2.6, 2001: 0.8, 2004: 0.8, 2007: 0.8, 2010: 1.15, 2013: 1.15, 2019: 1.25},
    ),
    BuildingSpaceTypeLPD(
        building_type="Library",
        section_type="Card File and Cataloging",
        lpd_by_year={1999: 1.4, 2001: 1.1, 2004: 1.1, 2007: 1.1, 2010: 0.72, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Reading area",
        lpd_by_year={1999: 1.8, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.93, 2013: 1.06, 2019: 0.96},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="The stacks",
        lpd_by_year={1999: 1.9, 2001: 1.7, 2004: 1.7, 2007: 1.7, 2010: 1.71, 2013: 1.71, 2019: 1.18},
    ),
    BuildingSpaceTypeLPD(
        building_type="Manufacturing Facility",
        section_type="Detailed manufacturing area",
        lpd_by_year={1999: 6.2, 2001: 2.1, 2004: 2.1, 2007: 2.1, 2010: 1.29, 2013: 1.29, 2019: 0.8},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Equipment room",
        lpd_by_year={1999: 0.8, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.95, 2013: 0.74, 2019: 0.76},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Extra high bay area (>50 ft height)",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 1.05, 2013: 1.05, 2019: 1.42},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="High bay area (25-50 ft height)",
        lpd_by_year={1999: 3.0, 2001: 1.7, 2004: None, 2007: 1.7, 2010: 1.23, 2013: 1.23, 2019: 1.24},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Low bay area (<25 ft height)",
        lpd_by_year={1999: 2.1, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 1.19, 2013: 1.19, 2019: 0.86},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Control room",
        lpd_by_year={1999: 0.5, 2001: 0.5, 2004: 0.5, 2007: 0.5, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Museum",
        section_type="General exhibition area",
        lpd_by_year={1999: 1.6, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 1.05, 2013: 1.05, 2019: 0.31},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Restoration room",
        lpd_by_year={1999: 2.5, 2001: 1.7, 2004: 1.7, 2007: 1.7, 2010: 1.02, 2013: 1.02, 2019: 1.1},
    ),
    BuildingSpaceTypeLPD(
        building_type="Performing Arts Theater",
        section_type="Dressing Room",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.4, 2013: 0.61, 2019: 0.41},
    ),
    BuildingSpaceTypeLPD(
        building_type="Post Office",
        section_type="Sorting Area",
        lpd_by_year={1999: 1.7, 2001: 1.2, 2004: 1.2, 2007: 1.2, 2010: 0.94, 2013: 0.94, 2019: 0.76},
    ),
    BuildingSpaceTypeLPD(
        building_type="Religious Buildings",
        section_type="Fellowship hall",
        lpd_by_year={1999: 2.3, 2001: 0.9, 2004: 0.9, 2007: 0.9, 2010: 0.64, 2013: 0.64, 2019: 0.54},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Worship/pulpit/choir area",
        lpd_by_year={1999: 5.2, 2001: 2.4, 2004: 2.4, 2007: 2.4, 2010: 1.53, 2013: 1.53, 2019: 0.85},
    ),
    BuildingSpaceTypeLPD(
        building_type="Retail Facilities",
        section_type="Dressing/fitting room",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.87, 2013: 0.71, 2019: 0.51},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Mall concourse",
        lpd_by_year={1999: 1.8, 2001: 1.7, 2004: 1.7, 2007: 1.7, 2010: 1.1, 2013: 1.1, 2019: 0.82},
    ),
    BuildingSpaceTypeLPD(
        building_type="Sports Arena Class I facility",
        section_type="Playing Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 3.01, 2013: 3.68, 2019: 2.94},
    ),
    BuildingSpaceTypeLPD(
        building_type="Sports Arena Class II facility",
        section_type="Playing Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 1.92, 2013: 2.4, 2019: 2.01},
    ),
    BuildingSpaceTypeLPD(
        building_type="Sports Arena Class III facility",
        section_type="Playing Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 1.2, 2013: 1.8, 2019: 1.3},
    ),
    BuildingSpaceTypeLPD(
        building_type="Sports Arena Class IV facility",
        section_type="Playing Area",
        lpd_by_year={1999: None, 2001: None, 2004: None, 2007: None, 2010: 0.72, 2013: 1.2, 2019: 0.86},
    ),
    BuildingSpaceTypeLPD(
        building_type="Ring Sports Arena",
        section_type="Playing Area",
        lpd_by_year={1999: 3.8, 2001: 2.7, 2004: 2.7, 2007: 2.7, 2010: 2.68, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Court Sports Area",
        section_type="Playing Area",
        lpd_by_year={1999: 4.3, 2001: 2.3, 2004: 2.3, 2007: 2.3, 2010: None, 2013: None, 2019: None},
    ),
    BuildingSpaceTypeLPD(
        building_type="Transportation Facility",
        section_type="Baggage / carousel area",
        lpd_by_year={1999: 1.3, 2001: 1.0, 2004: 1.0, 2007: 1.0, 2010: 0.76, 2013: 0.53, 2019: 0.39},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Airport concourse",
        lpd_by_year={1999: 0.7, 2001: 0.6, 2004: 0.6, 2007: 0.6, 2010: 0.36, 2013: 0.36, 2019: 0.25},
    ),
    BuildingSpaceTypeLPD(
        building_type="Other",
        section_type="Ticket counter",
        lpd_by_year={1999: 1.8, 2001: 1.5, 2004: 1.5, 2007: 1.5, 2010: 1.08, 2013: 0.8, 2019: 0.51},
    ),
    BuildingSpaceTypeLPD(
        building_type="Warehouse",
        section_type="Storage Area",
        lpd_by_year={1999: 1.35, 2001: 1.15, 2004: 1.15, 2007: 1.15, 2010: 0.76, 2013: 0.76, 2019: 0.51},
    ),
]
