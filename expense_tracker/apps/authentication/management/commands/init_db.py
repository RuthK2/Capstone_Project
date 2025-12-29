from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Initialize database for production'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database...')
        
        # Ensure /tmp directory exists and is writable
        db_path = '/tmp/expense_tracker.db'
        self.stdout.write(f'Database path: {db_path}')
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', '--run-syncdb', verbosity=2)
        call_command('migrate', verbosity=2)
        
        # Verify tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.stdout.write(f'Tables created: {[t[0] for t in tables]}')
            
        self.stdout.write(self.style.SUCCESS('Database initialization complete'))