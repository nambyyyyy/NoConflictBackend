from backend.core.interfaces.password_interface import PasswordValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class DjangoPasswordValidator(PasswordValidator):
    
    def validate(self, plain_password: str) -> None:
        try:
            validate_password(plain_password)
        except DjangoValidationError as e:
            raise ValueError(f"Слабый пароль: {', '.join(e.messages)}")