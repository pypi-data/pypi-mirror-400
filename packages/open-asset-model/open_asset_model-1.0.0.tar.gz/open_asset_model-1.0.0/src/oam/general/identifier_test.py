import json
import pytest
from oam.general.identifier import Identifier
from oam.general.identifier import IdentifierType
from oam.asset import AssetType

def test_identifier_key():
    want = "Legal Entity Identifier:549300XMYB546ZI1F126"
    i = Identifier(
        unique_id=want,
        id="549300XMYB546ZI1F126",
        type=IdentifierType.LEICode
    )
    
    assert i.key == want

def test_identifier_asset_type():
    i = Identifier(unique_id="", id="",
        type=IdentifierType.LEICode)
    
    expected = AssetType.Identifier
    actual = i.asset_type
    
    assert actual == expected

def test_identifier_json():
    i = Identifier(
        unique_id="Legal Entity Identifier:549300XMYB546ZI1F126",
        id="549300XMYB546ZI1F126",
        type=IdentifierType.LEICode,
        creation_date="2013-07-24T14:15:00Z",
        update_date="2023-08-04T17:33:45Z",
        expiration_date="2020-01-16T00:32:00Z",
        status="ACTIVE"
    )
    
    expected = {
        "unique_id":"Legal Entity Identifier:549300XMYB546ZI1F126",
        "id":"549300XMYB546ZI1F126",
        "id_type":"lei",
        "creation_date":"2013-07-24T14:15:00Z",
        "update_date":"2023-08-04T17:33:45Z",
        "expiration_date":"2020-01-16T00:32:00Z",
        "status":"ACTIVE"
    }

    assert i.to_dict() == expected
