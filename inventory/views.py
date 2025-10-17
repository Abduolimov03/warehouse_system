from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import tempfile

from .models import Warehouse, Product, Employee, EmployeeInventory
from .serializers import WarehouseSerializer, ProductSerializer, EmployeeInventorySerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.AllowAny]



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def central(self, request):
        """Markaziy ombordagi mahsulotlarni ko‘rsatish"""
        products = Product.objects.filter(warehouse__is_central=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)



class EmployeeInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeInventorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        employee = Employee.objects.get(user=self.request.user)
        return EmployeeInventory.objects.filter(employee=employee)

    @action(detail=True, methods=['post'])
    def add(self, request, pk=None):
        """Hodim o‘z omboriga mahsulot qo‘shadi"""
        product = get_object_or_404(Product, pk=pk)
        employee = Employee.objects.get(user=request.user)

        if product.quantity <= 0:
            return Response({"detail": "Mahsulot markaziy omborda tugagan."}, status=400)

        item, created = EmployeeInventory.objects.get_or_create(employee=employee, product=product)
        if created:
            return Response({"detail": "Mahsulot muvaffaqiyatli qo‘shildi."}, status=201)
        return Response({"detail": "Bu mahsulot allaqachon mavjud."}, status=200)



class ProductLocationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        """Mahsulot joylashgan omborlarni qaytarish"""
        product = get_object_or_404(Product, pk=pk)
        warehouses = Warehouse.objects.filter(products__id=product.id).distinct()

        data = [
            {
                "warehouse": w.name,
                "address": w.address,
                "latitude": w.latitude,
                "longitude": w.longitude,
            }
            for w in warehouses
        ]
        return Response(data)



class StatisticsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Umumiy statistik ma’lumotlar"""
        total_products = Product.objects.count()
        total_quantity = Product.objects.aggregate(qty=Sum('quantity'))['qty'] or 0
        total_warehouses = Warehouse.objects.count()
        total_employees = Employee.objects.count()

        top_products = Product.objects.order_by('-quantity')[:5]
        top_products_data = [{"name": p.name, "quantity": p.quantity} for p in top_products]

        data = {
            "total_products": total_products,
            "total_quantity": total_quantity,
            "total_warehouses": total_warehouses,
            "total_employees": total_employees,
            "top_products": top_products_data,
        }
        return Response(data)




def haversine(lat1, lon1, lat2, lon2):
    """Masofa (km) hisoblash"""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def nearest_warehouse(request):
    """
    Foydalanuvchining koordinatalaridan eng yaqin omborni aniqlaydi.
    Query params: ?lat=<float>&lon=<float>
    """
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')

    if not lat or not lon:
        return Response(
            {"detail": "Iltimos, lat va lon parametrlarini yuboring. Masalan: ?lat=41.31&lon=69.28"},
            status=400
        )

    try:
        user_lat = float(lat)
        user_lon = float(lon)
    except ValueError:
        return Response({"detail": "Noto‘g‘ri koordinatalar kiritilgan."}, status=400)

    warehouses = Warehouse.objects.exclude(latitude__isnull=True, longitude__isnull=True)
    if not warehouses.exists():
        return Response({"detail": "Ombor ma’lumotlari mavjud emas."}, status=404)

    nearest = None
    min_dist = float('inf')

    for w in warehouses:
        dist = haversine(user_lat, user_lon, w.latitude, w.longitude)
        if dist < min_dist:
            nearest = w
            min_dist = dist

    return Response({
        "nearest_warehouse": nearest.name,
        "address": nearest.address,
        "latitude": nearest.latitude,
        "longitude": nearest.longitude,
        "distance_km": round(min_dist, 2)
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_locations(request, pk):
    """Mahsulot joylashuvi va masofa (xaritaga chiqarish uchun)"""
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=404)

    warehouses = Warehouse.objects.filter(products__id=product.id).distinct()
    user_lat = request.query_params.get('user_lat')
    user_lon = request.query_params.get('user_lon')

    result = []
    for w in warehouses:
        item = {
            "warehouse": w.name,
            "address": w.address,
            "latitude": w.latitude,
            "longitude": w.longitude,
        }
        if user_lat and user_lon and w.latitude and w.longitude:
            try:
                dist_km = haversine(float(user_lat), float(user_lon), float(w.latitude), float(w.longitude))
                item["distance_km"] = round(dist_km, 3)
            except ValueError:
                item["distance_km"] = None
        result.append(item)
    return Response(result)



@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def export_products_csv(request):
    """Mahsulotlar ro‘yxatini CSV formatda eksport qilish"""
    qs = Product.objects.all().values('id', 'name', 'code', 'price', 'quantity', 'warehouse__name')
    df = pd.DataFrame(list(qs))
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    df.to_csv(tmp.name, index=False)
    tmp.flush()
    return FileResponse(open(tmp.name, 'rb'), as_attachment=True, filename='products.csv')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def export_products_excel(request):
    """Mahsulotlar ro‘yxatini Excel formatda eksport qilish"""
    qs = Product.objects.all().values('id', 'name', 'code', 'price', 'quantity', 'warehouse__name')
    df = pd.DataFrame(list(qs))
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(tmp.name, index=False)
    tmp.flush()
    return FileResponse(open(tmp.name, 'rb'), as_attachment=True, filename='products.xlsx')
