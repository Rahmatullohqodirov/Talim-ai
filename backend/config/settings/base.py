from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me")
AUTH_USER_MODEL = "accounts.User"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Email (ro'yxatdan o'tishni tasdiqlash uchun) ---
EMAIL_HOST = config("EMAIL_HOST", default="")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@talim.uz")

# --- Google / Facebook orqali kirish (ixtiyoriy) ---
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
FACEBOOK_APP_ID = config("FACEBOOK_APP_ID", default="")
FACEBOOK_APP_SECRET = config("FACEBOOK_APP_SECRET", default="")

# Frontend manzili — tasdiqlash havolasi shu domenga yo'naltiriladi
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "apps.ai_teacher",
    "apps.english_library",
    "channels",
    "apps.accounts",
    "apps.subjects",
    "apps.session",
    "apps.statistics",
    "apps.math_practice",
    "apps.avatars",
    "apps.gamification",
    "apps.learning_path",
    "apps.practice_tools",
    "apps.youtube_recommendations",
    "apps.payments",
    "apps.integrations",
    "apps.lessons",
]

MIDDLEWARE = [
    # CorsMiddleware ENG BIRINCHI bo'lishi kerak: SecurityMiddleware'ning SSL redirecti
    # preflight (OPTIONS) so'rovni buzmasligi uchun.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [config("REDIS_URL", default="redis://localhost:6379/2")]},
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth": "10/min",
        "payment": "20/min",
        "activity": "30/min",
        "youtube_search": "20/min",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SuperTutor AI API",
    "DESCRIPTION": "AI asosidagi til va matematika o'qitish platformasi backend API'si",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
}

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/3")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tashkent"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True

YOUTUBE_API_KEY = config("YOUTUBE_API_KEY", default="")
GROQ_API_KEY = config("GROQ_API_KEY", default="")
XAI_API_KEY = config("XAI_API_KEY", default="")
USD_TO_UZS_RATE = config("USD_TO_UZS_RATE", default=12700, cast=int)
PAYME_MERCHANT_ID = config("PAYME_MERCHANT_ID", default="")
PAYME_KEY = config("PAYME_KEY", default="")
CLICK_SERVICE_ID = config("CLICK_SERVICE_ID", default="")
CLICK_MERCHANT_ID = config("CLICK_MERCHANT_ID", default="")
CLICK_SECRET_KEY = config("CLICK_SECRET_KEY", default="")


# === CORS ===
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://talim-ai-pi.vercel.app"
    ),
    cast=lambda v: [
        origin.strip().rstrip("/")
        for origin in v.split(",")
        if origin.strip()
    ],
)

# Faqat SIZNING Vercel jamoangizning preview URL'lariga ruxsat (jamoa nomi bilan toraytirilgan)
_VERCEL_TEAM = r"kadirovrahmatilloqodirov202-6776s-projects"
CORS_ALLOWED_ORIGIN_REGEXES = [
    rf"^https://talim-[a-z0-9]+-{_VERCEL_TEAM}\.vercel\.app$",
    rf"^https://talim-ai-[a-z0-9-]+-{_VERCEL_TEAM}\.vercel\.app$",
]

CORS_ALLOW_CREDENTIALS = True

# CORS_URLS_REGEX olib tashlandi: endi CORS barcha yo'llarga (/api/..., /auth/...) qo'llanadi.


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


XAI_MODEL = config("XAI_MODEL", default="grok-4.1-fast")

# === AI Ustoz (Claude) ===
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL = config("ANTHROPIC_MODEL", default="claude-sonnet-5-5")
AI_TUTOR_HISTORY_LIMIT = config("AI_TUTOR_HISTORY_LIMIT", default=20, cast=int)
AI_TUTOR_MAX_TOOL_ROUNDS = config("AI_TUTOR_MAX_TOOL_ROUNDS", default=8, cast=int)

# === Speaking (ixtiyoriy) ===
WHISPER_MODEL_SIZE = config("WHISPER_MODEL_SIZE", default="small")
SPEAKING_MAX_UPLOAD_MB = config("SPEAKING_MAX_UPLOAD_MB", default=10, cast=int)