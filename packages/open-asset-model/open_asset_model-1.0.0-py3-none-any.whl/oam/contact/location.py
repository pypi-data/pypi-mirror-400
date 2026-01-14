from dataclasses import dataclass
from typing import Optional
from oam.asset import Asset
from oam.asset import AssetType

@dataclass
class Location(Asset):
    """Location represents the street address location."""
    address:         str
    city:            Optional[str] = None
    building:        Optional[str] = None
    building_number: Optional[str] = None
    street_name:     Optional[str] = None
    unit:            Optional[str] = None
    po_box:          Optional[str] = None
    locality:        Optional[str] = None
    province:        Optional[str] = None
    country:         Optional[str] = None
    postal_code:     Optional[str] = None
    gln:             Optional[int] = None

    @property
    def key(self) -> str:
        return self.address

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Location
