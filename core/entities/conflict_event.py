from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class ConflictEvent:
    id: UUID
    conflict_id: UUID
    created_at: datetime
    event_type: str
    initiator: Optional[dict] = None
    item_id: Optional[UUID] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    
