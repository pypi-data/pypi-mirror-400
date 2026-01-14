import pytest
import json
from oam.general.port import PortRelation
from oam.relation import Relation
from oam.relation import RelationType

def test_port_relation_name():
    want = "port"
    pr = PortRelation(
        name=want,
        port_number=80,
        protocol="tcp"
    )

    assert pr.label == want

def test_port_relation_implements_relation():
    assert issubclass(PortRelation, Relation)

def test_port_relation():
    pr = PortRelation(
        name="port",
        port_number=80,
        protocol="tcp"
    )

    assert pr.name == "port"
    assert pr.port_number == 80
    assert pr.protocol == "tcp"
    assert pr.relation_type == RelationType.PortRelation

def test_port_relation_json_serialization():
    pr = PortRelation(
        name="port",
        port_number=80,
        protocol="tcp"
    )

    json_data = pr.to_dict()
    expected_json = {
        "label": "port",
        "port_number": 80,
        "protocol": "tcp"
    }
    
    assert json_data == expected_json
