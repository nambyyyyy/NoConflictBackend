from abc import ABC, abstractmethod


class LinkDecoder(ABC):
    
    @abstractmethod
    def decode(self, encoded: str) -> str:
        """
        Декодирует строку из ссылки (например, id юзера).
        Кидает ValueError при ошибке.
        """
        pass