# Unmanaged Django Models for Forgejo

![PyPI - License](https://img.shields.io/pypi/l/django-unmanaged-forgejo)
![PyPI - Version](https://img.shields.io/pypi/v/django-unmanaged-forgejo)

# Installation

```shell
uv add django-unmanaged-forgejo
# or
pip install django-unmanaged-forgejo
```

Configure `settings.py` with correct `INSTALLED_APPS`, `DATABASES`, and `DATABASE_ROUTER`

```python
# Add django_unmanaged_forgejo to installed apps
INSTALLED_APPS = [
    "myapp",
    "django_unmanaged_forgejo", # << Add to installed apps
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASES = {
    "default": env.db_url(
        var="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR}/db.sqlite3",
    ),
    # Configure additional database connection named 'django_unmanaged_forgejo'
    # for the module to use with the router
    "django_unmanaged_forgejo": env.db_url("DATABASE_FORGEJO", default=None),
}

# https://docs.djangoproject.com/en/6.0/ref/settings/#database-routers
# Add the provided router
DATABASE_ROUTERS = ["django_unmanaged_forgejo.router.ForgejoRouter"]
```
