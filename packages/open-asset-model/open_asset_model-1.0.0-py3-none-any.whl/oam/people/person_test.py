import json
import pytest
from oam.people.person import Person
from oam.asset import AssetType
from oam.asset import Asset

def test_person_key():
    want = "222333444"
    p = Person(id=want, full_name="Jeff Foley")

    assert p.key == want


def test_person_asset_type():
    assert issubclass(Person, Asset)

    p = Person(id="", full_name="")
    assert p.asset_type == AssetType.Person


def test_person_json():
    p = Person(
        id="222333444",
        full_name="John Jacob Doe",
        first_name="John",
        middle_name="Jacob",
        family_name="Doe",
        birth_date="01/01/1970",
        gender="Male",
    )

    expected_json = {
        "unique_id": "222333444",
        "full_name": "John Jacob Doe",
        "first_name": "John",
        "middle_name": "Jacob",
        "family_name": "Doe",
        "birth_date": "01/01/1970",
        "gender": "Male"
    }

    json_data = p.to_dict()

    assert json_data == expected_json
