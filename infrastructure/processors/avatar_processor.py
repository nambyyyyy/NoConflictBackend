# core/services/avatar_processor.py
import os
import uuid
from typing import Optional
from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from uuid import UUID
from infrastructure.validators.avatar_validator import AvatarValidator
from core.storage.base import BaseStorage


class AvatarProcessor:
    def __init__(
        self,
        storage: BaseStorage,
        validator: Optional[AvatarValidator] = None,
        upload_dir: str = "avatars"
    ):
        self.storage = storage
        self.validator = validator or AvatarValidator()
        self.upload_dir = upload_dir

    def process_avatar(self, avatar_file: UploadedFile, user_id: UUID) -> str:
        """Безопасная обработка и сохранение аватара"""
        # Валидация
        self.validator.validate(avatar_file)
        
        # Генерация уникального имени
        filename = self._generate_filename(avatar_file, user_id)
        filepath = os.path.join(self.upload_dir, filename)
        
        # Обработка изображения
        processed_image = self._process_image(avatar_file)
        
        # Сохранение через абстракцию хранилища
        final_path = self._save_processed_image(processed_image, filepath)
        
        return filename  # Возвращаем только имя файла

    def _generate_filename(self, file: UploadedFile, user_id: UUID) -> str:
        """Генерация безопасного имени файла"""
        extension = os.path.splitext(file.name)[1].lower()
        if extension not in self.validator.allowed_extensions:
            extension = '.jpg'  # Дефолтное расширение
        return f"{user_id}_{uuid.uuid4().hex}{extension}"

    def _process_image(self, file: UploadedFile) -> Image.Image:
        """Обработка изображения: ресайз и оптимизация"""
        with Image.open(file) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
        
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)     
            return img

    def _save_processed_image(self, image: Image.Image, filepath: str) -> str:
        """Сохранение через BytesIO (без временных файлов)"""
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Сохраняем изображение в память
        buffer = BytesIO()
        image.save(buffer, format='JPEG', optimize=True, quality=85)
        buffer.seek(0)  # Перемещаемся в начало буфера
        
        # Создаем UploadedFile из памяти
        uploaded_file = SimpleUploadedFile(
            name=os.path.basename(filepath),
            content=buffer.getvalue(),
            content_type='image/jpeg'
        )
        
        # Сохраняем через абстракцию
        return self.storage.save(uploaded_file, filepath)