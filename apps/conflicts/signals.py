from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.conflicts.models import ConflictItemModel

@receiver(post_save, sender=ConflictItemModel)
def update_conflict_progress(sender, instance, **kwargs):
    # instance — это сохранённый ConflictItem
    if instance.conflict:  # Проверяем, есть ли связанный conflict
        instance.conflict.update_progress()  # Вызываем метод из модели Conflict