# api/migrations/0003_create_initial_superuser.py (hoặc tên mới của bạn)
from django.db import migrations, models # Thêm models nếu chưa có
from django.contrib.auth import get_user_model
import os
from django.conf import settings
from django.utils import timezone # Vẫn cần timezone nếu bạn muốn gán last_login

def create_superuser_safe(apps, schema_editor): # Đổi tên hàm cho rõ
    User = get_user_model()
    
    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print(">>> DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
        return

    username_field_name = getattr(User, 'USERNAME_FIELD', 'username')
    filter_kwargs = {username_field_name: DJANGO_SUPERUSER_USERNAME}

    if not User.objects.filter(**filter_kwargs).exists():
        print(f">>> Attempting to create superuser: {DJANGO_SUPERUSER_USERNAME}")
        try:
            # Gọi trực tiếp create_superuser.
            # Nếu migration trước (alter_last_login_allow_null) đã chạy thành công,
            # thì DB sẽ cho phép last_login là NULL, và create_superuser sẽ hoạt động.
            user = User.objects.create_superuser(
                **{username_field_name: DJANGO_SUPERUSER_USERNAME},
                email=DJANGO_SUPERUSER_EMAIL,
                password=DJANGO_SUPERUSER_PASSWORD
            )
            # Tùy chọn: Nếu bạn vẫn muốn set last_login ngay, mặc dù DB đã cho phép null:
            if hasattr(user, 'last_login'):
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            print(f">>> Superuser {DJANGO_SUPERUSER_USERNAME} created successfully.")
        except Exception as e:
            print(f">>> FAILED to create superuser {DJANGO_SUPERUSER_USERNAME}. Error: {e}")
            # QUAN TRỌNG: Ném lại lỗi để build thất bại nếu không tạo được superuser
            # Điều này sẽ ngăn lỗi TransactionManagementError.
            raise e 
    else:
        print(f">>> Superuser with {username_field_name} '{DJANGO_SUPERUSER_USERNAME}' already exists.")

class Migration(migrations.Migration):
    dependencies = [
        # Đảm bảo dependency này trỏ đến migration sửa last_login
        ('api', '0002_alter_auth_user_last_login_null'), # Tên file migration mới của bạn
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.RunPython(create_superuser_safe), # Sử dụng hàm đã sửa
    ]