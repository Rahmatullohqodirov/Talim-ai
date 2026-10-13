from .base import *
from decouple import config

DEBUG = False

# --- HTTPS / transport xavfsizligi ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
# Vercel / reverse proxy orqasida Django https ekanini bilishi uchun:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# --- HSTS ---
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- Qo'shimcha browser-darajasidagi himoya ---
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

ALLOWED_HOSTS = [
    h.strip()
    for h in config("ALLOWED_HOSTS", default="").split(",")
    if h.strip()
]

# --- CSRF: frontend va backend domenlariga ishonch ---
# .env da vergul bilan ajratib yozing. Doimiy domenni albatta qo'shing.
CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default=(
            "https://talim-ai-pi.vercel.app,"
            "https://talim-ai-backend.vercel.app"
        ),
    ).split(",")
    if origin.strip()
]

# --- CORS: faqat aniq domenlar (preview URL'lar base.py dagi regex orqali ruxsat etiladi) ---
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in config(
        "CORS_ALLOWED_ORIGINS",
        default="https://talim-ai-pi.vercel.app",
    ).split(",")
    if origin.strip()
]

# --- Cookie umri ---
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# --- Log ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.2,
        send_default_pii=False,
    )

if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-me":
    raise RuntimeError(
        "SECRET_KEY production uchun sozlanmagan! .env fayliga tasodifiy, uzun SECRET_KEY qo'ying "
        "(masalan: python -c \"import secrets; print(secrets.token_urlsafe(50))\")."
    )
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS bo'sh — .env fayliga real domeningizni yozing (masalan: talim-ai-backend.vercel.app).")

# Vercel serverless'da Redis bo'lmasa, oddiy xotira keshi
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "talim-production-cache",
    }
}