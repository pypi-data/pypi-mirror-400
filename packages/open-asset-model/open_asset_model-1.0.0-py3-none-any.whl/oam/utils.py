from __future__ import annotations
from dataclasses import fields
from dataclasses import is_dataclass
import inspect
from typing import cast
from typing import Type, TypeVar, Mapping, Any
from oam.oam_object import OAMObject
import oam
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import DataclassInstance

def _get_oam_obj_by_name(name: str) -> Type[OAMObject]:
    for [_name, cls] in inspect.getmembers(oam, inspect.isclass):
        if _name == name:
            return cast(type[OAMObject], cls)

    raise Exception("unsupported oam object")

def get_property_by_type(type: oam.PropertyType) -> Type[oam.Property]:
    if type not in oam.PropertyList:
        raise Exception("unsupported relation type")
    return cast(Type[oam.Property], _get_oam_obj_by_name(type.value))

def get_relation_by_type(type: oam.RelationType) -> Type[oam.Relation]:
    if type not in oam.RelationList:
        raise Exception("unsupported relation type")
    return cast(Type[oam.Relation], _get_oam_obj_by_name(type.value))

def get_asset_by_type(type: oam.AssetType) -> Type[oam.Asset]:
    if type not in oam.AssetList:
        raise Exception("unsupported asset type")
    return cast(Type[oam.Asset], _get_oam_obj_by_name(type.value))

def describe_oam_object(o: Type[OAMObject]) -> list:
    d = []
    for field in fields(o):
        json_name = field.metadata["json"] if "json" in field.metadata else field.name
        d.append(json_name)
            
    return d

T = TypeVar("T")

def make_oam_object_from_dict(o: Type[T], d: Mapping[str, Any]) -> T:
    real_d = {}
    o_fields = fields(cast(Any, o))
    for key, value in d.items():
        for field in o_fields:
            if ("json" in field.metadata and field.metadata["json"] == key) \
               or field.name == key:
                real_d[field.name] = value
                break
        
    return o(**real_d)
