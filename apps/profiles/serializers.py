from rest_framework import serializers
from apps.profiles.models import Profile
from PIL import Image, UnidentifiedImageError
from io import BytesIO

MAX_AVATAR_MB = 2
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_WIDTH = 1024
MAX_HEIGHT = 1024


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'id',
            'user',
            'first_name',
            'last_name',
            'avatar',
            'location',
            'bio',
            'created_at',
            'updated_at',
        )
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        
    
    def validate_avatar(self, file):
        if file is None:
            return file
        
        max_bytes = MAX_AVATAR_MB * 1024 * 1024
        if file.size > max_bytes:
            raise serializers.ValidationError(f"Файл слишком большой (> {MAX_AVATAR_MB}MB)")
        
        pos = file.tell()
        try:
            img = Image.open(file)
            img.verify()  # проверка целостности
        except UnidentifiedImageError:
            raise serializers.ValidationError("Некорректный файл изображения")
        finally:
            file.seek(pos)
        
        img = Image.open(file)
        fmt = (img.format or "").upper()
        if fmt not in ALLOWED_FORMATS:
            raise serializers.ValidationError("Допустимые форматы: JPEG, PNG, WEBP")

        w, h = img.size
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            raise serializers.ValidationError(
                f"Слишком большие размеры ({w}x{h}). Максимум {MAX_WIDTH}x{MAX_HEIGHT}"
            )

        file.seek(0)
        return file