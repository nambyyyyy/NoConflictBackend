from dataclasses import dataclass
from uuid import UUID



@dataclass
class OptionChoice:
    id: UUID
    value: str
    is_predefined: bool = False