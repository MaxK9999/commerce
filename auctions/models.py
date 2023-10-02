from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=254)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"


class Bid(models.Model):
    pass


class Comment(models.Model):
    pass


class Category(models.Model):
    name = models.CharField(max_length=40)
    
    def __str__(self):
        return self.name


class Image(models.Model):
    img = models.ImageField(upload_to='auction_images/', null=True)


class Auction(models.Model):
    title = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=500, null=True)
    images = models.ManyToManyField(Image)
    ask_price = models.FloatField(default=0.00)  
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  blank=True, null=True, related_name='user')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name='category')
    
    def __str__(self):
        return self.title