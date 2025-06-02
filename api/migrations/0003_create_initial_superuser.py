# api/migrations/0003_create_initial_superuser.py (hoặc tên file tạo superuser của bạn)
from django.db import migrations
import os
from django.utils import timezone
from django.contrib.auth.hashers import make_password # <<<< IMPORT QUAN TRỌNG

def create_custom_superuser(apps, schema_editor):
    UserAccount = apps.get_model("api", "UserAccount") # Lấy model UserAccount từ app 'api'

    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print(">>> DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
        return

    if not UserAccount.objects.filter(tendangnhap=DJANGO_SUPERUSER_USERNAME).exists():
        print(f">>> Attempting to create custom superuser: {DJANGO_SUPERUSER_USERNAME}")
        try:
            # Băm mật khẩu trực tiếp
            hashed_password = make_password(DJANGO_SUPERUSER_PASSWORD)

            user = UserAccount(
                tendangnhap=DJANGO_SUPERUSER_USERNAME,
                email=DJANGO_SUPERUSER_EMAIL,
                ho="Super", # Có thể lấy từ biến môi trường hoặc để mặc định
                ten="User",  # Có thể lấy từ biến môi trường hoặc để mặc định
                matkhau_hashed=hashed_password, # Gán mật khẩu đã băm
                is_admin=True, # Hoặc trường is_superuser nếu bạn dùng theo chuẩn Django
                is_active=True,
                # is_staff=True, # Thêm nếu model UserAccount có trường is_staff và bạn muốn superuser có quyền vào admin site
                date_joined=timezone.now(),
                last_login=timezone.now() # Gán luôn vì model của bạn đã cho phép null
            )
            # Không cần gọi user.set_password() nữa
            user.save()
            print(f">>> Custom superuser {DJANGO_SUPERUSER_USERNAME} created successfully.")
        except Exception as e:
            print(f">>> FAILED to create custom superuser {DJANGO_SUPERUSER_USERNAME}. Error: {e}")
            # Quan trọng: Ném lại lỗi để build thất bại nếu có vấn đề, giúp gỡ lỗi dễ hơn
            # và tránh lỗi TransactionManagementError.
            raise e 
    else:
        print(f">>> Custom superuser with tendangnhap '{DJANGO_SUPERUSER_USERNAME}' already exists.")

class Migration(migrations.Migration):
    dependencies = [
        # Đảm bảo dependency này trỏ đến migration trước đó của app 'api'
        # Ví dụ, nếu bạn có migration 0002_alter_last_login_allow_null.py:
        ('api', '0002_alter_last_login_allow_null'), 
        # Nếu không có migration 0002, thì nó sẽ là:
        # ('api', '0001_initial'), 
    ]
    operations = [
        migrations.RunPython(create_custom_superuser),
    ]