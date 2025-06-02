# api/admin.py
from django.contrib import admin
from .models import (
    UserAccount, ProductCategory, Unit, Supplier, Product,
    GoodsReceiptNote, GoodsReceiptNoteItem,
    GoodsIssueNote, GoodsIssueNoteItem
)

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('tendangnhap', 'email', 'ho', 'ten', 'is_admin', 'is_active', 'date_joined', 'last_login')
    search_fields = ('tendangnhap', 'email', 'ho', 'ten')
    list_filter = ('is_admin', 'is_active')
    readonly_fields = ('date_joined', 'last_login', 'matkhau_hashed') # Không hiển thị mật khẩu băm trực tiếp để sửa

    fieldsets = (
        (None, {'fields': ('tendangnhap', 'email')}),
        ('Thông tin cá nhân', {'fields': ('ho', 'ten')}),
        ('Trạng thái & Quyền', {'fields': ('is_active', 'is_admin')}),
        ('Thông tin hệ thống', {'fields': ('date_joined', 'last_login', 'matkhau_hashed')}),
    )
    # Lưu ý: Không có cách dễ dàng để thay đổi mật khẩu qua admin với model này
    # vì nó không tích hợp với hệ thống UserAdmin của Django.
    # Bạn sẽ cần tạo một form tùy chỉnh hoặc action nếu muốn đổi mật khẩu qua admin.

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