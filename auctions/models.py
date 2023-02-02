from django.contrib.auth.models import AbstractUser
from django.db import models

# Models.py is where define any models for the web application, where each model represents some type of data want to store in the database.
# Each time change anything in auctions/models.py, need to first run python manage.py makemigrations and then python manage.py migrate to migrate those changes to the database.

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watched")

def __str__(self):
    return f"{self.username} ({self.first.name} {self.last_name})"

# This application should have at least three models in addition to the User model: one for auction listings, one for bids, and one for comments made on auction listings. It’s up to you to decide what fields each model should have, and what the types of those fields should be. It may have additional models too.

# Listing Model
class Listing(models.Model):
    # type of data for 'Listing' model to be store in the database:
    # To define a many-to-one relationship, use ForeignKey. In this example, a User can be associated with many Listing objects
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    photo = models.CharField(max_length=400, blank=True)
    category = models.CharField(max_length=32, blank=True)
    status = models.BooleanField(default=True)

    
    def __str__(self): # Listing object in a String representation return:
        return f"Item:{self.title} User:{self.user} Price:{self.price} Date Listed:{self.date}"



# Model for users 'Bids' on a listing
class Bid(models.Model):
    # type of data for 'Bids' model to be store in the database:
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids") 
    price = models.DecimalField(max_digits=16, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self): # Bids object in a String representation return
        return f"Listing:{self.listing} price:{self.price}"

# Model for user 'Comments' on a listing
class Comment(models.Model):
    # type of data for 'Comment' model to be store in the database:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=300)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Date:{self.date} Comment:{self.comment} Listing:{self.listing}"


