# api/migrations/0003_create_initial_superuser.py (hoặc tên file tạo superuser của bạn)
from django.db import migrations
# from django.contrib.auth import get_user_model # Không cần thiết nếu bạn import UserAccount trực tiếp
import os
# from django.conf import settings # Không cần nếu không dùng swappable_dependency
from django.utils import timezone

# Import trực tiếp model UserAccount từ app 'api'
# Điều này được phép trong data migrations nếu model đã được định nghĩa trong migration trước đó (0001_initial)
# Hoặc dùng apps.get_model("api", "UserAccount")

def create_custom_superuser(apps, schema_editor):
    UserAccount = apps.get_model("api", "UserAccount") # Cách an toàn để lấy model trong migration

    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print(">>> DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
        return

    # Kiểm tra xem user đã tồn tại chưa bằng 'tendangnhap'
    if not UserAccount.objects.filter(tendangnhap=DJANGO_SUPERUSER_USERNAME).exists():
        print(f">>> Attempting to create custom superuser: {DJANGO_SUPERUSER_USERNAME}")
        try:
            user = UserAccount(
                tendangnhap=DJANGO_SUPERUSER_USERNAME,
                email=DJANGO_SUPERUSER_EMAIL,
                ho="Super", # Bạn có thể đặt giá trị mặc định hoặc lấy từ env
                ten="User",  # Bạn có thể đặt giá trị mặc định hoặc lấy từ env
                is_admin=True,
                is_active=True,
                date_joined=timezone.now(),
                last_login=timezone.now() # Gán luôn vì model của bạn cho phép null=True rồi
            )
            user.set_password(DJANGO_SUPERUSER_PASSWORD) # Sử dụng phương thức set_password của bạn
            user.save()
            print(f">>> Custom superuser {DJANGO_SUPERUSER_USERNAME} created successfully.")
        except Exception as e:
            print(f">>> FAILED to create custom superuser {DJANGO_SUPERUSER_USERNAME}. Error: {e}")
            raise e 
    else:
        print(f">>> Custom superuser with tendangnhap '{DJANGO_SUPERUSER_USERNAME}' already exists.")

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0002_alter_last_login_allow_null'), # Phụ thuộc vào migration sửa last_login của UserAccount
        # Không cần swappable_dependency(settings.AUTH_USER_MODEL) ở đây nữa
        # vì chúng ta đã xác định User model là của app 'api'
    ]
    operations = [
        migrations.RunPython(create_custom_superuser),
    ]