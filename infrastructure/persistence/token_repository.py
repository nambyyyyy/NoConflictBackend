from core.interfaces.token_interface import TokenRepository, JWTRepository
from apps.accounts.models import UserModel
from django.contrib.auth.tokens import default_token_generator
from core.entities.user import User
from datetime import timedelta
from django.utils import timezone
from uuid import uuid4
import jwt


class DjangoTokenRepository(TokenRepository):
    def make_token(self, user_entity: User) -> str:
        try:
            django_user = UserModel.objects.get(id=user_entity.id)
            return default_token_generator.make_token(django_user)
        except UserModel.DoesNotExist:
            raise ValueError("User not found in database")
    
    def check_token(self, user_entity: User, token: str) -> bool:
        try:
            django_user = UserModel.objects.get(id=user_entity.id)
            return default_token_generator.check_token(django_user, token)
        except UserModel.DoesNotExist:
            raise ValueError("User not found in database")


class DjangoJWTRepository(JWTRepository):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def create_access_token(self, user: User) -> str:
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': timezone.now() + timedelta(minutes=15),
            'token_type': 'access',
            'jti': str(uuid4())
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User) -> str:
        payload = {
            'user_id': str(user.id),
            'exp': timezone.now() + timedelta(days=7),
            'token_type': 'refresh',
            'jti': str(uuid4())
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)