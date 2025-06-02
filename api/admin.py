from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import * 

# Nếu bạn muốn tùy chỉnh cách UserAccount hiển thị trong admin
class UserAccountAdmin(BaseUserAdmin):
    # Các trường hiển thị trong list view
    list_display = ('tendangnhap', 'email', 'ho', 'ten', 'is_staff', 'is_admin', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_admin', 'groups')
    
    # Các trường trong form edit/add
    # fieldsets lấy từ BaseUserAdmin và điều chỉnh cho phù hợp với các trường của UserAccount
    fieldsets = (
        (None, {'fields': ('tendangnhap', 'password')}), # 'password' là trường của AbstractBaseUser
        ('Thông tin cá nhân', {'fields': ('ho', 'ten', 'email')}),
        ('Quyền hạn', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin',
                                       'groups', 'user_permissions')}),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )
    # add_fieldsets cũng tương tự cho form add user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('tendangnhap', 'email', 'ho', 'ten', 'password_1', 'password_2'), # Dùng password_1, password_2 cho việc tạo
        }),
    )
    search_fields = ('tendangnhap', 'email', 'ho', 'ten')
    ordering = ('tendangnhap',)
    filter_horizontal = ('groups', 'user_permissions',) # Cho many-to-many fields

    # Nếu UserAccount có trường 'username' nhưng USERNAME_FIELD là 'tendangnhap',
    # bạn có thể cần điều chỉnh thêm. Nhưng vì bạn không có 'username', điều này có thể không cần.

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