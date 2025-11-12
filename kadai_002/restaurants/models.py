# restaurants/models.py
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)
    representative = models.CharField(max_length=100)
    established_at = models.DateField(null=True, blank=True)
    zipcode = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    business = models.TextField()  # 事業内容
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='restaurants')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='restaurants')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurant/', blank=True, null=True)
    description = models.TextField(blank=True)
    price_min = models.IntegerField()
    price_max = models.IntegerField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    zipcode = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    tel = models.CharField(max_length=20)
    holiday = models.CharField(max_length=50, blank=True)  # 定休日
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
