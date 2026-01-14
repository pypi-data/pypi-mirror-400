import json
import pytest
from oam.certificate.tls_certificate import TLSCertificate, AssetType

def test_tls_certificate_key():
    want = "12345"
    cert = TLSCertificate(
        subject_common_name="www.example.org",
        issuer_common_name="DigiCert TLS RSA SHA256 2020 CA1",
        not_before="2006-01-02T15:04:05Z07:00",
        not_after="2006-01-02T15:04:05Z07:00",
        version="",
        serial_number=want,
        key_usage=[],
        ext_key_usage=[],
        signature_algorithm="",
        public_key_algorithm="",
        is_ca=False,
        crl_distribution_points=[],
        subject_key_id="",
        authority_key_id=""
    )
    
    assert cert.key == want

def test_tls_certificate_asset_type():
    cert = TLSCertificate(
        subject_common_name="www.example.org",
        issuer_common_name="DigiCert TLS RSA SHA256 2020 CA1",
        not_before="2006-01-02T15:04:05Z07:00",
        not_after="2006-01-02T15:04:05Z07:00",
        version="",
        serial_number="",
        key_usage=[],
        ext_key_usage=[],
        signature_algorithm="",
        public_key_algorithm="",
        is_ca=False,
        crl_distribution_points=[],
        subject_key_id="",
        authority_key_id=""
    )
    want = AssetType.TLSCertificate

    assert cert.asset_type == want

def test_tls_certificate_json():
    cert = TLSCertificate(
        subject_common_name="www.example.org",
        issuer_common_name="DigiCert TLS RSA SHA256 2020 CA1",
        not_before="2006-01-02T15:04:05Z07:00",
        not_after="2006-01-02T15:04:05Z07:00",
        version="",
        serial_number="",
        key_usage=[],
        ext_key_usage=[],
        signature_algorithm="",
        public_key_algorithm="",
        is_ca=False,
        crl_distribution_points=[],
        subject_key_id="",
        authority_key_id=""
    )

    # test AssetType method
    assert cert.asset_type == AssetType.TLSCertificate

    # test JSON method
    expected_json = {
        "version": "",
        "serial_number": "",
        "subject_common_name": "www.example.org",
        "issuer_common_name": "DigiCert TLS RSA SHA256 2020 CA1",
        "not_before": "2006-01-02T15:04:05Z07:00",
        "not_after": "2006-01-02T15:04:05Z07:00",
        "key_usage": [],
        "ext_key_usage": [],
        "signature_algorithm": "",
        "public_key_algorithm": "",
        "is_ca": False,
        "crl_distribution_points": [],
        "subject_key_id": "",
        "authority_key_id": ""
    }
    json_output = cert.to_dict()
    
    assert json_output == expected_json
