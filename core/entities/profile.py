from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from django.core.files import File
from django.utils import timezone


@dataclass
class Profile:
    id: UUID
    user_id: UUID
    avatar_filename: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_django_field_values(self) -> dict:
        """Получить значения полей для Django ORM"""
        return {
            'first_name': self.first_name or "",
            'last_name': self.last_name or "",
            'location': self.location or "",
            'bio': self.bio or "",
            'gender': self.gender,
            'avatar_filename': self.avatar_filename,
            'updated_at': self.updated_at or timezone.now(),
        }
