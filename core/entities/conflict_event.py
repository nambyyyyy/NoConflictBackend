from dataclasses import dataclass
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


@dataclass
class ConflictEvent:
    id: UUID
    conflict_id: UUID
    created_at: datetime
    initiator_id: Optional[UUID]
    event_type: str
    details: Optional[dict[str, Any]] = None 
    
    
