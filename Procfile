# Railway deployment
release: cd expense_tracker && python manage.py migrate --run-syncdb
web: cd expense_tracker && python manage.py collectstatic --noinput && gunicorn expense_tracker.wsgi --log-file -