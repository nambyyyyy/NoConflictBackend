from django.core.files.uploadedfile import UploadedFile


class AvatarValidator:
    allowed_extensions = {".jpg", ".jpeg", ".png"}

    def validate(self, file: UploadedFile) -> None:
        ext = file.name.lower().rsplit('.', 1)[-1]
        if f".{ext}" not in self.allowed_extensions:
            raise ValueError("Неподдерживаемый формат аватара")