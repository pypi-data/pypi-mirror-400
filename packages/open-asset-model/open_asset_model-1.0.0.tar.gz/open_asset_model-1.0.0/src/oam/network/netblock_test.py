import json
from oam.network.netblock import Netblock
from oam.network.netblock import NetblockType
from oam.asset import Asset
from oam.asset import AssetType

def test_netblock_key():
    want = "192.168.1.0/24"
    netblock = Netblock(cidr=want, type=NetblockType.IPv4) 
    assert netblock.key == want

def test_netblock_implements_asset():
    assert issubclass(Netblock, Asset)

def test_netblock(subtests):
    tests = [
        {
            "description": "Test successful creation of Netblock with valid IPv4 CIDR",
            "cidr": "198.51.100.0/24",
            "net_type": NetblockType.IPv4,
        },
        {
            "description": "Test successful creation of Netblock with valid IPv6 CIDR",
            "cidr": "2001:db8::/32",
            "net_type": NetblockType.IPv4,
        },
    ]
    
    for tt in tests:
        with subtests.test(tt["description"]):
            netblock = Netblock(cidr=tt["cidr"], type=tt["net_type"])

            assert netblock.cidr == tt["cidr"]
            assert netblock.type == tt["net_type"]
            assert netblock.asset_type == AssetType.Netblock

def test_netblock_json(subtests):
    tests = [
        {
            "description": "Test successful JSON serialization of Netblock with valid IPv4 CIDR",
            "cidr": "198.51.100.0/24",
            "type": NetblockType.IPv4,
        },
        {
            "description": "Test successful JSON serialization of Netblock with valid IPv6 CIDR",
            "cidr": "2001:db8::/32",
            "type": NetblockType.IPv6,
        },
    ]
    
    for tt in tests:
        with subtests.test(tt["description"]):
            netblock = Netblock(cidr=tt["cidr"], type=tt["type"])

            json_data = netblock.to_dict()
            
            expected_json = {"cidr": tt["cidr"], "type": tt["type"]}
            assert json_data == expected_json
