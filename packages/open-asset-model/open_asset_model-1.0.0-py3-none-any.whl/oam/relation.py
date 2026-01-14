import json
from oam.oam_object import OAMObject
from abc import abstractmethod
from enum import Enum
from typing import List
from oam.asset import AssetType
from dataclasses import dataclass

class RelationType(str, Enum):
    BasicDNSRelation = "BasicDNSRelation"
    PortRelation = "PortRelation"
    PrefDNSRelation = "PrefDNSRelation"
    SimpleRelation = "SimpleRelation"
    SRVDNSRelation = "SRVDNSRelation"

class Relation(OAMObject):
    @property
    @abstractmethod
    def label(self) -> str:
        pass

    @property
    @abstractmethod
    def relation_type(self) -> RelationType:
        pass

RelationList = list(RelationType)

account_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "user": {RelationType.SimpleRelation: {AssetType.Person, AssetType.Organization}},
}

autnum_record_rels = {
    "whois_server": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "registrant": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "admin_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "abuse_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "technical_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "rdap_url": {RelationType.SimpleRelation: {AssetType.URL}},
}

autonomous_system_rels = {
    "announces": {RelationType.SimpleRelation: {AssetType.Netblock}},
    "registration": {RelationType.SimpleRelation: {AssetType.AutnumRecord}},
}

contact_record_rels = {
    "fqdn": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "person": {RelationType.SimpleRelation: {AssetType.Person}},
    "organization": {RelationType.SimpleRelation: {AssetType.Organization}},
    "location": {RelationType.SimpleRelation: {AssetType.Location}},
    "phone": {RelationType.SimpleRelation: {AssetType.Phone}},
    "url": {RelationType.SimpleRelation: {AssetType.URL}},
}

domain_record_rels = {
    "name_server": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "whois_server": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "registrar_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "registrant_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "admin_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "technical_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "billing_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
}

file_rels = {
    "url": {RelationType.SimpleRelation: {AssetType.URL}},
    "contains": {RelationType.SimpleRelation: {AssetType.ContactRecord, AssetType.URL}},
}

fqdn_rels = {
    "port": {RelationType.PortRelation: {AssetType.Service}},
    "dns_record": {
        RelationType.BasicDNSRelation: {AssetType.FQDN, AssetType.IPAddress},
        RelationType.PrefDNSRelation: {AssetType.FQDN},
        RelationType.SRVDNSRelation: {AssetType.FQDN},
    },
    "node": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "registration": {RelationType.SimpleRelation: {AssetType.DomainRecord}},
    "verified_for": {RelationType.SimpleRelation: {AssetType.Organization, AssetType.Service}},
}

funds_transfer_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "sender": {RelationType.SimpleRelation: {AssetType.Account}},
    "recipient": {RelationType.SimpleRelation: {AssetType.Account}},
    "third_party": {RelationType.SimpleRelation: {AssetType.Organization}},
}

identifier_rels = {
    "registration_agency": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "issuing_authority": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "issuing_agent": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
}

ip_rels = {
    "port": {RelationType.PortRelation: {AssetType.Service}},
    "ptr_record": {RelationType.SimpleRelation: {AssetType.FQDN}},
}

ipnet_record_rels = {
    "whois_server": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "registrant": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "admin_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "abuse_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "technical_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "rdap_url": {RelationType.SimpleRelation: {AssetType.URL}},
}

location_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
}

netblock_rels = {
    "contains": {RelationType.SimpleRelation: {AssetType.IPAddress}},
    "registration": {RelationType.SimpleRelation: {AssetType.IPNetRecord}},
}

org_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "legal_address": {RelationType.SimpleRelation: {AssetType.Location}},
    "hq_address": {RelationType.SimpleRelation: {AssetType.Location}},
    "location": {RelationType.SimpleRelation: {AssetType.Location}},
    "subsidiary": {RelationType.SimpleRelation: {AssetType.Organization}},
    "org_unit": {RelationType.SimpleRelation: {AssetType.Organization}},
    "account": {RelationType.SimpleRelation: {AssetType.Account}},
    "member": {RelationType.SimpleRelation: {AssetType.Person}},
    "website": {RelationType.SimpleRelation: {AssetType.URL}},
    "social_media_profile": {RelationType.SimpleRelation: {AssetType.URL}},
    "funding_source": {RelationType.SimpleRelation: {AssetType.Person, AssetType.Organization}},
}

person_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "address": {RelationType.SimpleRelation: {AssetType.Location}},
    "phone": {RelationType.SimpleRelation: {AssetType.Phone}},
    "account": {RelationType.SimpleRelation: {AssetType.Account}},
}

