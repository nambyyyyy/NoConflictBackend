from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    username: str
    password_hash: str
    email_confirmed: bool = False
    is_active: bool = True
    is_deleted: bool = False
    created_at: Optional[datetime] = None