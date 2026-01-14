from dataclasses import dataclass
from typing import List
from oam.asset import Asset
from oam.asset import AssetType
from enum import Enum

class TLSKeyUsageType(str, Enum):
    KeyUsageDigitalSignature = "Digital Signature"
    KeyUsageContentCommitment = "Content Commitment"
    KeyUsageKeyEncipherment = "Key Encipherment"
    KeyUsageDataEncipherment = "Data Encipherment"
    KeyUsageKeyAgreement = "Key Agreement"
    KeyUsageCertSign = "Certificate Sign"
    KeyUsageCRLSign = "CRL Sign"
    KeyUsageEncipherOnly = "Encipher Only"
    KeyUsageDecipherOnly = "Decipher Only"

class TLSExtKeyUsageType(str, Enum):
    ExtKeyUsageAny = "Any Usage"
    ExtKeyUsageServerAuth = "TLS Server Authentication"
    ExtKeyUsageClientAuth = "TLS Client Authentication"
    ExtKeyUsageCodeSigning = "Code Signing"
    ExtKeyUsageEmailProtection = "E-mail Protection"
    ExtKeyUsageIPSECEndSystem = "IPSec End System"
    ExtKeyUsageIPSECTunnel = "IPSec Tunnel"
    ExtKeyUsageIPSECUser = "IPSec User"
    ExtKeyUsageTimeStamping = "Trusted Timestamping"
    ExtKeyUsageOCSPSigning = "OCSP Signing"
    ExtKeyUsageMicrosoftServerGatedCrypto = "Microsoft Server Gated Crypto"
    ExtKeyUsageNetscapeServerGatedCrypto = "Netscape Server Gated Crypto"
    ExtKeyUsageMicrosoftCommercialCodeSigning = "Microsoft Commercial Code Signing"
    ExtKeyUsageMicrosoftKernelCodeSigning = "Microsoft Kernel Code Signing"
    
@dataclass
class TLSCertificate(Asset):
    """TLSCertificate represents a TLS Certificate asset."""
    version:                  str
    serial_number:            str
    subject_common_name:      str
    issuer_common_name:       str
    not_before:               str
    not_after:                str
    key_usage:                List[TLSKeyUsageType]
    ext_key_usage:            List[TLSExtKeyUsageType]
    signature_algorithm:      str
    public_key_algorithm:     str
    is_ca:                    bool
    crl_distribution_points:  List[str]
    subject_key_id:           str
    authority_key_id:         str

    @property
    def key(self) -> str:
        return self.serial_number

    @property
    def asset_type(self) -> AssetType:
        return AssetType.TLSCertificate
