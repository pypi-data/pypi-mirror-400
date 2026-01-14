from dataclasses import dataclass
from enum import Enum
from typing import Optional
from oam.asset import Asset
from oam.asset import AssetType
from phonenumbers import parse
from phonenumbers import format_number
from phonenumbers import PhoneNumberFormat
from phonenumbers.phonenumberutil import region_code_for_country_code

class PhoneType(str, Enum):
    Regular = "phone"
    Fax     = "fax"
    Mobile  = "mobile"

@dataclass
class Phone(Asset):
    """This struct represents the phone number, whether it is fax,
    mobile, or home number linked to the possible asset."""
    raw:            str
    e164:           Optional[str] = None  # E.164 format
    type:           Optional[str] = None
    country_abbrev: Optional[str] = None
    country_code:   Optional[int] = None
    ext:            Optional[str] = None

    @property
    def key(self) -> str:
        return self.raw

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Phone
    
    @staticmethod
    def from_text(phone: str, region: Optional[str] = None) -> 'Phone':
        o = parse(phone, region)
        e164 = format_number(o, PhoneNumberFormat.E164)
        if not region and o.country_code:
            region = region_code_for_country_code(o.country_code)
            
        return Phone(
            raw = phone,
            e164 = e164,
            country_code = o.country_code,
            country_abbrev = region,
            ext = o.extension or None
        )
