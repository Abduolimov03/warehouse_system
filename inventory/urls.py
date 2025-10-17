from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet,
    ProductViewSet,
    EmployeeInventoryViewSet,
    ProductLocationAPIView,
    product_locations,
    export_products_csv,
    export_products_excel,
    StatisticsAPIView,
    nearest_warehouse,
)

router = DefaultRouter()
router.register('warehouses', WarehouseViewSet)
router.register('products', ProductViewSet)
router.register('inventory', EmployeeInventoryViewSet, basename='inventory')

urlpatterns = [
    path('', include(router.urls)),

    # Mahsulot joylashuvlari
    path('products/<int:pk>/locations/', product_locations, name='product_locations'),

    # Statistik endpoint
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),

    # Eksportlar
    path('export/products/csv/', export_products_csv, name='export_products_csv'),
    path('export/products/xlsx/', export_products_excel, name='export_products_excel'),

    path('warehouse/nearest/', nearest_warehouse, name='nearest_warehouse'),

]
