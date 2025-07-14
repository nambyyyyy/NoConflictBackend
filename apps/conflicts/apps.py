from django.apps import AppConfig


class ConflictsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.conflicts'

    def ready(self):
        import apps.conflicts.signals
