from dataclasses import dataclass
from typing import Optional, List
import json
import pytest
from oam.registration.ipnet_record import IPNetRecord
from oam.asset import Asset, AssetType

def test_ipnet_record_key():
    want = "NET-150-154-0-0-1"
    as_record = IPNetRecord(handle=want, cidr="150.154.0.0/16",
                             start_address="150.154.0.0",
                             end_address="150.154.255.255",
                             type="IPv4", name="REV-MVCC", created_date="1991-05-20",
                             updated_date="2024-03-28")
    
    assert as_record.key == want


def test_ipnet_record_asset_type():
    assert issubclass(IPNetRecord, Asset)
    assert isinstance(IPNetRecord, type)

    w = IPNetRecord(cidr="150.154.0.0/16", handle="NET-150-154-0-0-1", 
                    start_address="150.154.0.0", 
                    end_address="150.154.255.255",
                    type="IPv4", name="REV-MVCC", created_date="1991-05-20", 
                    updated_date="2024-03-28")
    
    want = AssetType.IPNetRecord

    assert w.asset_type == want


def test_ipnet_record():
    record = IPNetRecord(
        cidr="150.154.0.0/16",
        handle="NET-150-154-0-0-1",
        start_address="150.154.0.0",
        end_address="150.154.255.255",
        type="IPv4",
        name="REV-MVCC",
        method="DIRECT ALLOCATION",
        parent_handle="NET-150-0-0-0-0",
        whois_server="whois.arin.net",
        created_date="1991-05-20 04:00:00",
        updated_date="2024-03-28 18:47:50",
        status=["active"],
    )

    # Test AssetType method
    assert record.asset_type == AssetType.IPNetRecord

    # Test JSON method
    expected_json = {
        "cidr": "150.154.0.0/16",
        "handle": "NET-150-154-0-0-1",
        "start_address": "150.154.0.0",
        "end_address": "150.154.255.255",
        "type": "IPv4",
        "name": "REV-MVCC",
        "method": "DIRECT ALLOCATION",
        "parent_handle": "NET-150-0-0-0-0",
        "whois_server": "whois.arin.net",
        "created_date": "1991-05-20 04:00:00",
        "updated_date": "2024-03-28 18:47:50",
        "status": ["active"]}
    
    json_data = record.to_dict()
    assert json_data == expected_json
