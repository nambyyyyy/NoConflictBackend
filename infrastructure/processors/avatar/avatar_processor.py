import os
from uuid import UUID
from django.core.files.uploadedfile import UploadedFile
from backend.core.interfaces.avatar_processor import AvatarProcessor
from infrastructure.processors.avatar.avatar_validator import AvatarValidator
from infrastructure.processors.avatar.filename_generator import FilenameGenerator
from infrastructure.processors.avatar.image_processor import ImageProcessor
from infrastructure.processors.avatar.image_saver import ImageSaver


class DjangoAvatarProcessor(AvatarProcessor):
    def __init__(
        self,
        validator: AvatarValidator,
        generator: FilenameGenerator,
        processor: ImageProcessor,
        saver: ImageSaver,
        upload_dir: str = "avatars",
    ):
        self.validator = validator
        self.generator = generator
        self.processor = processor
        self.saver = saver
        self.upload_dir = upload_dir

    def process_avatar(self, file: UploadedFile, user_id: UUID) -> str:
        self.validator.validate(file)
        filename = self.generator.generate(file.name, user_id)
        filepath = os.path.join(self.upload_dir, filename)
        processed_img = self.processor.process(file)
        self.saver.save(processed_img, filepath)
        return filename