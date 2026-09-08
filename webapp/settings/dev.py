import os
from .base import *  # noqa

DEBUG = True
SECRET_KEY = "dev-only-not-for-prod"
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REDIS_URL = os.environ.get("REDIS_URL")
CACHES = (
    {"default": {"BACKEND": "django_redis.cache.RedisCache", "LOCATION": REDIS_URL}}
    if REDIS_URL
    else {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)