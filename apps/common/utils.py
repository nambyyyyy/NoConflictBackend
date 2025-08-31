from rest_framework.exceptions import ValidationError
from apps.common.images import process_avatar
from django.db import transaction


SENTINEL = object()
ALLOWED_PROFILE_FIELDS = {"first_name", "last_name", "location", "bio", "gender"}
DEFAULT_AVATAR_NAME = "avatars/default.jpg"


def set_dict_attr(obj, data):
    for attr, value in data.items():
        setattr(obj, attr, value)
    return obj


def set_profile_and_user(user, profile, validated_data):
    avatar = validated_data.pop("avatar", SENTINEL)

    changed = set()

    for attr, value in validated_data.items():
        if attr not in ALLOWED_PROFILE_FIELDS:
            raise ValidationError(f"Поле '{attr}' недоступно для изменения.")
        setattr(profile, attr, value)
        changed.add(attr)

    with transaction.atomic():
        if avatar is not SENTINEL:
            old_name = profile.avatar.name if getattr(profile, "avatar", None) else None

            if avatar is None:
                # Явная очистка: удаляем старый файл (кроме дефолтного) и ставим None
                if old_name and old_name != DEFAULT_AVATAR_NAME:
                    try:
                        profile.avatar.storage.delete(old_name)
                    except Exception:
                        pass
                profile.avatar.name = DEFAULT_AVATAR_NAME
                changed.add("avatar")

            else:
                # Обрабатываем и сохраняем новый
                try:
                    new_name, content = process_avatar(avatar, user.id)
                except Exception:
                    raise ValidationError("Не удалось обработать изображение.")

                profile.avatar.save(new_name, content, save=False)
                changed.add("avatar")

                if (
                    old_name
                    and old_name not in (None, DEFAULT_AVATAR_NAME)
                    and old_name != profile.avatar.name
                ):
                    try:
                        profile.avatar.storage.delete(old_name)
                    except Exception:
                        pass

        if changed:
            profile.save(update_fields=list(changed))
