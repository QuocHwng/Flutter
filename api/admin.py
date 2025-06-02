from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class UserAccountAdmin(BaseUserAdmin):
    list_display = ('tendangnhap', 'email', 'ho', 'ten', 'is_staff', 'is_admin', 'is_active', 'is_superuser') # Thêm is_superuser
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_admin', 'groups')
    
    fieldsets = (
        (None, {'fields': ('tendangnhap', 'password')}), # 'password' là trường của AbstractBaseUser
        ('Thông tin cá nhân', {'fields': ('ho', 'ten', 'email')}),
        ('Quyền hạn', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 
                                       'groups', 'user_permissions')}),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Sử dụng 'password' thay vì 'password_1' và 'password_2' nếu BaseUserAdmin xử lý form tạo user
            # Hoặc bạn có thể cần một form tùy chỉnh cho việc add user nếu BaseUserAdmin không tự xử lý tốt
            # với các trường tùy chỉnh của bạn khi tạo.
            # Để đơn giản, trước mắt hãy đảm bảo các trường chính xác.
            'fields': ('tendangnhap', 'email', 'ho', 'ten', 
                       # BaseUserAdmin sẽ có widget cho password khi tạo mới
                       # Nếu bạn muốn tùy chỉnh hoàn toàn, bạn sẽ cần custom form.
                       # Thông thường, để BaseUserAdmin xử lý password khi tạo, bạn không cần khai báo tường minh ở đây.
                       # Hãy thử bỏ 'password_1', 'password_2' nếu BaseUserAdmin tự thêm widget password.
                       # Nếu không, bạn cần 'password_1' và 'password_2' để UserCreationForm hoạt động.
                       # Tuy nhiên, lỗi hiện tại không phải ở đây.
                      ),
        }),
        # Thêm các fieldset cho quyền hạn khi tạo user nếu cần
        ('Quyền hạn (Khi tạo)', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin')
        })
    )
    search_fields = ('tendangnhap', 'email', 'ho', 'ten')
    ordering = ('tendangnhap',)
    filter_horizontal = ('groups', 'user_permissions',)

    # XÓA HOẶC SỬA readonly_fields NẾU BẠN CÓ KHAI BÁO NÓ
    # Nếu bạn có dòng như sau, hãy xóa 'matkhau_hashed' đi:
    # readonly_fields = ('last_login', 'date_joined', 'matkhau_hashed')
    # Sửa thành:
    readonly_fields = ('last_login', 'date_joined') 
    # Hoặc để Django tự xử lý các trường readonly mặc định của BaseUserAdmin nếu bạn không cần thêm.

admin.site.register(UserAccount, UserAccountAdmin)

# Các đăng ký model khác giữ nguyên, đảm bảo staff_account được hiển thị đúng
admin.site.register(ProductCategory)
admin.site.register(Unit)
admin.site.register(Supplier)
admin.site.register(Product)

class GoodsReceiptNoteItemInline(admin.TabularInline): model = GoodsReceiptNoteItem; extra = 1
@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ('receipt_code', 'supplier', 'receipt_date', 'staff_account', 'created_at')
    list_filter = ('receipt_date', 'supplier', 'staff_account')
    search_fields = ('receipt_code', 'supplier__name', 'staff_account__tendangnhap')
    inlines = [GoodsReceiptNoteItemInline]
    raw_id_fields = ('staff_account',) # Để dễ chọn UserAccount

class GoodsIssueNoteItemInline(admin.TabularInline): model = GoodsIssueNoteItem; extra = 1
@admin.register(GoodsIssueNote)
class GoodsIssueNoteAdmin(admin.ModelAdmin):
    list_display = ('issue_code', 'issued_to', 'issue_date', 'staff_account', 'created_at')
    list_filter = ('issue_date', 'staff_account')
    search_fields = ('issue_code', 'issued_to', 'staff_account__tendangnhap')
    inlines = [GoodsIssueNoteItemInline]
    raw_id_fields = ('staff_account',)