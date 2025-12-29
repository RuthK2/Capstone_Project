# Railway deployment
web: cd expense_tracker && python manage.py setup_db && python manage.py collectstatic --noinput && gunicorn expense_tracker.wsgi --log-file -