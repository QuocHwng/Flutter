# api/migrations/0002_alter_last_login_allow_null.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'), 
        ('auth', '0012_alter_user_first_name_max_length'), # Chính xác
    ]

    operations = [
        migrations.AlterField(
            model_name='user', # Vì auth.User là model User mặc định
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]