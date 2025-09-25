from abc import ABC, abstractmethod

class TokenRepository(ABC):
    @abstractmethod
    def make_token(self, user_entity) -> str:
        pass
    
    @abstractmethod
    def check_token(self, user_entity, token: str) -> bool:
        pass


class JWTRepository(ABC):
    @abstractmethod
    def create_access_token(self, user) -> str:
        pass
    
    @abstractmethod
    def create_refresh_token(self, user) -> str:
        pass