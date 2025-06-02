# api/migrations/0003_create_initial_superuser.py
from django.db import migrations
import os
# Không cần timezone hay make_password trực tiếp ở đây nữa
# vì UserAccountManager sẽ lo việc đó.

def create_custom_superuser_with_manager(apps, schema_editor):
    # LƯU Ý QUAN TRỌNG: Khi dùng apps.get_model trong migration,
    # model lấy ra sẽ không có các phương thức của manager tùy chỉnh (UserAccountManager).
    # Do đó, để tạo superuser trong data migration với custom manager,
    # cách tốt nhất là import trực tiếp manager nếu có thể (không khuyến khích)
    # hoặc chấp nhận rằng lệnh `createsuperuser` của Django CLI là cách chính để tạo superuser
    # sau khi migration schema đã hoàn tất.

    # Cách tiếp cận AN TOÀN NHẤT cho data migration là không dựa vào manager tùy chỉnh
    # mà là tạo bản ghi trực tiếp hoặc sử dụng các phương thức cơ bản của model.
    # Tuy nhiên, vì chúng ta muốn dùng logic của create_superuser, việc này trở nên phức tạp.

    # ĐỂ ĐƠN GIẢN HÓA, HÃY XEM XÉT VIỆC CHẠY LỆNH `createsuperuser` THỦ CÔNG SAU KHI DEPLOY
    # HOẶC QUA MỘT SCRIPT TRÊN RENDER NẾU CẦN TỰ ĐỘNG HÓA BAN ĐẦU.

    # Nếu bạn VẪN MUỐN thử tạo trong migration:
    UserAccount = apps.get_model("api", "UserAccount")
    # Lấy manager từ model lịch sử có thể không hoạt động như mong đợi.
    # Thay vào đó, chúng ta sẽ tạo và set các cờ thủ công hơn.

    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print(">>> DJANGO_SUPERUSER_PASSWORD env var not set. Skipping superuser creation.")
        return

    if not UserAccount.objects.filter(tendangnhap=DJANGO_SUPERUSER_USERNAME).exists():
        print(f">>> Attempting to create superuser via migration (manual fields): {DJANGO_SUPERUSER_USERNAME}")
        try:
            # Vì không gọi được manager.create_superuser, ta phải làm thủ công hơn
            user = UserAccount(
                tendangnhap=DJANGO_SUPERUSER_USERNAME,
                email=UserAccountManager().normalize_email(DJANGO_SUPERUSER_EMAIL), # Dùng normalize từ manager
                ho="Super",
                ten="User",
                is_staff=True,
                is_active=True,
                is_superuser=True, # Từ PermissionsMixin
                is_admin=True # Trường tùy chỉnh của bạn
            )
            user.set_password(DJANGO_SUPERUSER_PASSWORD) # AbstractBaseUser có phương thức này
            user.save()
            print(f">>> Superuser {DJANGO_SUPERUSER_USERNAME} (manual fields) created successfully.")
        except Exception as e:
            print(f">>> FAILED to create superuser {DJANGO_SUPERUSER_USERNAME} (manual fields). Error: {e}")
            raise e
    else:
        print(f">>> Superuser with tendangnhap '{DJANGO_SUPERUSER_USERNAME}' already exists.")


class Migration(migrations.Migration):
    dependencies = [
        # Trỏ đến migration mới tạo ra từ việc thay đổi UserAccount ở Bước 2
        ('api', '000X_auto_xxxx'), # Thay X bằng số migration mới nhất của bạn
    ]
    operations = [
        migrations.RunPython(create_custom_superuser_with_manager),
    ]