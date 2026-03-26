from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Creates a superuser for production'

    def handle(self, *args, **kwargs):
        username = os.getenv('SUPERUSER_USERNAME', 'admin') 
        password = os.getenv('SUPERUSER_PASSWORD', 'adminpass123') 
        email = os.getenv('SUPERUSER_EMAIL', '')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email
            )
            self.stdout.write(f'Superuser {username} created.')
        else:
            self.stdout.write(f'Superuser {username} already exists.')