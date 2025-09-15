import os
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from core.storage.base import BaseStorage


class ImageSaver:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def save(self, image: Image.Image, filepath: str) -> str:
        buffer = BytesIO()
        image.save(buffer, format='JPEG', optimize=True, quality=85)
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            name=os.path.basename(filepath),
            content=buffer.getvalue(),
            content_type='image/jpeg',
        )
        return self.storage.save(uploaded_file, filepath)