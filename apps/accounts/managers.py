from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class CustomUserManager(BaseUserManager):    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        
        username = extra_fields.get("username")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email).strip().lower()
        extra_fields["username"] = username.strip().lower()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    # def create_superuser(self, **extra_fields):      
    #     extra_fields.setdefault("is_staff", True)
    #     extra_fields.setdefault("is_superuser", True)  
        
    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True')
            
    #     return self.create_user(**extra_fields)

    # def create_staffuser(self, **extra_fields):      
    #     extra_fields.setdefault("is_staff", True)
    #     extra_fields.setdefault("is_superuser", False)
        
    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True')
        
    #     return self.create_user(**extra_fields)
