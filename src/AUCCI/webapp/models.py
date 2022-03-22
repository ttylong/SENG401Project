from django.db import models

# Create your models here.
class Product(models.Model):
    username = models.CharField(max_length=100)
    image = models.URLField()
    category = models.CharField(max_length=100)
    item = models.CharField(max_length=100)
    price = models.FloatField()
    listtime = models.CharField(max_length=11)
    timelimit = models.CharField(max_length=11)
    gender = models.CharField(max_length=10)
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    _id = models.CharField(max_length=100)
