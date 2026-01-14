import pytest
import json
from oam.account.account import Account
from oam.asset import Asset
from oam.asset import AssetType

def test_account_key():
    expected = "222333444"
    a = Account(
        id=expected,
        username="test",
        account_number="12345",
        account_type="ACH"
    )

    assert a.key == expected

def test_account_asset_type():
    assert issubclass(Account, Asset)

    a = Account(id="test_id", account_type="test")
    expected = AssetType.Account
    actual = a.asset_type

    assert actual == expected

def test_account_json():
    a = Account(
        id="222333444",
        account_type="ACH",
        username="test",
        account_number="12345",
        balance=42.50,
        active=True
    )
    expected = {
        "unique_id": "222333444",
        "account_type": "ACH",
        "username": "test",
        "account_number": "12345",
        "balance": 42.50,
        "active": True
    }
    actual = a.to_dict()

    assert actual == expected
