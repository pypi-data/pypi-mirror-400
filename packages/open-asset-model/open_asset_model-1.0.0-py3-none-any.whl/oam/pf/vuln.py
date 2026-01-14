from dataclasses import dataclass
from typing import Optional
from oam.property import Property, PropertyType


@dataclass
class VulnProperty(Property):
    """VulnProperty represents a simple property in the graph."""
    id:          str
    description: str
    source:      Optional[str] = None
    category:    Optional[str] = None
    enumeration: Optional[str] = None
    reference:   Optional[str] = None

    @property
    def name(self) -> str:
        return self.id

    @property
    def value(self) -> str:
        return self.description

    @property
    def property_type(self) -> PropertyType:
        return PropertyType.VulnProperty

    def to_dict(self) -> dict:
        return {key: value for key, value in {
            "id":       self.id,
            "desc":     self.description,
            "source":   self.source,
            "category": self.category,
            "enum":     self.enumeration,
            "ref":      self.reference,
        }.items() if value is not None}
