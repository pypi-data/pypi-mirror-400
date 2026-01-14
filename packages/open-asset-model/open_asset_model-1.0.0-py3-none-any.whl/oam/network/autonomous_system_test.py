import json
import pytest
from oam.network.autonomous_system import AutonomousSystem
from oam.asset import Asset
from oam.asset import AssetType

def test_autonomous_system_key():
    want = 26808
    as_system = AutonomousSystem(number=want)

    assert as_system.key == str(want)

def test_autonomous_system_asset():
    assert issubclass(AutonomousSystem, Asset)

def test_autonomous_system_creation():
    as_system = AutonomousSystem(number=64496)

    assert as_system.number == 64496
    assert as_system.asset_type == AssetType.AutonomousSystem

def test_autonomous_system_json():
    as_system = AutonomousSystem(number=64496)

    expected_json = {"number": 64496}
    assert as_system.to_dict() == expected_json
