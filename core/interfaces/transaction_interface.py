from abc import ABC, abstractmethod
from typing import Callable


class TransactionManager(ABC):
    
    @abstractmethod
    def on_commit(self, func: Callable[[], None]) -> None:
        """Выполнить функцию после успешного коммита транзакции"""
        pass