# api/migrations/000X_alter_auth_user_last_login_null.py
from django.db import migrations, models
from django.conf import settings # Cần thiết nếu bạn muốn dùng settings.AUTH_USER_MODEL

class Migration(migrations.Migration):

    dependencies = [
        # Đặt dependency này TRƯỚC migration tạo superuser.
        # Nếu '0001_initial' là migration cuối cùng của app 'api' trước khi tạo superuser:
        ('api', '0001_initial'), 
        # Cũng nên phụ thuộc vào migration cuối cùng của app 'auth' tích hợp sẵn
        # để đảm bảo bảng 'auth_user' đã ở trạng thái mong đợi trước khi thay đổi.
        # Tìm migration cuối cùng của app 'auth' trong thư mục .venv của bạn, ví dụ:
        ('auth', '0012_alter_user_first_name_max_length'), # Đây là ví dụ, version có thể khác
    ]

    operations = [
        migrations.AlterField(
            # Vì traceback chỉ rõ là "relation 'auth_user'", chúng ta nhắm vào model 'User' của app 'auth'.
            model_name='user', # Đây là tên model mặc định của Django trong app 'auth'
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]