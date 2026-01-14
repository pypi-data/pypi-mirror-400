from dataclasses import dataclass
from typing import Optional
from oam.asset import Asset, AssetType

@dataclass
class File(Asset):
    """File represents a file discovered, such as a document or image."""
    url: str
    name: Optional[str] = None
    type: Optional[str] = None

    @property
    def key(self) -> str:
        return self.url

    @property
    def asset_type(self) -> AssetType:
        return AssetType.File
