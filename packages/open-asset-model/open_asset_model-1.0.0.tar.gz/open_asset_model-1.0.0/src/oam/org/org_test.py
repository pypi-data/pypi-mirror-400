import pytest
import json
from oam.org.org import Organization
from oam.asset import AssetType

def test_organization_key():
    want = "222333444"
    o = Organization(id=want, name="OWASP Foundation")
    assert o.key == want

def test_organization_asset_type():
    o = Organization(id="222333444", name="OWASP Foundation")
    expected = AssetType.Organization
    actual = o.asset_type
    assert actual == expected

def test_organization_json():
    o = Organization(
        id="222333444",
        name="Acme Inc.",
        legal_name="Acme Inc.",
        founding_date="2013-07-24T14:15:00Z",
        jurisdiction="US-DE",
        registration_id="123456789",
        industry="Technology",
        target_markets=["Apps", "Software"],
        active=True,
        non_profit=False,
        headcount=10000,
    )
    expected = {
        "unique_id": "222333444",
        "name": "Acme Inc.",
        "legal_name": "Acme Inc.",
        "founding_date": "2013-07-24T14:15:00Z",
        "jurisdiction": "US-DE",
        "registration_id": "123456789",
        "industry": "Technology",
        "target_markets": ["Apps", "Software"],
        "active": True,
        "non_profit": False,
        "headcount": 10000
    }
    actual = o.to_dict()
    assert actual == expected
