from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from enum import Enum
from oam.asset import Asset
from oam.asset import AssetType

@dataclass
class Account(Asset):
    """Account represents an account managed by an organization.
    
    Should support relationships for the following:
    - User (e.g. Person or Organization)
    - Funds transfers
    - IBAN and SWIFT codes
    """
    id:             str = field(metadata={"json":"unique_id"})
    account_type:   str
    username:       Optional[str]   = None
    account_number: Optional[str]   = None
    balance:        Optional[float] = None
    active:         Optional[bool]  = None

    @property
    def key(self) -> str:
        return self.id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Account
