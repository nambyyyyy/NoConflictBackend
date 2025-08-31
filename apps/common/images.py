from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import uuid

TARGET_SIZE = (512, 512)   # итоговые габариты
TARGET_FORMAT = "WEBP"     # единый формат хранения
QUALITY = 85               # компрессия

def process_avatar(uploaded_file, user_id: int):
    uploaded_file.seek(0)
    img = Image.open(uploaded_file)

    # Правильная ориентация и удаление EXIF
    img = ImageOps.exif_transpose(img)

    # Конвертируем в RGB
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    img.thumbnail(TARGET_SIZE, Image.LANCZOS)

    # Сохраняем в буфер
    buf = BytesIO()
    save_kwargs = {"format": TARGET_FORMAT, "quality": QUALITY}
    img.save(buf, **save_kwargs)
    buf.seek(0)

    # Генерируем имя файла
    name = f"avatars/{user_id}-{uuid.uuid4().hex}.webp"
    content = ContentFile(buf.read())
    return name, content