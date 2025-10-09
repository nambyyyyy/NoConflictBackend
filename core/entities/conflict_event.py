from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class ConflictEvent:
    id: UUID
    conflict_id: UUID
    created_at: datetime
    initiator: Optional[dict]
    event_type: str
    item_id: Optional[UUID] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    
