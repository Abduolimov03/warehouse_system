from django.contrib import admin
from .models import Warehouse, Product, Employee, EmployeeInventory, ProductLog


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_central', 'address')
    list_filter = ('is_central',)
    search_fields = ('name', 'address')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'quantity', 'warehouse')
    search_fields = ('name', 'code')
    list_filter = ('warehouse',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'warehouse')


@admin.register(EmployeeInventory)
class EmployeeInventoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'product', 'date_added')


@admin.register(ProductLog)
class ProductLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'action', 'quantity', 'timestamp')
    list_filter = ('action',)
