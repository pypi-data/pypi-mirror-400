import pytest
import json
from oam.contact.location import Location
from oam.asset import Asset
from oam.asset import AssetType

def test_location_key():
    want = "123 Some Road New York NY"
    loc = Location(address=want)

    assert loc.key == want

def test_location_asset_type():
    assert issubclass(Location, Asset)

    loc = Location(address="example")
    assert loc.asset_type == AssetType.Location

def test_location_json():
    loc = Location(
        address="123 Main St",
        building="Building A",
        building_number="123",
        street_name="Main St",
        unit="Apt 1",
        po_box="P.O. Box 145",
        city="Anytown",
        locality="Anytown",
        province="Anyregion",
        country="US",
        postal_code="12345",
        gln=1234567890123,
    )

    expected_json = {
        "address": "123 Main St",
        "building": "Building A",
        "building_number": "123",
        "street_name": "Main St",
        "unit": "Apt 1",
        "po_box": "P.O. Box 145",
        "city": "Anytown",
        "locality": "Anytown",
        "province": "Anyregion",
        "country": "US",
        "postal_code": "12345",
        "gln": 1234567890123,
    }

    json_data = loc.to_dict()
    assert json_data == expected_json
