from core.interfaces.user_interface import UserRepository
from core.entities.user import User
from apps.accounts.models import UserModel
from uuid import UUID
from typing import Optional


class DjangoUserRepository(UserRepository):
    """Реализация UserRepository через Django ORM"""

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            django_user = UserModel.objects.get(email=email)
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            django_user = UserModel.objects.get(username=username)
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            django_user = UserModel.objects.get(id=user_id)
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None
    
    def get_by_id_model(self, user_id: UUID) -> Optional[UserModel]:
        try:
            django_user = UserModel.objects.get(id=user_id)
            return django_user
        except UserModel.DoesNotExist:
            return None

    def get_many_id(self, user_ids: list[UUID]) -> Optional[list[User]]:
        try:
            django_users: dict[UUID, UserModel] = UserModel.objects.in_bulk(user_ids)
            return [self._to_entity(user) for user in django_users.values()]
        except Exception:
            return None

    def save(self, user: User) -> Optional[User]:
        # Создаем или обновляем
        django_user, created = UserModel.objects.get_or_create(
            id=user.id,
            defaults={
                "email": user.email,
                "username": user.username,
                "password": user.password_hash,
                "email_confirmed": user.email_confirmed,
                "is_active": user.is_active,
            },
        )
        # Если не created, значит обновляем существующего
        if not created:
            return self.update(user)

        return self._to_entity(django_user)

    def update(self, user: User) -> Optional[User]:
        """Обновление существующего пользователя"""
        try:
            django_user = UserModel.objects.get(id=user.id)
            django_user.email = user.email
            django_user.username = user.username
            django_user.password = user.password_hash
            django_user.email_confirmed = user.email_confirmed
            django_user.is_active = user.is_active

            django_user.save()
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None

    def delete(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            django_user.delete()  # Мягкое удаление
            return True
        except UserModel.DoesNotExist:
            return False

    def _to_entity(self, django_user: UserModel) -> User:
        """Приватный метод конвертации"""
        return User(
            id=django_user.id,
            email=django_user.email,
            username=django_user.username,
            password_hash=django_user.password,  # уже захеширован
            email_confirmed=django_user.email_confirmed,
            is_active=django_user.is_active,
            created_at=django_user.created_at,
        )
