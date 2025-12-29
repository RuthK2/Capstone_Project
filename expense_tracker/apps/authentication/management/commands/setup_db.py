from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Setup database with all required tables'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database...')
        
        # Run migrations
        call_command('migrate', '--run-syncdb', verbosity=2)
        call_command('migrate', verbosity=2)
        
        # Check if auth_user table exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.auth_user');")
            result = cursor.fetchone()
            if result[0]:
                self.stdout.write(self.style.SUCCESS('auth_user table exists'))
            else:
                self.stdout.write(self.style.ERROR('auth_user table missing'))
        
        self.stdout.write(self.style.SUCCESS('Database setup complete'))