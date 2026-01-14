import json
import pytest

from oam.network.ip_address import IPAddress
from oam.network.ip_address import IPAddressType
from oam.asset import Asset
from oam.asset import AssetType

def test_ip_address_key():
    want = "1.1.1.1"
    ip = IPAddress(address=want, type=IPAddressType.IPv4) 
    assert ip.key == want

def test_ip_address_asset():
    assert issubclass(IPAddress, Asset)

def test_ip_address(subtests):
    tests = [
        {
            "description": "Test successful creation of IPAddress with valid IPv4 address",
            "ip": "192.168.1.1",
            "net_type": IPAddressType.IPv4,
        },
        {
            "description": "Test successful creation of IPAddress with valid IPv6 address",
            "ip": "2001:db8::1",
            "net_type": IPAddressType.IPv6,
        },
    ]
    
    for tt in tests:
        with subtests.test(tt["description"]):
            ip = tt["ip"]
            ip_address = IPAddress(address=ip, type=tt["net_type"])

            assert ip_address.address is not None
            assert ip_address.address == ip
            assert ip_address.type is tt["net_type"]
            assert ip_address.asset_type is AssetType.IPAddress

def test_ip_address_json(subtests):
    tests = [
        {
            "description": "Test successful JSON serialization of IPAddress with valid IPv4 address",
            "ip": "192.168.1.1",
            "net_type": IPAddressType.IPv4,
        },
        {
            "description": "Test successful JSON serialization of IPAddress with valid IPv6 address",
            "ip": "2001:db8::1",
            "net_type": IPAddressType.IPv6,
        },
    ]
    
    for tt in tests:
        with subtests.test(tt["description"]):
            ip = tt["ip"]
            ip_address = IPAddress(address=ip, type=tt["net_type"])

            json_data = ip_address.to_dict()
            expected_json = {"address": tt["ip"], "type": tt["net_type"]}
            assert json_data == expected_json
