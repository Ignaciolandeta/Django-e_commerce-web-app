from django.contrib import admin
from .models import User, Listing, Bid, Comment

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "id")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "price", "date")

class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "comment", "listing")    

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)




