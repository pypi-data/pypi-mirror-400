from dataclasses import dataclass
from dataclasses import field
from typing import List, Optional
from enum import Enum
from oam.asset import Asset, AssetType

@dataclass
class Organization(Asset):
    """Organization represents an organization.
    Should support relationships for the following:
    - Principal place of business
    - Parent organizations
    - Subsidiaries
    - Sister companies
    - DUNS number
    - Tax identification number
    - Trader identification number
    - ARIN organization identifier
    - Decentralized identifier (DID)
    - Ticker symbol
    - Global Location Number (GLN)
    - ISIC, NAICS, SIC, BIC, and ISO 6523 code
    - Legal Entity Identifier (LEI) ISO 17442 code
    - Registration number
    - Website
    - Social media profiles
    - Contact information
    - Founder, sponsorships, and funding sources
    """
    id: str = field(metadata={"json":"unique_id"})
    name: str
    legal_name:      Optional[str] = None
    founding_date:   Optional[str] = None
    jurisdiction:    Optional[str] = None
    registration_id: Optional[str] = None
    industry:        Optional[str] = None
    target_markets:  Optional[List[str]] = None
    active:          Optional[bool] = None
    non_profit:      Optional[bool] = None
    headcount:       Optional[int] = None

    @property
    def key(self) -> str:
        return self.id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Organization
