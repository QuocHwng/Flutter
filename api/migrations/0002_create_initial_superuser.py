# api/migrations/0002_create_initial_superuser.py
from django.db import migrations
from django.contrib.auth import get_user_model
import os
from django.conf import settings
from django.utils import timezone

def create_superuser(apps, schema_editor):
    User = get_user_model() # Sẽ lấy User model đang được sử dụng
    
    DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not DJANGO_SUPERUSER_PASSWORD:
        print(">>> DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
        return

    # Vì traceback chỉ rõ 'auth_user', chúng ta giả định User model này có trường 'username'
    # và đó là USERNAME_FIELD.
    username_field_name = getattr(User, 'USERNAME_FIELD', 'username')
    
    filter_kwargs = {username_field_name: DJANGO_SUPERUSER_USERNAME}

    if not User.objects.filter(**filter_kwargs).exists():
        print(f">>> Creating superuser: {DJANGO_SUPERUSER_USERNAME}")
        
        create_kwargs = {
            username_field_name: DJANGO_SUPERUSER_USERNAME,
            'email': DJANGO_SUPERUSER_EMAIL,
            'password': DJANGO_SUPERUSER_PASSWORD,
        }
        
        # create_superuser sẽ tự động set is_staff=True, is_superuser=True
        # Nó sẽ gọi user.save() bên trong.
        # Chúng ta không thể truyền last_login trực tiếp vào đây.
        try:
            # Bước 1: Tạo superuser. Tại thời điểm này, last_login có thể là null (gây lỗi nếu not-null constraint)
            # Tuy nhiên, với User model mặc định, last_login có thể null ban đầu.
            # Lỗi xảy ra vì database constraint không cho null.
            
            # THAY ĐỔI QUAN TRỌNG:
            # Thay vì gọi create_superuser, chúng ta sẽ tạo một user bình thường trước,
            # sau đó set các cờ superuser và last_login.
            
            # Tạo user với các thông tin cơ bản
            user = User.objects.create_user(
                **create_kwargs
                # Không truyền password trực tiếp vào create_user, mà dùng set_password
            )
            # create_user sẽ tự hash password nếu truyền password.
            # Nếu create_user không nhận password trực tiếp, thì:
            # user = User(**{username_field_name: DJANGO_SUPERUSER_USERNAME, 'email': DJANGO_SUPERUSER_EMAIL})
            # user.set_password(DJANGO_SUPERUSER_PASSWORD)
            
            # Đặt các cờ superuser
            user.is_staff = True
            user.is_superuser = True
            
            # Gán last_login
            # Đây là điểm mấu chốt, đảm bảo last_login có giá trị trước khi save cuối cùng
            # nếu constraint là NOT NULL.
            # Tuy nhiên, User model mặc định của Django có last_login cho phép null.
            # Vấn đề là constraint "NOT NULL" ở mức DB.
            # Điều này thường xảy ra nếu bạn đã có một migration trước đó thay đổi last_login
            # thành NOT NULL, hoặc schema ban đầu của bạn (có thể từ một dự án khác) là như vậy.

            # Gán last_login
            if hasattr(user, 'last_login'):
                 user.last_login = timezone.now()
            
            user.save() # Lưu tất cả các thay đổi (is_staff, is_superuser, last_login)

            print(f">>> Superuser {DJANGO_SUPERUSER_USERNAME} created successfully.")

        except Exception as e:
            print(f">>> Error creating superuser {DJANGO_SUPERUSER_USERNAME}: {e}")
            # In ra traceback đầy đủ hơn nếu cần debug
            import traceback
            traceback.print_exc()
            # Nếu bạn muốn build thất bại khi không tạo được superuser:
            # raise e 

    else:
        print(f">>> Superuser with {username_field_name} '{DJANGO_SUPERUSER_USERNAME}' already exists.")

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'), 
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]