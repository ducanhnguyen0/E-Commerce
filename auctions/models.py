from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    label = models.CharField(max_length=64)

    def __str__(self):
        return self.label

class Listings(models.Model):
    title = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="category")
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    price = models.FloatField(default=0)
    isactive = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    bid = models.FloatField(default=0)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="buyer")
    date = models.DateTimeField(auto_now_add=True, null=True)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, null=True, related_name="bid_listing")

    def __str__(self):
        return f"{self.buyer} placed a bid {self.bid} for {self.listing}"

class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="author")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, null=True, related_name="listing")
    message = models.CharField(max_length=256, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"