phone_rels = {
    "account": {RelationType.SimpleRelation: {AssetType.Account}},
    "contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
}

product_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "manufacturer": {RelationType.SimpleRelation: {AssetType.Organization}},
    "website": {RelationType.SimpleRelation: {AssetType.URL}},
    "release": {RelationType.SimpleRelation: {AssetType.ProductRelease}},
}

product_release_rels = {
    "id": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "website": {RelationType.SimpleRelation: {AssetType.URL}},
}

service_rels = {
    "provider": {RelationType.SimpleRelation: {AssetType.Organization}},
    "certificate": {RelationType.SimpleRelation: {AssetType.TLSCertificate}},
    "terms_of_service": {RelationType.SimpleRelation: {AssetType.File, AssetType.URL}},
    "product_used": {RelationType.SimpleRelation: {AssetType.Product, AssetType.ProductRelease}},
}

tlscert_rels = {
    "common_name": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "subject_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "issuer_contact": {RelationType.SimpleRelation: {AssetType.ContactRecord}},
    "san_dns_name": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "san_email_address": {RelationType.SimpleRelation: {AssetType.Identifier}},
    "san_ip_address": {RelationType.SimpleRelation: {AssetType.IPAddress}},
    "san_url": {RelationType.SimpleRelation: {AssetType.URL}},
    "issuing_certificate": {RelationType.SimpleRelation: {AssetType.TLSCertificate}},
    "issuing_certificate_url": {RelationType.SimpleRelation: {AssetType.URL}},
    "ocsp_server": {RelationType.SimpleRelation: {AssetType.URL}},
}

url_rels = {
    "domain": {RelationType.SimpleRelation: {AssetType.FQDN}},
    "ip_address": {RelationType.SimpleRelation: {AssetType.IPAddress}},
    "port": {RelationType.PortRelation: {AssetType.Service}},
    "file": {RelationType.SimpleRelation: {AssetType.File}},
}

def asset_type_relations(atype: AssetType) -> dict:
    match atype:
        case AssetType.Account:
            return account_rels
        case AssetType.AutnumRecord:
            return autnum_record_rels
        case AssetType.AutonomousSystem:
            return autonomous_system_rels
        case AssetType.ContactRecord:
            return contact_record_rels
        case AssetType.DomainRecord:
            return domain_record_rels
        case AssetType.File:
            return file_rels
        case AssetType.FQDN:
            return fqdn_rels
        case AssetType.FundsTransfer:
            return funds_transfer_rels
        case AssetType.Identifier:
            return identifier_rels
        case AssetType.IPAddress:
            return ip_rels
        case AssetType.IPNetRecord:
            return ipnet_record_rels
        case AssetType.Location:
            return location_rels
        case AssetType.Netblock:
            return netblock_rels
        case AssetType.Organization:
            return org_rels
        case AssetType.Person:
            return person_rels
        case AssetType.Phone:
            return phone_rels
        case AssetType.Product:
            return product_rels
        case AssetType.ProductRelease:
            return product_release_rels
        case AssetType.Service:
            return service_rels
        case AssetType.TLSCertificate:
            return tlscert_rels
        case AssetType.URL:
            return url_rels
        case _:
            return None

def get_asset_outgoing_relations(subject: AssetType) -> List[str] | None:
    """
    GetAssetOutgoingRelations returns the relation types allowed
    to be used when the subject is the asset type provided in the
    parameter.

    Providing an invalid subject causes a return value of nil.
    """
    relations = asset_type_relations(subject)
    if relations == None:
        return None

    return list(relations.keys())


def get_transform_asset_types(
        subject: AssetType,
        label: str,
        rtype: RelationType) -> List[AssetType] | None:
    """
    GetTransformAssetTypes returns the asset types allowed to be assigned
    when the subject is the asset type provided in the parameter, along
    with the provided label and RelationType.
    Providing an invalid subject causes a return value of nil."""
    relations = asset_type_relations(subject)
    if relations == None:
        return None

    label = label.lower()
    atypes: List[AssetType] = []
    for r, assets in relations.items():
        if r != label:
            continue
        
        for a in assets.values():
            atypes.extend(list(a))

    return atypes
        

def valid_relationship(
        src: AssetType,
        label: str,
        rtype: RelationType,
        dst: AssetType) -> bool:
    """
    ValidRelationship returns true if the relation is valid in the
    taxonomy when outgoing from the source asset type to the
    destination asset type.
    """
    atypes = get_transform_asset_types(src, label, rtype)
    if atypes == None:
        return False
    
    return dst in atypes
