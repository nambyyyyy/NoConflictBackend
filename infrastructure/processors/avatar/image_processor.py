from PIL import Image
from django.core.files.uploadedfile import UploadedFile


class ImageProcessor:
    def process(self, file: UploadedFile) -> Image.Image:
        with Image.open(file) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            return img