# api/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication # Để giải mã token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import UserAccount # Model UserAccount của bạn
import jwt # Thư viện pyjwt

# Tạm thời bỏ qua SIMPLE_JWT settings và sử dụng SECRET_KEY mặc định của Django
from django.conf import settings

class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission để kiểm tra xem request có token JWT hợp lệ không
    và token đó có trỏ đến một UserAccount đang active không.
    """
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]
        try:
            # Giải mã token để lấy user_account_id
            # Lưu ý: SECRET_KEY này phải giống với khi bạn tạo token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_account_id = payload.get('user_account_id') # Claim bạn đặt khi tạo token

            if not user_account_id:
                return False

            user = UserAccount.objects.get(pk=user_account_id, is_active=True)
            request.user_account = user # Gán UserAccount vào request để view sử dụng
            return True
        except jwt.ExpiredSignatureError:
            # print("Token has expired")
            return False
        except (jwt.InvalidTokenError, UserAccount.DoesNotExist, Exception) as e:
            # print(f"Token validation error: {e}")
            return False
        
        
class IsAdminUserCustom(BasePermission):
    """
    Allows access only to admin users (UserAccount.is_admin).
    Assumes IsAuthenticatedCustom has already run and set request.user_account.
    """
    def has_permission(self, request, view):
        # Ensure user_account is attached and is an admin
        return hasattr(request, 'user_account') and request.user_account and request.user_account.is_admin
        