from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, ProductViewSet, EmployeeInventoryViewSet, ProductLocationAPIView

router = DefaultRouter()
router.register('warehouses', WarehouseViewSet)
router.register('products', ProductViewSet)
router.register('inventory', EmployeeInventoryViewSet, basename='inventory')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('products/<int:pk>/locations/', ProductLocationAPIView.as_view(), name='product_locations'),
]
