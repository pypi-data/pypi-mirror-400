from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from enum import Enum
from oam.property import PropertyType
from oam.asset import Asset, AssetType

@dataclass
class FundsTransfer(Asset):
    """FundsTransfer represents a single transfer of funds between two accounts.
    Should support relationships for the following:
    - Sender financial account (e.g. Account)
    - Recipient financial account (e.g. Account)
    - IBIN and SWIFT codes
    """
    id:               str = field(metadata={"json":"unique_id"})
    amount:           float
    reference_number: Optional[str] = None
    currency:         Optional[str] = None
    method:           Optional[str] = field(default=None, metadata={"json":"transfer_method"})
    exchange_date:    Optional[str] = None
    exchange_rate:    Optional[float] = None

    @property
    def key(self) -> str:
        return self.id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.FundsTransfer

    def to_dict(self) -> dict:
        return {key: value for key, value in {
            "unique_id":        self.id,
            "amount":           self.amount,
            "reference_number": self.reference_number,
            "currency":         self.currency,
            "transfer_method":  self.method,
            "exchange_date":    self.exchange_date,
            "exchange_rate":    self.exchange_rate,
        }.items() if value is not None}
