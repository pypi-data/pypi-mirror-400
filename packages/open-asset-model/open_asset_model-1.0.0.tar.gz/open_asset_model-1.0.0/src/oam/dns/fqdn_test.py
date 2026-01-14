import json
from json import JSONDecodeError
from oam.dns.fqdn import FQDN
from oam.asset import Asset
from oam.asset import AssetType

def test_fqdn_key():
    want = "example.com"
    fqdn = FQDN(name=want)

    assert fqdn.key == want

def test_fqdn_implements_asset():
    assert issubclass(FQDN, Asset)

def test_successful_creation_of_fqdn_with_valid_name_and_tld():
    fqdn = FQDN(name="foo.example.com")
    
    assert fqdn.name == "foo.example.com"
    assert fqdn.asset_type == AssetType.FQDN

def test_successful_json_serialization_of_fqdn_with_valid_name_and_tld():
    fqdn = FQDN(name="foo.example.com")
    
    json_data = fqdn.to_dict()
    expected_json = {"name":"foo.example.com"}
    assert json_data == expected_json


