from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass
class ConflictItem:
    id: UUID
    conflict_id: UUID
    item_type: str
    available_option_ids: list[UUID] = field(default_factory=list)
    creator_choice_id: Optional[UUID] = None
    partner_choice_id: Optional[UUID] = None
    agreed_choice_id: Optional[UUID] = None
    is_agreed: bool = False

    def update_status(self):
        if self.creator_choice_id and self.partner_choice_id:
            # Если ответы совпадают - пункт согласован!
            if self.creator_choice_id == self.partner_choice_id:
                self.is_agreed = True
                self.agreed_choice_id = self.creator_choice_id
            else:
                # Ответы есть, но они разные. Пункт не согласован.
                self.is_agreed = False
                self.agreed_choice_id = None
        else:
            # Если хотя бы один из пользователей еще не ответил, пункт не может быть согласован.
            self.is_agreed = False
            self.agreed_choice_id = None

    def unlock(self):
        if not self.is_agreed:
            # Еще не согласован, подстраховка, просто скип.
            return

        self.is_agreed = False
        self.agreed_choice_id = None
