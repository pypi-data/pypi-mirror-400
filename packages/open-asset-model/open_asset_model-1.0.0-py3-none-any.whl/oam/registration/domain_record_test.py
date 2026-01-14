import json
import pytest
from oam.registration.domain_record import DomainRecord
from oam.asset import AssetType
from oam.asset import Asset

def test_domain_record_key():
    want = "owasp.org"
    dr = DomainRecord(domain=want, raw="", id="")
    assert dr.key == want

def test_domain_record_asset_type():
    assert issubclass(DomainRecord, Asset)  # Verify proper implementation of the Asset interface
    w = DomainRecord(raw="", id="", domain="")
    want = AssetType.DomainRecord
    assert w.asset_type == want

def test_domain_record():
    record = DomainRecord(
        domain="example.com",
        created_date="2020-01-01",
        updated_date="2021-01-01",
        expiration_date="2022-01-01",
        status=["active", "clientTransferProhibited"],
        dnssec=True,
    )

    # Test AssetType method
    assert record.asset_type == AssetType.DomainRecord

    # Test JSON method
    expected_json = {
        "domain":"example.com",
        "created_date":"2020-01-01",
        "updated_date":"2021-01-01",
        "expiration_date":"2022-01-01",
        "status":["active","clientTransferProhibited"],
        "dnssec":True
    }
    actual_json = record.to_dict()
    assert actual_json == expected_json
