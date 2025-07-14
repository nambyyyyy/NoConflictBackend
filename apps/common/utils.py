from rest_framework.exceptions import ValidationError

def set_dict_attr(obj, data):
    for attr, value in data.items():
        setattr(obj, attr, value)
    return obj


def set_profile_and_user(user, profile, validated_data):
    for attr, value in validated_data.items():
        if not (hasattr(profile, attr) or hasattr(user, attr)):
            raise ValidationError(
                f"Поле '{attr}' отсутствует в модели User или Profile."
            )
        if hasattr(profile, attr):
            setattr(profile, attr, value)
        if hasattr(user, attr):
            setattr(user, attr, value)
    profile.save()
    user.save()
