from django.apps import AppConfig


class DjangoUnmanagedForgejoConfig(AppConfig):
    name = __package__

    def ready(self):
        from . import checks  # NOQA:F401
