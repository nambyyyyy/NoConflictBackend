from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class ConflictEvent:
    conflict_id: UUID
    event_type: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    initiator_id: Optional[UUID] = None
    initiator_username: Optional[str] = None
    item_id: Optional[UUID] = None
    item_title: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    
