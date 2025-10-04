from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class ConflictItem:
    id: UUID
    conflict_id: UUID
    title: str
    creator_choice_value: Optional[str] = None
    partner_choice_value: Optional[str] = None
    agreed_choice_value: Optional[str] = None
    is_agreed: bool = False

    def update_status(self):
        if self.creator_choice_value and self.partner_choice_value:
            # Если ответы совпадают - пункт согласован!
            if self.creator_choice_value == self.partner_choice_value:
                self.is_agreed = True
                self.agreed_choice_value = self.creator_choice_value
            else:
                # Ответы есть, но они разные. Пункт не согласован.
                self.is_agreed = False
                self.agreed_choice_value = None
        else:
            # Если хотя бы один из пользователей еще не ответил, пункт не может быть согласован.
            self.is_agreed = False
            self.agreed_choice_value = None

    def unlock(self):
        if not self.is_agreed:
            # Еще не согласован, подстраховка, просто скип.
            return

        self.is_agreed = False
        self.agreed_choice_value = None
