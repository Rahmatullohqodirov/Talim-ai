from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os
import sys


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self):
        # 1. Signal ishga tushishi uchun
        try:
            from . import signals  # noqa
        except ImportError:
            pass

        # 2. Avtomatik superuser yaratish uchun
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv or 'uvicorn' in sys.argv:
            try:
                User = get_user_model()
                username = os.getenv('ADMIN_USERNAME', 'admin')
                email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
                password = os.getenv('ADMIN_PASSWORD', 'admin12345')

                # Agar bunday user hali bazada bo'lmasa, yaratamiz
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username=username, email=email, password=password)
                    print(f"✅ Avtomatik superuser yaratildi: {username} / {password}")
            except Exception as e:
                pass