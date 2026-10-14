from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = [
    h.strip()
    for h in config("ALLOWED_HOSTS", default="127.0.0.1,localhost,.trycloudflare.com").split(",")
    if h.strip()
]

# --- HTTPS / transport xavfsizligi ---
# Lokal http://localhost:8000 orqali to'g'ridan-to'g'ri sinash kerak bo'lsa, .env ga
# SECURE_SSL_REDIRECT=False yozing. Tunnel (https) orqali ishlaganda True qoldiring.
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # frontend JS CSRF tokenini o'qishi kerak bo'lsa False qoladi
# Tunnel / reverse proxy orqasida Django https ekanini bilishi uchun:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# --- HSTS ---
# Tunnel manzillari o'zgarib turgani uchun sinov davrida o'chiq (0).
# Haqiqiy domen bilan ishga tushirganda .env ga SECURE_HSTS_SECONDS=2592000 (30 kun) yozing.
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False

# --- Qo'shimcha browser-darajasidagi himoya ---
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# --- CSRF: ishonchli originlar ---
CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default="https://*.trycloudflare.com",
    ).split(",")
    if origin.strip()
]

# --- CORS ---
# CORS_ALLOWED_ORIGINS va CORS_ALLOWED_ORIGIN_REGEXES base.py dan olinadi.
CORS_ALLOW_ALL_ORIGINS = False

# --- Cookie umri ---
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 kun

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
    raise RuntimeError("ALLOWED_HOSTS bo'sh — .env fayliga real domeningizni yozing.")