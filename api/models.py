# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin # THÊM IMPORT
from django.utils import timezone

# --- TẠO CUSTOM USER MANAGER ---
class UserAccountManager(BaseUserManager):
    def create_user(self, tendangnhap, email, ho, ten, password=None, **extra_fields):
        if not tendangnhap:
            raise ValueError('Tên đăng nhập là bắt buộc')
        if not email:
            raise ValueError('Email là bắt buộc')
        
        email = self.normalize_email(email)
        user = self.model(
            tendangnhap=tendangnhap, 
            email=email, 
            ho=ho, 
            ten=ten, 
            **extra_fields
        )
        user.set_password(password) # AbstractBaseUser có phương thức này
        user.save(using=self._db)
        return user

    def create_superuser(self, tendangnhap, email, ho, ten, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True) # Từ PermissionsMixin
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True) # Trường is_admin tùy chỉnh của bạn (nếu vẫn muốn giữ)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser phải có is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_superuser=True.')

        return self.create_user(tendangnhap, email, ho, ten, password, **extra_fields)

# --- SỬA MODEL USERACCOUNT ---
class UserAccount(AbstractBaseUser, PermissionsMixin): # KẾ THỪA TỪ ĐÂY
    tendangnhap = models.CharField(max_length=100, unique=True, verbose_name="Tên đăng nhập")
    email = models.EmailField(max_length=100, unique=True, verbose_name="Email")
    ho = models.CharField(max_length=100, verbose_name="Họ")
    ten = models.CharField(max_length=100, verbose_name="Tên")
    # matkhau_hashed không cần nữa, AbstractBaseUser có trường 'password' để lưu mật khẩu đã băm.
    
    is_admin = models.BooleanField(default=False, verbose_name="Là quản trị viên kho (tùy chỉnh)") # Bạn có thể giữ lại nếu có logic riêng
                                                                                             # hoặc chỉ dựa vào is_superuser và permissions.
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    is_staff = models.BooleanField(default=False, verbose_name="Có quyền truy cập admin site") # Rất quan trọng cho admin
    # is_superuser đã có từ PermissionsMixin
    
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Ngày tham gia")
    # last_login đã có trong AbstractBaseUser và được tự động cập nhật.

    objects = UserAccountManager() # GÁN CUSTOM MANAGER

    USERNAME_FIELD = 'tendangnhap'
    REQUIRED_FIELDS = ['email', 'ho', 'ten'] # Các trường yêu cầu khi tạo superuser qua CLI

    # Các phương thức set_password, check_password đã có trong AbstractBaseUser.
    # Các thuộc tính is_anonymous, is_authenticated cũng đã có.

    def __str__(self):
        return f"{self.ho} {self.ten} ({self.tendangnhap})"

    # get_full_name và get_short_name nếu cần (PermissionsMixin có thể cung cấp chúng dựa trên các trường khác)
    def get_full_name(self):
        return f"{self.ho} {self.ten}".strip()

    def get_short_name(self):
        return self.ten

    class Meta:
        verbose_name = "Tài khoản người dùng" # Sửa lại cho ngắn gọn hơn
        verbose_name_plural = "Các tài khoản người dùng"
        ordering = ['tendangnhap']

# --- Các model khác (ProductCategory, Unit, Supplier, Product, etc.) ---
# Giữ nguyên như bạn đã cung cấp
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
    email = models.EmailField(blank=True, null=True, verbose_name="Email") # Sửa max_length nếu cần, EmailField mặc định là 254
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    def __str__(self): return self.name
    class Meta: verbose_name = "Nhà cung cấp"; verbose_name_plural = "Các nhà cung cấp"

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loại hàng")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, verbose_name="Đơn vị tính") # Để blank=True nếu đơn vị tính có thể không có
    quantity_on_hand = models.IntegerField(default=0, verbose_name="Số lượng tồn kho")
    def __str__(self): return f"{self.name} ({self.code})"
    class Meta: verbose_name = "Hàng hóa"; verbose_name_plural = "Các mặt hàng"

class GoodsReceiptNote(models.Model):
    receipt_code = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Mã phiếu nhập") # blank=True nếu bạn tự sinh code
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Nhà cung cấp")
    receipt_date = models.DateField(verbose_name="Ngày nhập")
    staff_account = models.ForeignKey(UserAccount, on_delete=models.PROTECT, verbose_name="Nhân viên thực hiện")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.receipt_code
    class Meta: verbose_name = "Phiếu nhập kho"; verbose_name_plural = "Các phiếu nhập kho"

class GoodsReceiptNoteItem(models.Model):
    receipt_note = models.ForeignKey(GoodsReceiptNote, related_name='items', on_delete=models.CASCADE, verbose_name="Phiếu nhập")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng nhập") # Cân nhắc PositiveIntegerField
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Đơn giá nhập")
    def __str__(self): return f"{self.product.name} - SL: {self.quantity}"
    class Meta: verbose_name = "Chi tiết phiếu nhập"; verbose_name_plural = "Các chi tiết phiếu nhập"

class GoodsIssueNote(models.Model):
    issue_code = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Mã phiếu xuất") # blank=True nếu bạn tự sinh code
    issued_to = models.CharField(max_length=200, verbose_name="Xuất cho (Công trình/Ai)")
    reason = models.TextField(blank=True, null=True, verbose_name="Lý do xuất")
    issue_date = models.DateField(verbose_name="Ngày xuất")
    staff_account = models.ForeignKey(UserAccount, on_delete=models.PROTECT, verbose_name="Nhân viên thực hiện")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.issue_code
    class Meta: verbose_name = "Phiếu xuất kho"; verbose_name_plural = "Các phiếu xuất kho"

class GoodsIssueNoteItem(models.Model):
    issue_note = models.ForeignKey(GoodsIssueNote, related_name='items', on_delete=models.CASCADE, verbose_name="Phiếu xuất")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng xuất") # Cân nhắc PositiveIntegerField
    def __str__(self): return f"{self.product.name} - SL: {self.quantity}"
    class Meta: verbose_name = "Chi tiết phiếu xuất"; verbose_name_plural = "Các chi tiết phiếu xuất"