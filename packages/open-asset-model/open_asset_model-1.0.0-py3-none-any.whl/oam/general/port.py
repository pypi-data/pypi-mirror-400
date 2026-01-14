from dataclasses import dataclass
from dataclasses import field
from oam.relation import Relation, RelationType
import json

@dataclass
class PortRelation(Relation):
    """PortRelation is a relation in the graph representing an open
    port."""
    name: str = field(metadata={"json":"label"})
    port_number: int
    protocol: str
    
    @property
    def label(self) -> str:
        return self.name

    @property
    def relation_type(self) -> RelationType:
        return RelationType.PortRelation
