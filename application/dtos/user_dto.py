from dataclasses import dataclass
from uuid import UUID

@dataclass
class UserDTO:
    """DTO для передачи данных о пользователе"""
    id: UUID
    email: str
    username: str
    email_confirmed: bool