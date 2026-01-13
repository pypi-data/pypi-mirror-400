from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.database)
def settings_check(app_configs, **kwargs):
    errors = []
    from .router import ForgejoRouter

    routers = getattr(settings, "DATABASE_ROUTERS", [])
    if f"{ForgejoRouter.__module__}.{ForgejoRouter.__name__}" not in routers:
        errors.append(
            Error(
                "Missing database router",
                obj=settings,
                hint="Will be unable to route to correct database",
            )
        )

    databases = getattr(settings, "DATABASES", {})
    if __package__ not in databases:
        errors.append(
            Error(
                f"Missing database config for '{__package__}'",
                obj=settings,
                hint="Unable to connect to database",
            )
        )

    return errors
