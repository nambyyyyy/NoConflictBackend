import uuid
import os
from uuid import UUID


class FilenameGenerator:
    def generate(self, original_name: str, user_id: UUID) -> str:
        ext = os.path.splitext(original_name)[1].lower()
        if not ext:
            ext = ".jpg"
        return f"{user_id}_{uuid.uuid4().hex}{ext}"