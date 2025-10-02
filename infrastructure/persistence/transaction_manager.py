from django.db import transaction
from core.interfaces.transaction_interface import TransactionManager
from typing import Callable


class DjangoTransactionManager(TransactionManager):
    
    def on_commit(self, func: Callable[[], None]) -> None:
        transaction.on_commit(func)