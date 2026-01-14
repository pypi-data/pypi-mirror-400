from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from enum import Enum
from oam.asset import Asset
from oam.asset import AssetType

@dataclass
class Product(Asset):
    """Product represents a technology product and organizes the
    product releases in the data model.
    
    Should support relationships for the following:
    - Manufacturer (e.g. Organization)
    - Website
    - Product releases
    """
    id:                str = field(metadata={"json":"unique_id"})
    name:              str = field(metadata={"json":"product_name"})
    type:              str = field(metadata={"json":"product_type"})
    category:          Optional[str] = None
    description:       Optional[str] = None
    country_of_origin: Optional[str] = None

    @property
    def key(self) -> str:
        return self.id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Product

@dataclass
class ProductRelease(Asset):
    """ProductRelease represents a release of a technology product
    that belongs to a Product.

    Should support relationships for the following:
    - Amazon Standard Identification Number (ASIN)
    - Global Trade Item Number (GTIN)
    - International Article Number (EAN)
    - International Standard Book Number (ISBN)
    - Manufacturer Part Number (MPN)
    - Model Number
    - NATO Stock Number (NSN)
    - Serial Number
    - Universal Product Code (UPC)
    - Version Number
    - Vulnerabilities
    - Website with release details

    """
    name: str
    release_date: Optional[str] = None

    @property
    def key(self) -> str:
        return self.name

    @property
    def asset_type(self) -> AssetType:
        return AssetType.ProductRelease
