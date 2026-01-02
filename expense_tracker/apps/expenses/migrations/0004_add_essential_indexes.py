# Generated manually to restore essential database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0003_remove_expenses_expenses_ex_user_id_845e3d_idx_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='expenses',
            index=models.Index(fields=['user', 'date'], name='expenses_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='expenses',
            index=models.Index(fields=['user', 'category'], name='expenses_user_category_idx'),
        ),
    ]