from django.db import models

# Create your models here.
class ProductTile(models.Model):
    img_src = models.URLField()
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    current_auction = models.FloatField()
    time_left = models.CharField(max_length=11)
