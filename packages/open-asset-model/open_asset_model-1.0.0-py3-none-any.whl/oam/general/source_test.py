import pytest
from oam.general.source import SourceProperty
from oam.property import Property
from oam.property import PropertyType

def test_source_property_name():
    want = "anything"
    sp = SourceProperty(source="anything", confidence=80)
    
    assert sp.name == want

def test_source_property_value():
    want = "80"
    sp = SourceProperty(source="anything", confidence=80)
    
    assert sp.value == want

def test_source_property_implements_property():
    assert issubclass(SourceProperty, Property)

def test_source_property_creation():
    sp = SourceProperty(source="anything", confidence=80)

    assert sp.source == "anything"
    assert sp.confidence == 80
    assert sp.property_type == PropertyType.SourceProperty

def test_source_property_json_serialization():
    sp = SourceProperty(source="anything", confidence=80)

    expected = {
        "name": "anything",
        "confidence": 80
    }
    
    assert sp.to_dict() == expected
