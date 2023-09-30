from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=254)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"


class Auction(models.Model):
    pass


class Bid(models.Model):
    pass


class Comment(models.Model):
    pass