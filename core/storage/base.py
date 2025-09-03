from abc import ABC, abstractmethod
from django.core.files.uploadedfile import UploadedFile

class BaseStorage(ABC):
    @abstractmethod
    def save(self, file: UploadedFile, filepath: str) -> str:
        """Сохраняет файл и возвращает путь"""
        pass
    
    @abstractmethod
    def delete(self, filepath: str) -> None:
        """Удаляет файл"""
        pass
    
    @abstractmethod
    def exists(self, filepath: str) -> bool:
        """Проверяет существование файла"""
        pass