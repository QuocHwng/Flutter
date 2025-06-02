# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserAccountViewSetAPI, basename='useraccount') # basename quan trọng
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'units', UnitViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'goods-receipts', GoodsReceiptNoteViewSet)
router.register(r'goods-issues', GoodsIssueNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', UserAccountRegisterViewAPI.as_view(), name='custom_user_register'),
    path('auth/login/', UserAccountLoginViewAPI.as_view(), name='custom_user_login'),
    path('auth/profile/', UserAccountProfileViewAPI.as_view(), name='custom_user_profile'),
    path('auth/token/refresh/', TokenRefreshViewAPI.as_view(), name='custom_token_refresh'),
     path('inventory-chart-data/', InventoryChartDataView.as_view(), name='inventory_chart_data'),
]