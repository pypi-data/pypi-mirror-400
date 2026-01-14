from dataclasses import dataclass
from datetime import datetime
from oam import Property
from typing import Optional
from .edge import Edge

@dataclass
class EdgeTag:
    id:         Optional[str]      = None
    edge:       Optional[Edge]     = None
    prop:       Optional[Property] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def ttype(self) -> Optional[str]:
        if not self.prop:
            return None
        return self.prop.property_type.value
    
    def to_dict(self) -> dict:
        if self.id is None or \
           self.created_at is None or \
           self.updated_at is None or \
           self.edge is None or \
           self.prop is None:
            raise Exception("malformed edge tag")
        
        return {
            "tag_id":     self.id,
            "edge_id":    self.edge.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ttype":      self.ttype,
            **self.prop.to_dict()
        }
