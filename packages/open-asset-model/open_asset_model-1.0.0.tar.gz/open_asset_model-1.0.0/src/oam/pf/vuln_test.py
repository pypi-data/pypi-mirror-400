import pytest
import json
from oam.pf.vuln import VulnProperty
from oam.property import Property
from oam.property import PropertyType

def test_vuln_property_name():
    want = "CVE-2019-00001"
    sp = VulnProperty(
        id="CVE-2019-00001",
        description="In macOS before 2.12.6, there is a vulnerability in the RPC...",
        source="Tenable",
        category="Firewall",
        enumeration="CVE",
        reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-6111",
    )
    assert sp.name == want

def test_vuln_property_value():
    want = "In macOS before 2.12.6, there is a vulnerability in the RPC..."
    sp = VulnProperty(
        id="CVE-2019-00001",
        description="In macOS before 2.12.6, there is a vulnerability in the RPC...",
        source="Tenable",
        category="Firewall",
        enumeration="CVE",
        reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-6111",
    )
    assert sp.value == want

def test_vuln_property_implements_property():
    assert issubclass(VulnProperty, Property)

def test_vuln_property_creation():
    sp = VulnProperty(
        id="CVE-2019-00001",
        description="In macOS before 2.12.6, there is a vulnerability in the RPC...",
        source="Tenable",
        category="Firewall",
        enumeration="CVE",
        reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-6111",
    )

    assert sp.id == "CVE-2019-00001"
    assert sp.description == "In macOS before 2.12.6, there is a vulnerability in the RPC..."
    assert sp.source == "Tenable"
    assert sp.category == "Firewall"
    assert sp.enumeration == "CVE"
    assert sp.reference == "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-6111"
    assert sp.property_type == PropertyType.VulnProperty

def test_vuln_property_json_serialization():
    sp = VulnProperty(
        id="CVE-2019-00001",
        description="foobar",
        source="Tenable",
        category="Firewall",
        enumeration="CVE",
        reference="URL",
    )

    json_data = sp.to_dict()
    expected_json = { 
        "id": "CVE-2019-00001",
        "desc": "foobar",
        "source": "Tenable",
        "category": "Firewall",
        "enum": "CVE",
        "ref": "URL"
    }
    assert json_data == expected_json
