from core.interfaces.profile_interface import ProfileRepository
from core.interfaces.avatar_processor import AvatarProcessor
from uuid import UUID
from typing import Optional
from core.entities.profile import Profile
from application.dtos.profile_dto import ProfileDTO 


class ProfileService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        avatar_processor: AvatarProcessor,
        media_base_url: str,
    ):
        self.media_base_url = media_base_url
        self.profile_repo = profile_repository
        self.avatar_processor = avatar_processor

    def update_profile(
        self,
        user_id: UUID,
        profile_data: dict,
        avatar_file: Optional[object] = None,
    ) -> ProfileDTO:

        profile_entity: Optional[Profile] = self.profile_repo.get_by_user_id(user_id)

        if profile_entity is None:
            raise ValueError("Profile not found")

        if avatar_file is not None:
            profile_entity.avatar_filename = self.avatar_processor.process_avatar(
                avatar_file, user_id
            )

        for field_name, field_value in profile_data.items():
            setattr(profile_entity, field_name, field_value)

        profile_entity: Optional[Profile] = self.profile_repo.update(profile_entity)
        if profile_entity is None:
            raise ValueError("Profile not found")
        
        return self._to_dto(profile_entity)

    def _get_avatar_url(self, filename: Optional[str]) -> Optional[str]:
        return f"{self.media_base_url}avatars/{filename}" if filename else None

    def _get_fullname(self, first_name: Optional[str], last_name: Optional[str]):
        return (
            f"{first_name} {last_name}".strip() if (first_name and last_name) else None
        )

    def _to_dto(self, profile_entity: Profile) -> ProfileDTO:
        avatar_url: Optional[str] = self._get_avatar_url(profile_entity.avatar_filename)
        full_name: Optional[str] = self._get_fullname(
            profile_entity.first_name, profile_entity.last_name
        )

        return ProfileDTO(
            id=profile_entity.id,
            user_id=profile_entity.user_id,
            first_name=profile_entity.first_name,
            last_name=profile_entity.last_name,
            full_name=full_name,
            gender=profile_entity.gender,
            location=profile_entity.location,
            bio=profile_entity.bio,
            avatar_url=avatar_url,
            created_at=profile_entity.created_at,
            updated_at=profile_entity.updated_at,
        )
