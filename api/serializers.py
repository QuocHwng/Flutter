# api/serializers.py
from rest_framework import serializers # THÊM DÒNG NÀY
from django.db import transaction
from django.utils import timezone
from .models import * # Import tất cả model của bạn
# from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken # Dòng này có vẻ không được sử dụng, có thể bỏ nếu không cần

# User Serializer
class UserAccountPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ('id', 'tendangnhap', 'email', 'ho', 'ten', 'is_admin', 'is_active', 'date_joined', 'last_login')
        read_only_fields = fields


class UserAccountRegisterSerializer(serializers.ModelSerializer):
    matkhau = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Mật khẩu")
    matkhau2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Xác nhận mật khẩu")

    class Meta:
        model = UserAccount
        fields = ('tendangnhap', 'email', 'ho', 'ten', 'matkhau', 'matkhau2', 'is_admin')
        extra_kwargs = {
            'is_admin': {'default': False}
        }

    def validate_tendangnhap(self, value):
        if UserAccount.objects.filter(tendangnhap=value).exists():
            raise serializers.ValidationError("Tên đăng nhập này đã được sử dụng.")
        return value

    def validate_email(self, value):
        if UserAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError("Địa chỉ email này đã được sử dụng.")
        return value

    def validate(self, attrs):
        if attrs['matkhau'] != attrs['matkhau2']:
            raise serializers.ValidationError({"matkhau": "Mật khẩu không khớp."})
        return attrs

    def create(self, validated_data):
        raw_password = validated_data.pop('matkhau')
        validated_data.pop('matkhau2')
        
        user = UserAccount(**validated_data)
        user.set_password(raw_password)
        user.save()
        return user

class UserAccountLoginSerializer(serializers.Serializer):
    tendangnhap = serializers.CharField(required=True)
    matkhau = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

# Master Data Serializers
# Bạn có thể định nghĩa rõ ràng thay vì dùng type() để dễ đọc và debug hơn
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'description', 'category', 'category_name', 'unit', 'unit_name', 'quantity_on_hand']
        read_only_fields = ['quantity_on_hand']


# Goods Receipt Serializers
class GoodsReceiptNoteItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    product_code = serializers.CharField(source='product.code', read_only=True, allow_null=True)

    class Meta:
        model = GoodsReceiptNoteItem
        fields = ['id', 'product', 'product_name', 'product_code', 'quantity', 'unit_price']

class GoodsReceiptNoteSerializer(serializers.ModelSerializer):
    items = GoodsReceiptNoteItemSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True, allow_null=True)
    staff_account_details = UserAccountPublicSerializer(source='staff_account', read_only=True)

    class Meta:
        model = GoodsReceiptNote
        fields = [
            'id', 'receipt_code', 'supplier', 'supplier_name', 'receipt_date',
            'staff_account', 
            'staff_account_details',
            'notes', 'created_at', 'items'
        ]
        read_only_fields = ('created_at', 'id', 'supplier_name', 
                            'staff_account', 'staff_account_details', 
                            'receipt_code')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Phiếu nhập kho phải có ít nhất một mặt hàng.")
        for item_data in value:
            if item_data.get('quantity', 0) <= 0:
                raise serializers.ValidationError({"items": "Số lượng mặt hàng phải lớn hơn 0."})
            if item_data.get('unit_price', 0) < 0:
                raise serializers.ValidationError({"items": "Đơn giá mặt hàng không được âm."})
        return value

    def _generate_receipt_code(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        last_receipt = GoodsReceiptNote.objects.order_by('-id').first()
        next_id = (last_receipt.id + 1) if last_receipt else 1
        new_code = f"PN{timestamp}-{next_id:04d}"
        while GoodsReceiptNote.objects.filter(receipt_code=new_code).exists():
            next_id +=1
            new_code = f"PN{timestamp}-{next_id:04d}"
        return new_code

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        staff_account_id_from_context = self.context.get('staff_account_id')

        if not staff_account_id_from_context:
            raise serializers.ValidationError({"detail": "Không thể xác định người dùng thực hiện."})
        
        try:
            staff_user_instance = UserAccount.objects.get(pk=staff_account_id_from_context, is_active=True)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError({"detail": "Tài khoản người dùng không hợp lệ hoặc không hoạt động."})
        
        validated_data['staff_account'] = staff_user_instance
        validated_data['receipt_code'] = self._generate_receipt_code()

        with transaction.atomic():
            receipt_note = GoodsReceiptNote.objects.create(**validated_data)
            for item_data in items_data:
                product_instance = item_data.get('product')
                if not product_instance:
                     raise serializers.ValidationError({"items": "Mỗi mặt hàng phải có thông tin sản phẩm (ID sản phẩm)."})
                
                GoodsReceiptNoteItem.objects.create(receipt_note=receipt_note, **item_data)
                
                product_instance.quantity_on_hand += item_data['quantity']
                product_instance.save()
        return receipt_note

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None) 
        
        validated_data.pop('staff_account', None)
        validated_data.pop('receipt_code', None)

        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.receipt_date = validated_data.get('receipt_date', instance.receipt_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()

        if items_data is not None:
            with transaction.atomic():
                old_items_product_quantities = {}
                for old_item in instance.items.all():
                    old_items_product_quantities[old_item.product_id] = old_items_product_quantities.get(old_item.product_id, 0) + old_item.quantity
                
                for product_id, total_quantity in old_items_product_quantities.items():
                    try:
                        product_to_revert = Product.objects.get(id=product_id)
                        product_to_revert.quantity_on_hand -= total_quantity
                        if product_to_revert.quantity_on_hand < 0: product_to_revert.quantity_on_hand = 0
                        product_to_revert.save()
                    except Product.DoesNotExist:
                        pass 

                instance.items.all().delete()

                for item_data in items_data:
                    product_instance = item_data.get('product')
                    if not product_instance:
                        raise serializers.ValidationError({"items": "Mỗi mặt hàng phải có thông tin sản phẩm (ID sản phẩm)."})
                    
                    GoodsReceiptNoteItem.objects.create(receipt_note=instance, **item_data)
                    
                    product_instance.quantity_on_hand += item_data['quantity']
                    product_instance.save()
                        
        instance.refresh_from_db() 
        return instance

# Goods Issue Serializers
class GoodsIssueNoteItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True) # Cho phép null để nhất quán
    product_code = serializers.CharField(source='product.code', read_only=True, allow_null=True) # Cho phép null để nhất quán
    class Meta: 
        model = GoodsIssueNoteItem
        fields = ['id', 'product', 'product_name', 'product_code', 'quantity']
        # 'product' và 'quantity' là bắt buộc khi tạo/sửa item

