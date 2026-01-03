from django.apps import AppConfig
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    
    def ready(self):
        import apps.authentication.signals
        
        # Force migrations on startup for production
        try:
            # Check if basic Django tables exist
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
                if not cursor.fetchone():
                    print("Creating database tables...")
                    call_command('migrate', '--run-syncdb', verbosity=1)
                    print("Database setup complete.")
        except Exception as e:
            print(f"Migration error: {e}")
            # Try basic migration anyway
            try:
                call_command('migrate', verbosity=1)
            except:
                pass
