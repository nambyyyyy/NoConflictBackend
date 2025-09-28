from dataclasses import dataclass
from typing import Optional, Any
from uuid import UUID


@dataclass
class ConflictEvent:
    id: UUID
    conflict_id: UUID
    initiator_id: Optional[UUID]
    event_type: str
    details: Optional[dict[str, Any]] = None 
    
    
