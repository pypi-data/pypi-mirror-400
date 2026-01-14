import pytest
import json
from oam.financial.funds_transfer import FundsTransfer
from oam.asset import AssetType

def test_funds_transfer_key():
    want = "222333444"
    ft = FundsTransfer(id=want, amount=42.0)

    assert ft.key == want

def test_funds_transfer_asset_type():
    ft = FundsTransfer(id="222333444", amount=42.0)
    expected = AssetType.FundsTransfer
    actual = ft.asset_type

    assert actual == expected

def test_funds_transfer_json():
    ft = FundsTransfer(
        id="222333444",
        amount=42.0,
        reference_number="555666777",
        currency="US",
        method="ACH",
        exchange_date="2013-07-24T14:15:00Z",
        exchange_rate=0.9,
    )
    expected = {
        "unique_id": "222333444",
        "amount": 42.0,
        "reference_number": "555666777",
        "currency": "US",
        "transfer_method": "ACH",
        "exchange_date": "2013-07-24T14:15:00Z",
        "exchange_rate": 0.9
    }
    
    assert ft.to_dict() == expected
