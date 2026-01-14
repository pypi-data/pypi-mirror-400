from dataclasses import dataclass
from datetime import datetime
from oam import Asset
from typing import Optional

@dataclass
class Entity:
    id:         Optional[str]      = None
    asset:      Optional[Asset]    = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def etype(self) -> Optional[str]:
        if not self.asset:
            return None
        return self.asset.asset_type.value
    
    def to_dict(self) -> dict:
        if self.id is None or \
           self.created_at is None or \
           self.updated_at is None or \
           self.asset is None:
            raise Exception("malformed entity")
        
        return {
            "entity_id":  self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "etype":      self.etype,
            **self.asset.to_dict()
        }

