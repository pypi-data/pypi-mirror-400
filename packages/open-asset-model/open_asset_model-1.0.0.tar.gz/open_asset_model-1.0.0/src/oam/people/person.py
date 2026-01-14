from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Optional
from oam.asset import Asset, AssetType

@dataclass
class Person(Asset):
    """Person represents a person's information."""
    id:          str = field(metadata={"json":"unique_id"})
    full_name:   str
    first_name:  Optional[str] = None
    family_name: Optional[str] = None
    middle_name: Optional[str] = None
    birth_date:  Optional[str] = None
    gender:      Optional[str] = None

    @property
    def key(self) -> str:
        return self.id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Person
