from core.interfaces.profile_repository import ProfileRepository
from apps.profiles.models import ProfileModel
from core.entities.profile import Profile
from typing import Optional
from uuid import UUID
from datetime import datetime


class DjangoProfielRepository(ProfileRepository):

    def get_by_id(self, profile_id: UUID) -> Optional[Profile]:
        """Найти профиль по ID"""
        try:
            profile = ProfileModel.objects.get(id=profile_id)
            return self._to_entity(django_profile=profile)
        except ProfileModel.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Найти профиль по ID пользователя (основной метод!)"""
        try:
            profile = ProfileModel.objects.get(user_id=user_id)
            return self._to_entity(django_profile=profile)
        except ProfileModel.DoesNotExist:
            return None

    def update(self, profile: Profile) -> Optional[Profile]:
        """Обновление существующего профиля"""
        try:
            django_profile = ProfileModel.objects.get(id=profile.id)
        except ProfileModel.DoesNotExist:
            return None

        field_values: dict[str, str | datetime] = profile.get_django_field_values()

        for field_name, value in field_values.items():
            setattr(django_profile, field_name, value)

        django_profile.save()
        return self._to_entity(django_profile)

    def _to_entity(self, django_profile: ProfileModel) -> Profile:
        """Приватный метод конвертации"""
        avatar_filename = None      
        if django_profile.avatar_filename:
            avatar_filename = (
                django_profile.avatar_filename.name 
                if hasattr(django_profile.avatar_filename, 'name')
                else str(django_profile.avatar_filename)
            )
            
        return Profile(
            id=django_profile.id,
            user_id=django_profile.user.id,
            first_name=django_profile.first_name,
            last_name=django_profile.last_name,
            gender=django_profile.gender,
            avatar_filename=avatar_filename,
            location=django_profile.location,
            bio=django_profile.bio,
            created_at=django_profile.created_at,
            updated_at=django_profile.updated_at,
        )
