from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Section:
    type: Optional[str]
    areas: dict


@dataclass
class Asset:
    name: str
    value: Any


@dataclass
class AssetData:
    assets: list[Asset]


@dataclass
class AssetDef:
    name: str
    type: str
    export_name: str
    parent_path: str
    key: str
    export_units: bool
    units: Optional[str] = None


@dataclass
class SystemData:
    value: Any
    sqft: Optional[float] = None
    cap: Optional[str] = None
    cap_units: Optional[str] = None
    units: Optional[str] = None
