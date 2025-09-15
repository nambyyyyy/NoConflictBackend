from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from datetime import datetime

@dataclass
class ProfileDTO:
    """DTO для отдачи данных профиля на клиент"""
    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None  # ← Вычисляемое поле!
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None  # ← URL, а не filename!
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None