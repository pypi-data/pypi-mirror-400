from dataclasses import dataclass
from dataclasses import field
from oam.property import Property, PropertyType

@dataclass
class SourceProperty(Property):
    """SourceProperty represents a source of data in the graph."""
    source: str = field(metadata={"json":"name"})
    confidence: int

    @property
    def name(self) -> str:
        return self.source

    @property
    def value(self) -> str:
        return str(self.confidence)

    @property
    def property_type(self) -> PropertyType:
        return PropertyType.SourceProperty
