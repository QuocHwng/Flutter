# api/migrations/0002_alter_last_login_allow_null.py
from django.db import migrations, models
# from django.conf import settings # Bạn không cần settings ở đây nếu hardcode app 'auth'

class Migration(migrations.Migration):

    dependencies = [
        # Dependency của bạn ở đây
        ('api', '0001_initial'), 
        ('auth', '0012_alter_user_first_name_max_length'), # Đảm bảo dependency vào migration cuối của 'auth'
    ]

    operations = [
        migrations.AlterField(
            # SỬA Ở ĐÂY:
            # Thay vì model_name='user' (ngầm hiểu là trong app hiện tại 'api')
            # bạn cần chỉ rõ app_label là 'auth' và model_name là 'user'.
            # Tuy nhiên, cách đúng để tham chiếu model của app khác trong AlterField
            # là không dùng app_label ở đây, mà Django sẽ tự hiểu qua tên model.
            # Django sẽ tìm model 'User' trong tất cả các app đã biết.
            # Nhưng để an toàn hơn và rõ ràng hơn, nhất là khi tên model có thể trùng,
            # cách tốt nhất là đảm bảo dependency đúng và Django sẽ giải quyết.
            # Hoặc, cách Django thường làm là migration này nên nằm trong app 'auth'.
            # Vì migration này đang ở app 'api', chúng ta cần cẩn thận.

            # CÁCH 1: Giữ migration ở app 'api' nhưng trỏ đúng
            # model_name='User', # Django sẽ cố tìm model tên 'User' ở đâu đó
            # Nếu cách trên không đủ, bạn có thể cần một cách khác.
            # Tuy nhiên, thông thường, Django sẽ tìm 'User' trong app 'auth' nếu nó là User model mặc định.

            # CÁCH CHÍNH XÁC NHẤT KHI ALTERFIELD CHO MODEL CỦA APP KHÁC:
            # Migration này nên nằm trong app 'auth'.
            # Nếu BẮT BUỘC phải đặt ở app 'api', thì cách an toàn nhất là
            # đảm bảo `settings.AUTH_USER_MODEL` được Django hiểu đúng tại thời điểm này.
            # Nhưng vì đây là thao tác mức thấp, chỉ cần tên bảng đúng là được.
            # Bảng là 'auth_user'.

            # Hãy thử cách đơn giản nhất trước:
            model_name='user', # Vì model User mặc định của Django có tên là 'User' và thuộc app 'auth'
                               # Django sẽ cố gắng tìm nó.
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]