import json
from oam.oam_object import OAMObject
from abc import ABC
from abc import abstractmethod
from enum import Enum

class AssetType(str, Enum):
    Account = "Account"
    AutnumRecord = "AutnumRecord"
    AutonomousSystem = "AutonomousSystem"
    ContactRecord = "ContactRecord"
    DomainRecord = "DomainRecord"
    File = "File"
    FQDN = "FQDN"
    FundsTransfer = "FundsTransfer"
    Identifier = "Identifier"
    IPAddress = "IPAddress"
    IPNetRecord = "IPNetRecord"
    Location = "Location"
    Netblock = "Netblock"
    Organization = "Organization"
    Person = "Person"
    Phone = "Phone"
    Product = "Product"
    ProductRelease = "ProductRelease"
    Service = "Service"
    TLSCertificate = "TLSCertificate"
    URL = "URL"

class Asset(OAMObject):
    @property
    @abstractmethod
    def key(self) -> str:
        pass

    @property
    @abstractmethod
    def asset_type(self) -> AssetType:
        pass

AssetList = list(AssetType)

