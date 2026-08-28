from django.apps import AppConfig

# pylint: disable=import-outside-toplevel,unused-import


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        from apps.core import checks
