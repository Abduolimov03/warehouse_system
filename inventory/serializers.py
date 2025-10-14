from rest_framework import serializers
from .models import Warehouse, Product, EmployeeInventory, Employee

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'warehouse']


class EmployeeInventorySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = EmployeeInventory
        fields = ['id', 'employee', 'product', 'date_added']