import json
import pytest
from oam.registration.autnum_record import AutnumRecord
from oam.asset import Asset
from oam.asset import AssetType

def test_autnum_record_key():
    want = "AS26808"
    as_record = AutnumRecord(
        number=26808,
        handle="AS26808",
        name="UTICA-COLLEGE",
        whois_server="whois.arin.net",
        created_date="2002-11-25 22:25:46",
        updated_date="2021-05-03 17:59:17",
        status=["active"],
    )

    assert as_record.key == want

def test_autnum_record_asset_type():
    assert issubclass(AutnumRecord, Asset)  

    w = AutnumRecord(
        number=26808,
        handle="AS26808",
        name="UTICA-COLLEGE",
        whois_server="whois.arin.net",
        created_date="2002-11-25 22:25:46",
        updated_date="2021-05-03 17:59:17",
        status=["active"],
    )
    want = AssetType.AutnumRecord

    assert w.asset_type == want

def test_autnum_record():
    record = AutnumRecord(
        number=26808,
        handle="AS26808",
        name="UTICA-COLLEGE",
        whois_server="whois.arin.net",
        created_date="2002-11-25 22:25:46",
        updated_date="2021-05-03 17:59:17",
        status=["active"],
    )

    # Test AssetType method
    assert record.asset_type == AssetType.AutnumRecord

    # Test JSON method
    expected_json = {
        "number": 26808,
        "handle": "AS26808",
        "name": "UTICA-COLLEGE",
        "whois_server": "whois.arin.net",
        "created_date": "2002-11-25 22:25:46",
        "updated_date": "2021-05-03 17:59:17",
        "status": ["active"]
    }
    json_output = record.to_dict()
    
    assert json_output == expected_json
