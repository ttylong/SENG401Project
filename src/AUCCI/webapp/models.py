from django.db import models

# Create your models here.
class Product(models.Model):
    username = models.CharField(max_length=100)
    image = models.CharField(max_length=1000)
    category = models.CharField(max_length=100)
    item = models.CharField(max_length=100)
    price = models.FloatField()
    listtime = models.CharField(max_length=11)
    gender = models.CharField(max_length=10)
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    product_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
