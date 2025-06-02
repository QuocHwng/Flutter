# api/migrations/0002_alter_last_login_allow_null.py
from django.db import migrations, models
# from django.conf import settings # Không cần thiết cho cách này

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'), 
        ('auth', '0012_alter_user_first_name_max_length'), # Đảm bảo dependency này đúng
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Phần này sẽ thực thi lệnh SQL trực tiếp trên database
            database_operations=[
                # Lệnh SQL này để thay đổi cột 'last_login' trong bảng 'auth_user'
                # cho phép giá trị NULL trong PostgreSQL.
                migrations.RunSQL(
                    sql="ALTER TABLE auth_user ALTER COLUMN last_login DROP NOT NULL;",
                    # Lệnh reverse_sql để khôi phục (nếu bạn rollback migration)
                    reverse_sql="ALTER TABLE auth_user ALTER COLUMN last_login SET NOT NULL;",
                ),
            ],
            # Phần này sẽ cập nhật "trạng thái" mà Django theo dõi về model.
            # Nó không chạy SQL mà chỉ thay đổi cách Django hiểu model User.
            state_operations=[
                migrations.AlterField(
                    model_name='user',  # Ở đây, 'user' sẽ được hiểu là model User của app 'auth'
                                        # vì Django quản lý state của các model built-in.
                    name='last_login',
                    field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
                ),
            ]
        )
    ]