from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from datetime import datetime



# @dataclass
# class ConflictItemDTO:
#     id: UUID
#     title: str
#     creator_choice_value: Optional[str]
#     partner_choice_value: Optional[str]
#     agreed_choice_value: Optional[str]
#     is_agreed: bool


# @dataclass
# class ConflictEventDTO:
#     id: UUID
#     event_type: str
#     created_at: datetime
#     initiator_id: Optional[UUID]
#     initiator_name: Optional[str] = None
#     initiator_avatar_url: Optional[str] = None
#     details: Optional[dict[str, Any]] = None


@dataclass
class ConflictShortDTO:
    id: UUID
    title: str
    status: str
    progress: float


@dataclass
class ConflictDetailDTO:
    id: UUID
    creator_id: UUID
    partner_id: Optional[UUID]
    title: Optional[str]
    status: str
    slug: str
    progress: float
    resolved_at: Optional[datetime]
    truce_status: str
    truce_initiator_id: Optional[UUID]
    items: list[dict]
    events: list[dict]

