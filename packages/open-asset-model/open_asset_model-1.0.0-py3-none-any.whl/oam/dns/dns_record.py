from enum import Enum
from typing import Optional
from dataclasses import dataclass
from dataclasses import field
from oam.relation import Relation
from oam.relation import RelationType
from oam.property import Property
from oam.property import PropertyType
from oam.oam_object import OAMObject

@dataclass
class BasicDNSRelation(Relation):
    """BasicDNSRelation is a relation in the graph representing a
    basic DNS resource record."""
    name:    str = field(metadata={"json":"label"})
    rrtype:  int = field(metadata={"json":"header_rrtype"})
    cls:     Optional[int] = field(default=None, metadata={"json":"header_class"})
    ttl:     Optional[int] = field(default=None, metadata={"json":"header_ttl"})


    @property
    def relation_type(self) -> RelationType:
        return RelationType.BasicDNSRelation

    @property
    def label(self) -> str:
        return self.name

@dataclass
class PrefDNSRelation(Relation):
    """PrefDNSRelation is a relation in the graph representing a DNS
    resource record with preference information."""
    name:       str = field(metadata={"json":"label"})
    preference: int
    rrtype:     int = field(metadata={"json":"header_rrtype"})
    cls:        Optional[int] = field(default=None, metadata={"json":"header_class"})
    ttl:        Optional[int] = field(default=None, metadata={"json":"header_ttl"})

    @property
    def relation_type(self) -> RelationType:
        return RelationType.PrefDNSRelation

    @property
    def label(self) -> str:
        return self.name

@dataclass
class SRVDNSRelation(Relation):
    """SRVDNSRelation is a relation in the graph representing a DNS
    SRV resource record."""
    name:     str = field(metadata={"json":"label"})
    priority: int
    weight:   int
    port:     int
    rrtype:   int = field(metadata={"json":"header_rrtype"})
    cls:      Optional[int] = field(default=None, metadata={"json":"header_class"})
    ttl:      Optional[int] = field(default=None, metadata={"json":"header_ttl"})

    @property
    def relation_type(self) -> RelationType:
        return RelationType.SRVDNSRelation
    
    @property
    def label(self) -> str:
        return self.name

@dataclass
class DNSRecordProperty(Property):
    """DNSRecordProperty represents a DNS resource record that does
    not refer to another asset in the graph."""
    property_name: str
    data:          str
    rrtype:        int = field(metadata={"json":"header_rrtype"})
    cls:           Optional[int] = field(default=None, metadata={"json":"header_class"})
    ttl:           Optional[int] = field(default=None, metadata={"json":"header_ttl"})

    @property
    def property_type(self) -> PropertyType:
        return PropertyType.DNSRecordProperty
    
    @property
    def name(self) -> str:
        return self.property_name

    @property
    def value(self) -> str:
        return self.data
