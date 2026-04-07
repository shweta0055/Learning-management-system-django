from django.apps import AppConfig


class LmsBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms_backend'

    def ready(self):
        import lms_backend.signals  # noqa: F401
