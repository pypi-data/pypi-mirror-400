from enum import Enum
from oam.asset import Asset
from oam.asset import AssetType
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

class IdentifierType(str, Enum):
    AccountNumber = "account"     # Account number
    ARINHandle = "arin"           # American Registry for Internet Numbers (ARIN) handle
    ASINNumber = "asin"           # Amazon Standard Identification Number
    BankIDCode = "bic"            # Bank Identifier Code
    DUNSNumer = "duns"            # Data Universal Numbering System, Dun & Bradstreet (D&B) assigns this number
    EAN8 = "ean_8"                # International Article Number (EAN) 8-digit
    EAN13 = "ean_13"              # International Article Number (EAN) 13-digit
    EmailAddress = "email"        # Email address
    EmployerIDNumber = "ein"      # Employer Identification Number
    GlobalLocNumber = "gln"       # Global Location Number
    GlobalTradeItemNumber = "gtin" # Global Trade Item Number
    GovIssuedIDNumber = "gov_id"  # Government issued identification number for individuals
    IBANCode = "iban"             # International Bank Account Number
    ICANNAuthCode = "icann_auth"  # Auth Code, Internet Corporation for Assigned Names and Numbers
    ICANNEPPCode = "icann_epp"    # Extensible Provisioning Protocol (EPP) status code, ICANN
    ISBN = "isbn"                 # International Standard Book Number
    ISICCode = "isic"             # International Standard Industrial Classification
    LegalName = "legal_name"      # Legal name
    LEICode = "lei"               # Legal Entity Identifier, Global Legal Entity Identifier Foundation assigns this number
    MarketIDCode = "mic"          # Market Identifier Code, International Organization for Standardization (ISO) 10383 standard
    ModelNumber = "model"         # Model number
    MPN = "mpn"                   # Manufacturer Part Number
    NAICSCode = "naics"          # North American Industry Classification System
    NSNCode = "nsn"               # NATO Stock Number
    OECDCode = "oecd"             # Organization for Economic Co-operation and Development
    OpenCorpID = "ocid"           # OpenCorporates ID, identifier for a corporation in the OpenCorporates database
    OrganizationName = "org_name"  # Organization name
    SerialNumber = "serial"        # Serial number
    SICCode = "sic"                # Standard Industrial Classification
    SPGlobalCompanyID = "spglobal" # S&P Global Company ID, S&P Global Market Intelligence
    SWIFTCode = "swift"            # Society for Worldwide Interbank Financial Telecommunication
    TaxIDNumber = "tin"            # Taxpayer Identification Number
    TickerSymbol = "ticker"        # Stock ticker symbol
    UPCNumberA = "upc_a"           # Universal Product Code (UPC) Version A
    UPCNumberE = "upc_e"           # Universal Product Code (UPC) Version E
    VersionNumber = "version"      # Version number

@dataclass
class Identifier(Asset):
    """Identifier identifies something that's a member of a system or
    organization that issues ID numbers or codes.
    
    Should support relationships for the following:
    - Registration agency (e.g., ContactRecord)
    - Issuing authority (e.g., ContactRecord)
    - Issuing agent (e.g., ContactRecord)
    """
    unique_id:       str
    id:              str
    type:            IdentifierType = field(metadata={"json":"id_type"})
    creation_date:   Optional[str] = None
    update_date:     Optional[str] = None
    expiration_date: Optional[str] = None
    status:          Optional[str] = None

    @property
    def key(self) -> str:
        return self.unique_id

    @property
    def asset_type(self) -> AssetType:
        return AssetType.Identifier
