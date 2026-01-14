from dataclasses import dataclass
from oam.asset import Asset
from oam.asset import  AssetType
from enum import Enum

class IPAddressType(str, Enum):
    IPv4 = "IPv4"
    IPv6 = "IPv6"

@dataclass
class IPAddress(Asset):
    """IPAddress represents an IP address."""
    address: str
    type:    IPAddressType

    @property
    def key(self) -> str:
        return self.address

    @property
    def asset_type(self) -> AssetType:
        return AssetType.IPAddress
