from django.contrib import admin
from .models import Warehouse, Product, Employee, EmployeeInventory


admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(EmployeeInventory)