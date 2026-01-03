#!/bin/bash
cd expense_tracker
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:$PORT