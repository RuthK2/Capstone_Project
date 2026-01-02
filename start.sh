#!/bin/bash
echo "Removing old database..."
rm -f db.sqlite3
echo "Running fresh migrations..."
python manage.py migrate
echo "Creating categories..."
python manage.py shell -c "from apps.categories.models import Category; Category.objects.get_or_create(name='Groceries'); Category.objects.get_or_create(name='Utilities'); Category.objects.get_or_create(name='Transportation')"
echo "Starting server..."
python manage.py runserver 0.0.0.0:$PORT