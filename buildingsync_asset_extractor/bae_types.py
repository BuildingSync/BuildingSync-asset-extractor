from dataclasses import dataclass
from typing import Any


@dataclass
class Section:
    type: str | None
    areas: dict[str, float]


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
    units: str | None = None


@dataclass
class SystemData:
    value: Any
    sqft: float | None = None
    cap: float | str | None = None
    cap_units: str | None = None
    units: str | None = None
