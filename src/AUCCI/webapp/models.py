from django.db import models

# Create your models here.
class Product(models.Model):
    img_src = models.URLField()
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    current_auction_price = models.FloatField()
    time_created = models.CharField(max_length=11)
    auction_time_limit = models.CharField(max_length=11)
    gender = models.CharField(max_length=10)
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    listing_id = models.CharField(max_length=100)
