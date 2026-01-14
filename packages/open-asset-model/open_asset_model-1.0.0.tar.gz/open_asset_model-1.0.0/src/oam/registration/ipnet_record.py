from dataclasses import dataclass
from dataclasses import field
from typing import Optional, List
from oam.asset import Asset
from oam.asset import AssetType

@dataclass
class IPNetRecord(Asset):
    """IPNetRecord represents the RDAP record for an IP network."""
    cidr:          str
    handle:        str
    type:          str
    name:          str
    created_date:  str
    updated_date:  str
    start_address: str
    end_address:   str
    raw:           Optional[str] = None
    method:        Optional[str] = None
    country:       Optional[str] = None
    parent_handle: Optional[str] = None
    whois_server:  Optional[str] =  None
    status:        Optional[List[str]] =  None

    @property
    def key(self) -> str:
        return self.handle

    @property
    def asset_type(self) -> AssetType:
        return AssetType.IPNetRecord
