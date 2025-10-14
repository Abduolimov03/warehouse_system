from django.db import models
from django.contrib.auth.models import User


class Warehouse(models.Model):
    name = models.CharField(max_length=120)
    is_central = models.BooleanField(blank=True, null=True)
    address = models.CharField(max_length=120)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.OneToOneField(Warehouse, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class EmployeeInventory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'product')

    def __str__(self):
        return f"{self.employee.user.username} - {self.product.name}"