class GoodsIssueNoteSerializer(serializers.ModelSerializer):
    items = GoodsIssueNoteItemSerializer(many=True)
    # Hiển thị tên nhân viên, không cho client sửa trực tiếp staff_account
    staff_username = serializers.CharField(source='staff_account.tendangnhap', read_only=True) 
    # Nếu muốn gửi cả object user chi tiết hơn thì dùng UserAccountPublicSerializer
    # staff_account_details = UserAccountPublicSerializer(source='staff_account', read_only=True)


    class Meta:
        model = GoodsIssueNote
        fields = [
            'id', 'issue_code', 'issued_to', 'reason', 'issue_date',
            'staff_account', # Sẽ được gán từ context, không phải từ client khi tạo/sửa
            'staff_username', # Trường này để hiển thị
            # 'staff_account_details', # Bỏ comment nếu muốn dùng serializer chi tiết hơn
            'notes', 'created_at', 'items'
        ]
        read_only_fields = ('created_at', 'id', 
                            'staff_account', 'staff_username', #'staff_account_details',
                            'issue_code') 

    def _generate_issue_code(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        last_issue = GoodsIssueNote.objects.order_by('-id').first()
        next_id = (last_issue.id + 1) if last_issue else 1
        new_code = f"PX{timestamp}-{next_id:04d}"
        while GoodsIssueNote.objects.filter(issue_code=new_code).exists():
            next_id +=1
            new_code = f"PX{timestamp}-{next_id:04d}"
        return new_code

    def validate_items(self, items_data):
        if not items_data:
            raise serializers.ValidationError("Phiếu xuất kho phải có ít nhất một mặt hàng.")
        
        for item_data in items_data:
            product_instance = item_data.get('product') # Đây là instance Product
            if not product_instance:
                 raise serializers.ValidationError({"items": "Mỗi mặt hàng phải có thông tin sản phẩm (ID sản phẩm)."})
            
            quantity_to_issue = item_data.get('quantity', 0)
            if quantity_to_issue <= 0:
                raise serializers.ValidationError(
                    {"items": f"Số lượng xuất cho '{product_instance.name}' phải lớn hơn 0."}
                )
            
            # Khi validate, kiểm tra tồn kho hiện tại của sản phẩm
            # Lưu ý: đây là tồn kho tại thời điểm validate, có thể thay đổi trước khi vào transaction.
            # Việc kiểm tra lại trong transaction (ở create/update) là cần thiết cho các hệ thống có độ tương tranh cao.
            if product_instance.quantity_on_hand < quantity_to_issue:
                raise serializers.ValidationError(
                    {"items": f"Không đủ số lượng tồn cho '{product_instance.name}'. Hiện có: {product_instance.quantity_on_hand}, Cần xuất: {quantity_to_issue}."}
                )
        return items_data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        staff_account_id = self.context.get('staff_account_id')

        if not staff_account_id:
            raise serializers.ValidationError("Thiếu thông tin nhân viên thực hiện (staff_account_id).")
        try:
            staff = UserAccount.objects.get(pk=staff_account_id, is_active=True)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError("Nhân viên thực hiện không hợp lệ hoặc không hoạt động.")
        
        validated_data['staff_account'] = staff
        validated_data['issue_code'] = self._generate_issue_code()

        with transaction.atomic():
            # Kiểm tra lại tồn kho của tất cả sản phẩm một lần nữa bên trong transaction
            for item_data_check in items_data:
                product = Product.objects.select_for_update().get(pk=item_data_check['product'].pk) # Khóa dòng để đọc
                quantity_to_issue = item_data_check['quantity']
                if product.quantity_on_hand < quantity_to_issue:
                    raise serializers.ValidationError(
                        f"Không đủ số lượng tồn kho cho '{product.name}' tại thời điểm tạo phiếu. "
                        f"Hiện có: {product.quantity_on_hand}, Cần xuất: {quantity_to_issue}."
                    )
            
            issue_note = GoodsIssueNote.objects.create(**validated_data)
            for item_data in items_data:
                product = Product.objects.select_for_update().get(pk=item_data['product'].pk) # Khóa dòng để cập nhật
                quantity = item_data['quantity']
                
                GoodsIssueNoteItem.objects.create(issue_note=issue_note, **item_data)
                
                product.quantity_on_hand -= quantity
                product.save()
        return issue_note

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Không cho phép cập nhật staff_account hoặc issue_code qua API update
        validated_data.pop('staff_account', None)
        validated_data.pop('issue_code', None)

        # Cập nhật các trường của instance GoodsIssueNote
        instance.issued_to = validated_data.get('issued_to', instance.issued_to)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.issue_date = validated_data.get('issue_date', instance.issue_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save() # Lưu các thay đổi của phiếu chính

        if items_data is not None: # Nếu client có gửi danh sách items để cập nhật
            with transaction.atomic():
                # 1. Hoàn trả tồn kho (CỘNG LẠI) cho tất cả các item cũ của phiếu này
                old_items_product_quantities = {}
                for old_item in instance.items.all():
                    old_items_product_quantities[old_item.product_id] = old_items_product_quantities.get(old_item.product_id, 0) + old_item.quantity
                
                for product_id, total_quantity in old_items_product_quantities.items():
                    try:
                        # Khóa dòng để cập nhật
                        product_to_revert = Product.objects.select_for_update().get(id=product_id)
                        product_to_revert.quantity_on_hand += total_quantity
                        product_to_revert.save()
                    except Product.DoesNotExist:
                        # Ghi log nếu sản phẩm không tồn tại (lạ)
                        print(f"Cảnh báo: Sản phẩm ID {product_id} không tồn tại khi hoàn trả tồn kho cho phiếu xuất ID {instance.id}.")
                        pass 

                # 2. Xóa tất cả các item cũ của phiếu
                instance.items.all().delete()

                # 3. Tạo các item mới từ items_data và TRỪ đi tồn kho cho chúng
                # Kiểm tra lại tồn kho của tất cả sản phẩm một lần nữa bên trong transaction trước khi tạo item mới
                for item_data_check in items_data:
                    product = Product.objects.select_for_update().get(pk=item_data_check['product'].pk) # Khóa dòng
                    quantity_to_issue = item_data_check['quantity']
                    if product.quantity_on_hand < quantity_to_issue:
                        raise serializers.ValidationError( # Ném lỗi ở đây sẽ rollback transaction
                            f"Không đủ số lượng tồn kho cho '{product.name}' khi cập nhật phiếu. "
                            f"Hiện có: {product.quantity_on_hand}, Cần xuất: {quantity_to_issue}."
                        )

                for item_data in items_data:
                    product = Product.objects.select_for_update().get(pk=item_data['product'].pk) # Khóa dòng
                    quantity = item_data['quantity']
                    
                    GoodsIssueNoteItem.objects.create(issue_note=instance, **item_data)
                    
                    product.quantity_on_hand -= quantity
                    product.save()
                    
        instance.refresh_from_db() 
        return instance