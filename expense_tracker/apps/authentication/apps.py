from django.apps import AppConfig
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError
import os

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    
    def ready(self):
        # Run migrations on startup if tables don't exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM auth_user LIMIT 1;")
        except OperationalError:
            # Tables don't exist, run migrations
            print("Running migrations...")
            call_command('migrate', '--run-syncdb', verbosity=0)
            call_command('migrate', verbosity=0)
            print("Migrations complete")
