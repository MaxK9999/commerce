from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max
from django.utils import timezone


class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=254)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"


class Category(models.Model):
    name = models.CharField(max_length=40)
    
    def __str__(self):
        return (self.name)


class Image(models.Model):
    img = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    
    def __str__(self):
        return str(self.img)
    

class Auction(models.Model):
    title = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=500, null=True)
    images = models.ManyToManyField(Image)
    valuta = models.CharField(max_length=5, choices=[("$", "$ USD"), ("€", "€ EUR"), ("£", "£ GBP"), ("¥", "¥ JPY")], default='$')
    ask_price = models.FloatField(default=0.00)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  blank=True, null=True, related_name='user')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name='category')
    watchlist = models.ManyToManyField(User, related_name='watchlist', blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    closed_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
        
    def close(self):
        self.active =False
        self.closed_at = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
    

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None, null=True)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids', null=True)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    timestamp = models.DateTimeField(default=timezone.now)
    is_winner = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} has placed a bid of {self.listing.valuta}{self.amount} on {self.listing.title}!"
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None, null=True)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments', null=True)
    text = models.TextField(max_length=10000, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} placed a comment {self.text} on {self.listing.title}!"
