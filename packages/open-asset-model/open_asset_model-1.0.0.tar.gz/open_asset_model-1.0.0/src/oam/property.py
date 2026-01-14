import json
from oam.oam_object import OAMObject
from abc import abstractmethod
from enum import Enum
from dataclasses import dataclass

class PropertyType(str, Enum):
    DNSRecordProperty = "DNSRecordProperty"
    SimpleProperty = "SimpleProperty"
    SourceProperty = "SourceProperty"
    VulnProperty = "VulnProperty"

class Property(OAMObject):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> str:
        pass

    @property
    @abstractmethod
    def property_type(self) -> PropertyType:
        pass

PropertyList = list(PropertyType)
