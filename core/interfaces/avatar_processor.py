from abc import ABC, abstractmethod
from uuid import UUID

class AvatarProcessor(ABC):

    @abstractmethod
    def process_avatar(self, file: object, user_id: UUID) -> str:
        """Принимает файл и возвращает имя сохранённого файла"""
        pass