from dataclasses import dataclass
from typing import List, Optional
from oam.asset import Asset, AssetType
import json


@dataclass
class DomainRecord(Asset):
    """DomainRecord represents the WHOIS record of a domain."""
    domain:          str
    id:              Optional[str] = None
    raw:             Optional[str] = None
    punycode:        Optional[str] = None
    name:            Optional[str] = None
    extension:       Optional[str] = None
    whois_server:    Optional[str] = None
    created_date:    Optional[str] = None
    updated_date:    Optional[str] = None
    expiration_date: Optional[str] = None
    status:          Optional[List[str]] = None
    dnssec:          Optional[bool] = None

    @property
    def key(self) -> str:
        return self.domain

    @property
    def asset_type(self) -> AssetType:
        return AssetType.DomainRecord
