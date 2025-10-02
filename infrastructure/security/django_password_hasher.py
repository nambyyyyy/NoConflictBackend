from django.contrib.auth.hashers import make_password, check_password
from core.interfaces.password_interface import PasswordHasher


class DjangoPasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return make_password(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return check_password(plain_password, hashed_password)