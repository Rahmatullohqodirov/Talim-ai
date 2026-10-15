from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Avtomatik test yoki admin user yaratish'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
            self.stdout.write(self.style.SUCCESS('Successfully created default superuser'))
        else:
            self.stdout.write('Superuser already exists')