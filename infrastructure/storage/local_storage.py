from django.core.files.storage import FileSystemStorage
from core.storage.base import BaseStorage
from django.core.files.uploadedfile import UploadedFile


class LocalStorage(BaseStorage):
    def __init__(self, location: str = "media"):
        self.storage = FileSystemStorage(location=location)
    
    def save(self, file: UploadedFile, filepath: str) -> str:
        return self.storage.save(filepath, file)
    
    def delete(self, filepath: str) -> None:
        if self.storage.exists(filepath):
            self.storage.delete(filepath)
    
    def exists(self, filepath: str) -> bool:
        return self.storage.exists(filepath)