# api/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class UserAccount(models.Model):
    tendangnhap = models.CharField(max_length=100, unique=True, verbose_name="Tên đăng nhập")
    email = models.EmailField(max_length=100, unique=True, verbose_name="Email")
    ho = models.CharField(max_length=100, verbose_name="Họ")
    ten = models.CharField(max_length=100, verbose_name="Tên")
    matkhau_hashed = models.CharField(max_length=128, verbose_name="Mật khẩu (đã băm)")
    is_admin = models.BooleanField(default=False, verbose_name="Là quản trị viên kho")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động") # Quan trọng cho is_authenticated
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Ngày tham gia")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Đăng nhập lần cuối")

    USERNAME_FIELD = 'tendangnhap'
    REQUIRED_FIELDS = ['email', 'ho', 'ten']

    # --- THÊM CÁC THUỘC TÍNH SAU ---
    @property
    def is_anonymous(self):
        """
        Luôn trả về False cho các instance của UserAccount.
        User ẩn danh sẽ là một instance của AnonymousUser từ django.contrib.auth.models.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Luôn trả về True cho các instance của UserAccount nếu is_active.
        Model này đại diện cho user đã được xác thực.
        """
        return self.is_active # Hoặc chỉ đơn giản là True nếu bạn không dùng is_active để kiểm soát việc đăng nhập

    # Bạn cũng có thể cần is_staff nếu muốn tích hợp với Django admin
    # is_staff = models.BooleanField(default=False, verbose_name="Có quyền truy cập admin site")

    # --- KẾT THÚC PHẦN THÊM ---

    def set_password(self, raw_password):
        self.matkhau_hashed = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.matkhau_hashed)

    def __str__(self):
        return f"{self.ho} {self.ten} ({self.tendangnhap}){' (Admin)' if self.is_admin else ''}"

    class Meta:
        verbose_name = "Tài khoản người dùng (Tùy chỉnh)"
        verbose_name_plural = "Các tài khoản người dùng (Tùy chỉnh)"
        ordering = ['tendangnhap']


# --- Các model khác (ProductCategory, Unit, Supplier, Product) ---
# Giữ nguyên như trước, không thay đổi gì ở đây
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên loại hàng")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    def __str__(self): return self.name
    class Meta: verbose_name = "Loại hàng hóa"; verbose_name_plural = "Các loại hàng hóa"

class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tên đơn vị")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    def __str__(self): return self.name
    class Meta: verbose_name = "Đơn vị tính"; verbose_name_plural = "Các đơn vị tính"

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên nhà cung cấp")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Người liên hệ")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    def __str__(self): return self.name
    class Meta: verbose_name = "Nhà cung cấp"; verbose_name_plural = "Các nhà cung cấp"

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loại hàng")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, verbose_name="Đơn vị tính")
    quantity_on_hand = models.IntegerField(default=0, verbose_name="Số lượng tồn kho")
    def __str__(self): return f"{self.name} ({self.code})"
    class Meta: verbose_name = "Hàng hóa"; verbose_name_plural = "Các mặt hàng"


# --- Model Phiếu Nhập/Xuất sẽ trỏ đến UserAccount ---
class GoodsReceiptNote(models.Model):
    receipt_code = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Mã phiếu nhập")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Nhà cung cấp")
    receipt_date = models.DateField(verbose_name="Ngày nhập")
    staff_account = models.ForeignKey(UserAccount, on_delete=models.PROTECT, verbose_name="Nhân viên thực hiện") # Trỏ đến UserAccount
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.receipt_code
    class Meta: verbose_name = "Phiếu nhập kho"; verbose_name_plural = "Các phiếu nhập kho"

class GoodsReceiptNoteItem(models.Model):
    receipt_note = models.ForeignKey(GoodsReceiptNote, related_name='items', on_delete=models.CASCADE, verbose_name="Phiếu nhập")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng nhập")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Đơn giá nhập")
    def __str__(self): return f"{self.product.name} - SL: {self.quantity}"
    class Meta: verbose_name = "Chi tiết phiếu nhập"; verbose_name_plural = "Các chi tiết phiếu nhập"

class GoodsIssueNote(models.Model):
    issue_code = models.CharField(max_length=50, unique=True, verbose_name="Mã phiếu xuất")
    issued_to = models.CharField(max_length=200, verbose_name="Xuất cho (Công trình/Ai)")
    reason = models.TextField(blank=True, null=True, verbose_name="Lý do xuất")
    issue_date = models.DateField(verbose_name="Ngày xuất")
    staff_account = models.ForeignKey(UserAccount, on_delete=models.PROTECT, verbose_name="Nhân viên thực hiện") # Trỏ đến UserAccount
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.issue_code
    class Meta: verbose_name = "Phiếu xuất kho"; verbose_name_plural = "Các phiếu xuất kho"

class GoodsIssueNoteItem(models.Model):
    issue_note = models.ForeignKey(GoodsIssueNote, related_name='items', on_delete=models.CASCADE, verbose_name="Phiếu xuất")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng xuất")
    def __str__(self): return f"{self.product.name} - SL: {self.quantity}"
    class Meta: verbose_name = "Chi tiết phiếu xuất"; verbose_name_plural = "Các chi tiết phiếu xuất"