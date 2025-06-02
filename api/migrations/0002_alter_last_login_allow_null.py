# api/migrations/0002_alter_last_login_allow_null.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'), 
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount', # Trỏ đến model 'UserAccount' của app 'api'
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Đăng nhập lần cuối'),
        ),
    ]