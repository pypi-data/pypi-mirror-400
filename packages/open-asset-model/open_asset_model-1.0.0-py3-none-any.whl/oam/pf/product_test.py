import json
import pytest
from oam.pf.product import Product
from oam.pf.product import ProductRelease
from oam.asset import Asset
from oam.asset import AssetType

def test_product_key():
    want = "12345"
    p = Product(id=want, name="OWASP Amass", type="Information Security")

    assert p.key == want

def test_product_asset_type():
    assert issubclass(Product, Asset)
    assert issubclass(Product, Asset)
    p = Product(id="dummy", name="dummy", type="dummy")

    assert p.asset_type == AssetType.Product

def test_product_json():
    p = Product(
        id="12345",
        name="OWASP Amass",
        type="Attack Surface Management",
        category="Information Security",
        description="In-depth attack surface mapping and asset discovery",
        country_of_origin="US"
    )
    expected = {
        "unique_id": "12345",
        "product_name": "OWASP Amass",
        "product_type": "Attack Surface Management",
        "category": "Information Security",
        "description": "In-depth attack surface mapping and asset discovery",
        "country_of_origin": "US"
    }
    
    actual = p.to_dict()
    
    assert actual == expected

def test_product_release_key():
    want = "Amass v4.2.0"
    p = ProductRelease(name=want)

    assert p.key == want


def test_product_release_asset_type():
    assert issubclass(ProductRelease, Asset)
    assert issubclass(ProductRelease, Asset)
    p = ProductRelease(name="dummy")

    assert p.asset_type == AssetType.ProductRelease

def test_product_release_json():
    p = ProductRelease(
        name="Amass v4.2.0",
        release_date="2023-09-10T14:15:00Z"
    )
    expected = {
        "name": "Amass v4.2.0",
        "release_date": "2023-09-10T14:15:00Z"
    }
    
    actual = p.to_dict()
    
    assert actual == expected
