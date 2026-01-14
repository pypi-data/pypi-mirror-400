from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from urllib.parse import urlparse
from oam.asset import Asset
from oam.asset import AssetType

@dataclass
class URL(Asset):
    """URL represents a URL."""
    raw:      str           = field(metadata={"json":"url"})
    scheme:   Optional[str] = None
    host:     Optional[str] = None
    path:     Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    port:     Optional[int] = None
    options:  Optional[str] = None
    fragment: Optional[str] = None

    @property
    def key(self) -> str:
        return self.raw

    @property
    def asset_type(self) -> AssetType:
        return AssetType.URL

    @staticmethod
    def from_text(url: str) -> 'URL':
        o = urlparse(url)
        return URL(
            raw=url,
            scheme=o.scheme,
            host=o.hostname or "",
            path=o.path,
            username=o.username,
            password=o.password,
            port=o.port,
            options=o.query,
            fragment=o.fragment
        )
