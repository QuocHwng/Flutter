# api/migrations/0002_create_initial_superuser.py
from django.db import migrations
from django.contrib.auth import get_user_model
import os
from django.conf import settings
from django.utils import timezone # <<<< THÊM DÒNG NÀY

def create_superuser(apps, schema_editor):
    User = get_user_model() # Điều này sẽ lấy User model được cấu hình (có thể là custom hoặc default)
    
    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com') # Sửa thành email hợp lệ hơn
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print("DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
        return

    if not User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists(): # Hoặc tendangnhap nếu đó là USERNAME_FIELD
        print(f"Creating superuser: {DJANGO_SUPERUSER_USERNAME}")
        
        # Kiểm tra xem User model có trường last_login không và có phải là User model mặc định không
        # Nếu bạn đang dùng UserAccount model của riêng mình với trường tendangnhap là USERNAME_FIELD
        # thì cần điều chỉnh cho phù hợp.
        
        # Giả sử USERNAME_FIELD của bạn là 'tendangnhap' (nếu bạn dùng UserAccount model như trên)
        # hoặc 'username' nếu bạn dùng User model mặc định của Django.
        # Trong traceback, nó đang cố gắng tạo user với "username=admin", "email=admin@gamil.com"
        # Điều này gợi ý rằng có thể User model của bạn vẫn dùng 'username' làm USERNAME_FIELD,
        # hoặc hàm get_user_model() đang trả về User model mặc định của Django.
        
        # Dựa trên traceback "relation 'auth_user'", rất có thể bạn đang dùng User model mặc định của Django
        # hoặc User model tùy chỉnh của bạn chưa được cấu hình đúng làm AUTH_USER_MODEL,
        # và Django đang fallback về User model mặc định cho các thao tác của `django.contrib.auth`.
        
        # Nếu User model của bạn là UserAccount và USERNAME_FIELD là 'tendangnhap'
        if hasattr(User, 'tendangnhap'):
            if User.objects.filter(tendangnhap=DJANGO_SUPERUSER_USERNAME).exists():
                print(f"Superuser với tendangnhap {DJANGO_SUPERUSER_USERNAME} đã tồn tại.")
                return
            user = User.objects.create_superuser(
                tendangnhap=DJANGO_SUPERUSER_USERNAME, # Sử dụng tendangnhap nếu đó là USERNAME_FIELD
                email=DJANGO_SUPERUSER_EMAIL,
                password=DJANGO_SUPERUSER_PASSWORD,
                # last_login=timezone.now() # Có thể thử cách này, nhưng create_superuser không nhận last_login
            )
            # Cách an toàn hơn là tạo user rồi gán last_login và lưu lại
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        # Nếu User model của bạn dùng 'username' làm USERNAME_FIELD (như User mặc định)
        elif hasattr(User, 'username'):
            if User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists():
                print(f"Superuser với username {DJANGO_SUPERUSER_USERNAME} đã tồn tại.")
                return
            user = User.objects.create_superuser(
                username=DJANGO_SUPERUSER_USERNAME,
                email=DJANGO_SUPERUSER_EMAIL,
                password=DJANGO_SUPERUSER_PASSWORD,
            )
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
        else:
            print("Không thể xác định USERNAME_FIELD cho User model. Bỏ qua tạo superuser.")
            return
        
        print(f"Đã tạo superuser: {DJANGO_SUPERUSER_USERNAME}")
    else:
        # Kiểm tra cả username và tendangnhap nếu có thể
        username_field_value = DJANGO_SUPERUSER_USERNAME
        if hasattr(User, 'tendangnhap') and User.USERNAME_FIELD == 'tendangnhap':
             if User.objects.filter(tendangnhap=DJANGO_SUPERUSER_USERNAME).exists():
                print(f"Superuser với tendangnhap {DJANGO_SUPERUSER_USERNAME} đã tồn tại.")
        elif hasattr(User, 'username') and User.USERNAME_FIELD == 'username':
            if User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists():
                print(f"Superuser với username {DJANGO_SUPERUSER_USERNAME} đã tồn tại.")
        else:
            print(f"Superuser {DJANGO_SUPERUSER_USERNAME} (hoặc tương đương) đã tồn tại.")


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]