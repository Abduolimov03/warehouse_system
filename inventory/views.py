from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Warehouse, Product, Employee, EmployeeInventory
from .serializers import WarehouseSerializer, ProductSerializer, EmployeeInventorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView



class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def central(self, request):
        products = Product.objects.filter(warehouse__is_cental=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class EmployeeInventoryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeInventory.objects.all()
    serializer_class = EmployeeInventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee = Employee.objects.get(user=self.request.user)
        return EmployeeInventory.objects.filter(employee=employee)

    @action(detail=True, methods=['post'])
    def add(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        employee = Employee.objects.get(user = request.user)
        item, created = EmployeeInventory.objects.get_or_create(employee=employee, product=product)
        if created:
            return Response({"detail": "Mahsulot qo‘shildi"}, status=status.HTTP_201_CREATED)
        return Response({"detail": "Bu mahsulot allaqachon mavjud!"}, status=status.HTTP_200_OK)



class ProductLocationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        warehouses = Warehouse.objects.filter(products__name=product.name)
        data = [
            {
                'warehouse': w.name,
                'address': w.address,
                'latitude': w.latitude,
                'longitude': w.longitude,
            } for w in warehouses
        ]
        return Response(data)
