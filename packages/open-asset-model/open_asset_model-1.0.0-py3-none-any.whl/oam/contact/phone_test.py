import json
import pytest
from oam.contact.phone import Phone
from oam.contact.phone import PhoneType
from oam.asset import Asset
from oam.asset import AssetType

def test_phone_key():
    want = "+12345556666"
    p = Phone.from_text(want)
    assert p.key == want

def test_phone_asset_type():
    p = Phone.from_text("+12345556666")
    assert isinstance(p, Asset)
    assert p.asset_type == AssetType.Phone

def test_phone_json():
    p = Phone(
        raw="123-456-7890 Ext. 123",
        e164="+1234567890",
        type=PhoneType.Mobile,
        country_abbrev="US",
        country_code=1,
        ext="123",
    )

    expected_json = {
        "raw":"123-456-7890 Ext. 123",
        "e164":"+1234567890",
        "type":"mobile",
        "country_abbrev":"US",
        "country_code":1,
        "ext":"123"
    }

    phone_json = p.to_dict()
    assert phone_json == expected_json
