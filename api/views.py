# api/views.py
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from .models import *
from django.db import transaction
from .serializers import *
from .permissions import *
from django.utils import timezone
from datetime import timedelta, date # Thêm date
from django.db.models import Count # Thêm Count
from django.db.models.functions import TruncDate # Thêm TruncDate
from rest_framework.views import APIView # Thêm APIView
from rest_framework.response import Response
from .permissions import IsAuthenticatedCustom # Giữ nguyên permission
from .models import GoodsReceiptNote, GoodsIssueNote

# JWT imports (chỉ cần cho việc tạo token)
import jwt
from datetime import timedelta
from django.conf import settings # Để lấy SECRET_KEY

def generate_jwt_token_for_user(user_account):
    """Hàm helper để tạo JWT token cho một UserAccount."""
    access_token_payload = {
        'user_account_id': user_account.id, # Quan trọng: claim để định danh user
        'tendangnhap': user_account.tendangnhap,
        'is_admin': user_account.is_admin,
        'exp': timezone.now() + timedelta(minutes=60), # Thời gian hết hạn access token
        'iat': timezone.now(),
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

    refresh_token_payload = {
        'user_account_id': user_account.id,
        'exp': timezone.now() + timedelta(days=7), # Thời gian hết hạn refresh token
        'iat': timezone.now(),
        # Thêm một claim để phân biệt refresh token, ví dụ: 'token_type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return {'access': access_token, 'refresh': refresh_token}


class UserAccountRegisterViewAPI(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountRegisterSerializer
    permission_classes = [permissions.AllowAny] # Ai cũng có thể đăng ký

class UserAccountLoginViewAPI(generics.GenericAPIView):
    serializer_class = UserAccountLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tendangnhap = serializer.validated_data['tendangnhap']
        matkhau_raw = serializer.validated_data['matkhau']

        try:
            user = UserAccount.objects.get(tendangnhap=tendangnhap)
        except UserAccount.DoesNotExist:
            return Response({"detail": "Tên đăng nhập hoặc mật khẩu không chính xác."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(matkhau_raw):
            return Response({"detail": "Tên đăng nhập hoặc mật khẩu không chính xác."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "Tài khoản này chưa được kích hoạt."}, status=status.HTTP_403_FORBIDDEN)

        # Cập nhật last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        tokens = generate_jwt_token_for_user(user)
        user_data = UserAccountPublicSerializer(user).data
        
        return Response({
            **tokens, # 'access': ..., 'refresh': ...
            'user': user_data
        })

class UserAccountProfileViewAPI(generics.RetrieveAPIView):
    serializer_class = UserAccountPublicSerializer
    permission_classes = [IsAuthenticatedCustom] # Dùng custom permission

    def get_object(self):
        # IsAuthenticatedCustom đã gán user_account vào request
        return self.request.user_account

class TokenRefreshViewAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny] # Ai cũng có thể thử refresh

    def post(self, request, *args, **kwargs):
        refresh_token_from_request = request.data.get('refresh')
        if not refresh_token_from_request:
            return Response({'detail': 'Refresh token là bắt buộc.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(refresh_token_from_request, settings.SECRET_KEY, algorithms=['HS256'])
            user_account_id = payload.get('user_account_id')
            # (Tùy chọn) Kiểm tra xem token có phải là refresh token không (dựa trên claim 'token_type' nếu có)

            user = UserAccount.objects.get(pk=user_account_id, is_active=True)
            
            # Tạo access token mới
            new_access_token_payload = {
                'user_account_id': user.id,
                'tendangnhap': user.tendangnhap,
                'is_admin': user.is_admin,
                'exp': timezone.now() + timedelta(minutes=60),
                'iat': timezone.now(),
            }
            new_access_token = jwt.encode(new_access_token_payload, settings.SECRET_KEY, algorithm='HS256')
            
            return Response({'access': new_access_token})

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Refresh token đã hết hạn.'}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, UserAccount.DoesNotExist, Exception) as e:
            return Response({'detail': f'Refresh token không hợp lệ: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)


# ViewSet cho UserAccount (chỉ admin xem/sửa được)
class UserAccountViewSetAPI(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountPublicSerializer
    permission_classes = [IsAuthenticatedCustom, IsAdminUserCustom] 

    def get_permissions(self):
        """
        Chỉ admin (UserAccount.is_admin) mới có quyền thực hiện các action nguy hiểm.
        Người dùng thường chỉ có thể xem (list, retrieve) nếu được cho phép.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Kiểm tra request.user_account.is_admin
            # Cần đảm bảo IsAuthenticatedCustom đã chạy và gán request.user_account
            # Trả về một permission class kiểm tra is_admin
            class IsUserAccountAdmin(permissions.BasePermission):
                def has_permission(self, request, view):
                    return hasattr(request, 'user_account') and request.user_account.is_admin
            return [IsAuthenticatedCustom(), IsUserAccountAdmin()]
        return super().get_permissions()
    
    # Nếu muốn cho phép người dùng tự cập nhật thông tin của họ (không phải is_admin, is_active)
    # thì cần logic phức tạp hơn trong `update` và `partial_update`.


# --- Các ViewSet khác ---
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all().order_by('name')
    serializer_class = ProductCategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedCustom()] 
        return [IsAuthenticatedCustom(), IsAdminUserCustom()] 

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all().order_by('name')
    serializer_class = UnitSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedCustom()]
        return [IsAuthenticatedCustom(), IsAdminUserCustom()]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedCustom()]
        return [IsAuthenticatedCustom(), IsAdminUserCustom()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'unit').all().order_by('name')
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedCustom()]
        return [IsAuthenticatedCustom(), IsAdminUserCustom()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        code = self.request.query_params.get('code')
        category_id = self.request.query_params.get('category_id')
        if name: queryset = queryset.filter(name__icontains=name)
        if code: queryset = queryset.filter(code__icontains=code)
        if category_id: queryset = queryset.filter(category_id=category_id)
        return queryset

class GoodsReceiptNoteViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceiptNote.objects.select_related('supplier', 'staff_account').prefetch_related('items__product__unit', 'items__product__category').all().order_by('-receipt_date', '-created_at')
    serializer_class = GoodsReceiptNoteSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticatedCustom(), IsAdminUserCustom()] # Only admins can update/delete
        # For 'create', 'list', 'retrieve', any authenticated user can perform
        return [IsAuthenticatedCustom()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request, 'user_account'):
            context['staff_account_id'] = self.request.user_account.id
        return context
    
    # perform_create không cần nữa nếu serializer.create đã lo việc gán staff và receipt_code

    # perform_update cũng không cần gán gì đặc biệt nếu serializer.update xử lý
    # việc không cho sửa staff, receipt_code và logic items.

    def perform_destroy(self, instance):
        with transaction.atomic():
            for item in instance.items.all():
                product = item.product
                product.quantity_on_hand -= item.quantity
                if product.quantity_on_hand < 0:
                    # Ghi log hoặc xử lý trường hợp tồn kho âm (không nên xảy ra)
                    product.quantity_on_hand = 0 
                product.save()
            instance.delete()
    
    # perform_create không cần nữa vì serializer tự lấy staff_account_id từ context

class GoodsIssueNoteViewSet(viewsets.ModelViewSet):
    queryset = GoodsIssueNote.objects.select_related('staff_account').prefetch_related('items__product__unit', 'items__product__category').all().order_by('-issue_date', '-created_at')
    serializer_class = GoodsIssueNoteSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticatedCustom(), IsAdminUserCustom()] # Only admins can update/delete
        return [IsAuthenticatedCustom()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request, 'user_account'): # Từ IsAuthenticatedCustom
            context['staff_account_id'] = self.request.user_account.id
        return context
    
    # perform_create không cần nữa nếu serializer.create đã lo việc gán staff và issue_code

    def perform_destroy(self, instance):
        with transaction.atomic():
            for item in instance.items.all():
                product = item.product # Đây là instance Product từ item
                # Khóa dòng để cập nhật, đảm bảo đọc và ghi là atomic cho từng sản phẩm
                product_to_update = Product.objects.select_for_update().get(pk=product.pk)
                product_to_update.quantity_on_hand += item.quantity # Cộng lại số lượng đã xuất
                product_to_update.save()
            instance.delete()
            
            
            
class InventoryChartDataView(APIView):
    permission_classes = [IsAuthenticatedCustom, IsAdminUserCustom]

    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'week')
        end_date = timezone.now().date()
        if period == 'month':
            start_date = end_date - timedelta(days=29)
        else:
            start_date = end_date - timedelta(days=6)

        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        
        receipts_data = GoodsReceiptNote.objects.filter(
            receipt_date__gte=start_date,
            receipt_date__lte=end_date
        ).annotate(
            day=TruncDate('receipt_date')
        ).values(
            'day'
        ).annotate(
            count=Count('id')
        ).order_by('day')

        issues_data = GoodsIssueNote.objects.filter(
            issue_date__gte=start_date,
            issue_date__lte=end_date
        ).annotate(
            day=TruncDate('issue_date')
        ).values(
            'day'
        ).annotate(
            count=Count('id')
        ).order_by('day')

        receipts_map = {item['day']: item['count'] for item in receipts_data}
        issues_map = {item['day']: item['count'] for item in issues_data}
        
        chart_data = []
        for dt in all_dates:
            chart_data.append({
                'date': dt.strftime('%Y-%m-%d'),
                'receipt_count': receipts_map.get(dt, 0),
                'issue_count': issues_map.get(dt, 0)
            })
        
        return Response(chart_data)