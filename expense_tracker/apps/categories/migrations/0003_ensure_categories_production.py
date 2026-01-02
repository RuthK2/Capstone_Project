# Generated manually to ensure categories exist in production

from django.db import migrations


def ensure_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    predefined_categories = [
        'Groceries',
        'Transportation', 
        'Utilities',
        'Healthcare',
        'Entertainment',
        'Dining',
        'Clothing',
        'Education',
        'Bills',
        'Miscellaneous'
    ]
    
    for category_name in predefined_categories:
        Category.objects.get_or_create(name=category_name)


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_populate_predefined_categories'),
    ]

    operations = [
        migrations.RunPython(ensure_categories, migrations.RunPython.noop),
    ]