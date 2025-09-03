import os
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from typing import Optional


class AvatarValidator:
    def __init__(
        self,
        max_size_mb: int = 5,
        allowed_extensions: Optional[set] = None,
        allowed_mime_types: Optional[set] = None,
        max_dimensions: tuple[int, int] = (2000, 2000)
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_extensions = allowed_extensions or {'.jpg', '.jpeg', '.png', '.webp'}
        self.allowed_mime_types = allowed_mime_types or {
            'image/jpeg', 'image/png', 'image/webp'
        }
        self.max_dimensions = max_dimensions

    def validate(self, file: UploadedFile) -> None:
        """Полная валидация файла"""
        self._validate_size(file)
        self._validate_extension(file)
        self._validate_mime_type(file)
        self._validate_image_content(file)

    def _validate_size(self, file: UploadedFile) -> None:
        if file.size > self.max_size_bytes:
            raise ValidationError(
                f"Файл слишком большой. Максимум {self.max_size_bytes//1024//1024}MB"
            )

    def _validate_extension(self, file: UploadedFile) -> None:
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Недопустимое расширение. Разрешены: {', '.join(self.allowed_extensions)}"
            )

    def _validate_mime_type(self, file: UploadedFile) -> None:
        if hasattr(file, 'content_type') and file.content_type:
            if file.content_type not in self.allowed_mime_types:
                raise ValidationError("Недопустимый тип файла")

    def _validate_image_content(self, file: UploadedFile) -> None:
        """Проверяет, что файл действительно является изображением"""
        try:
            with Image.open(file) as img:
                img.verify()  # Проверяет целостность изображения
                
                # Проверяем размеры
                if img.width > self.max_dimensions[0] or img.height > self.max_dimensions[1]:
                    raise ValidationError(
                        f"Слишком большие размеры. Максимум {self.max_dimensions[0]}x{self.max_dimensions[1]}px"
                    )
                
        except Exception as e:
            raise ValidationError("Файл не является корректным изображением") from e