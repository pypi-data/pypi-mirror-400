from __future__ import annotations
from abc import ABC
from json import dumps
from dataclasses import fields
from dataclasses import dataclass
from dataclasses import is_dataclass
from typing import Any

@dataclass
class OAMObject(ABC):
    def to_dict(self) -> dict:
        d = {}
        for field in fields(self):
            json_name = field.metadata["json"] if "json" in field.metadata else field.name
            json_value = self.__dict__[field.name]
            if json_value is not None:
                d[json_name] = json_value
        return d
    
    def to_json(self) -> str:
        return dumps(self.to_dict())        
