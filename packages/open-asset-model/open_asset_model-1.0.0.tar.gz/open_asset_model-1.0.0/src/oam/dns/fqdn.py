from dataclasses import dataclass
from oam.asset import AssetType
from oam.asset import Asset

@dataclass
class FQDN(Asset):
    """FQDN represents a Fully Qualified Domain Name."""
    name: str
    
    @property
    def key(self) -> str:
        return self.name

    @property
    def asset_type(self) -> AssetType:
        return AssetType.FQDN
