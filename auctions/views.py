from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from .models import User


def index(request):
    # The index view returns a index.html template.
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=True)
    })


def login_view(request):
    # The login_view view renders a login form when a user tries to GET the page. When a user submits the form using the POST request method, the user is authenticated, logged in, and redirected to the index page.
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Your username and/or password is not valid."
            })
    else:
        return render(request, "auctions/login.html")



def register(request):
    # The register route displays a registration form to the user, and creates a new user when the form is submitted
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already exists."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def logout_view(request):
    # The logout_view view logs the user out and redirects them to the index page.
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Create Listing: Users should be able to visit a page (/create-listing.html) to create a new listing. They should be able to specify a title for the listing, a text-based description, and what the starting bid should be. Users should also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.).
@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        # Listing item variables; 
        user = request.user
        title = request.POST["title"].title()
        description = request.POST["description"]
        price = float(request.POST["price"])
        category = request.POST["category"].capitalize()
        photo = request.POST["photo"]

        # creates and save in database any new listing item with variables detalied above;
        listing = Listing(user=user, title=title, price=price, description=description, photo=photo, category=category)
        listing.save()

        # add new listing to user creator´s watchlist
        user.watchlist.add(listing)

        messages.add_message(request, messages.INFO, 'Congratulations the Listing was succesfullly created :)', extra_tags='alert alert-primary')
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    return render(request, "auctions/create-listing.html")

# Listing Page: Clicking on a listing should take users to a page specific to that listing. On that page, users should be able to view all details about the listing, including the current price for the listing.
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id) # get by listing_id
    listing_creator = listing.user #listing_id user creator 
    user = request.user
    bids = listing.bids.all() #show bids on that listing_id
    comments = listing.comments.all() #show all comments on that listing_id

    # If user is signed in authenticated, show message if user is whether or not is Watching the item
    if request.user.is_authenticated:
        if user.watchlist.filter(pk=listing_id):
            watchlist_message = "already Watching Item"
        else:
            watchlist_message = "not Watching Item yet"

        # If the user is signed in and is the one who created the listing, the user should have the ability to “close” the auction from a button in this page 
        if user == listing_creator:
            user_is_creator = True  # create variable 'user_is_creator'
        else:
            user_is_creator = False
    
        # which makes the highest bidder the winner of the auction and makes the listing no longer active.
        if bids:
            max_bid = bids.latest('price')
        else:
            max_bid = None
    
        return render(request, "auctions/listing.html",{
            "listing": listing,
            "watchlist_message": watchlist_message,
            "bids": bids,
            "comments": comments,
            "user_is_creator": user_is_creator,
            "max_bid": max_bid
        })
    else:
        return render(request, "auctions/listing.html", {
        "listing": listing
    })

# If the user is signed in, the user should be able to add the item to their “Watchlist.” If the item is already on the watchlist, the user should be able to remove it.
@login_required(login_url='login')
def add_remove_watchlist(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id) # get listing_id uer items
    if user.watchlist.filter(pk=listing_id):
        user.watchlist.remove(listing) # user can remove item from watchlist
    else:
        user.watchlist.add(listing) # user can add item to watchlist

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

# Watchlist: Users who are signed in should be able to visit a Watchlist page, which should display all of the listings that a user has added to their watchlist. Clicking on any of those listings should take the user to that listing’s page.
def watchlist(request):
    user = request.user
    watchlist = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


# If the user is signed in, the user should be able to bid on the item. The bid must be at least as large as the starting bid, and must be greater than any other bids that have been placed (if any). If the bid doesn’t meet those criteria, the user should be presented with an error.
def bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id) #define 'listing' variable from listing_id
        bidder = request.user #define 'bidder' variable from post user
        price = float(request.POST["price"]) #define 'price' varaible from bidding Form at /listing.html
        
        bidder.watchlist.add(listing) #if the user Bids on one item, this is added to his/her watchlist

        #if first bid, the bid must be at least as large as the starting bid
        if listing.bids.count() == 0:
            bid = Bid(listing=listing, price=price, bidder=bidder) #new bid object
            listing.price = float(listing.price) #convert price to float
            if bid.price >= listing.price: # the bid must be at least as large as the starting bid
                listing.price = bid.price #if yes, the greater bid is the new price (next bids should be higher)
                listing.save()
                bid.save()

                messages.add_message(request, messages.INFO, 'Your bid is valid, good luck!', extra_tags='alert alert-primary')
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                messages.add_message(request, messages.INFO, 'Your bid should be higher', extra_tags="alert alert-warning")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

        # if bid is != 0 (not the first), must be greater than any other bids that have been placed
        else:
            bid = Bid(listing=listing, price=price, bidder=bidder) #new bid object
            if bid.price > listing.price:
                listing.price = bid.price
                listing.save()
                bid.save()

                messages.add_message(request, messages.INFO, 'Your bid is valid, good luck!', extra_tags='alert alert-primary')
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                messages.add_message(request, messages.INFO, 'Your bid should be higher', extra_tags="alert alert-warning")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



# Users who are signed in should be able to add comments to the listing page. The listing page should display all comments that have been made on the listing.
@login_required(login_url='login')
def comment(request, listing_id):
    if request.method == "POST":
        comment_text = request.POST["comment_text"] #create variable ´comment' with posted comment text by the user in listing.html
        user = request.user
        listing = Listing.objects.get(pk=listing_id)

        comment = Comment(user=user, comment=comment_text, listing=listing) #new comment object
        comment.save() #save the comment in models.py

        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



# Categories: Users should be able to visit a page that displays a list of all listing categories. (e.g. Fashion, Toys, Electronics, Home, etc.).
def listing_categories(request):
    categories = [] #create category list
    listings = Listing.objects.filter(status=True).exclude(category="") #all items with any category asigned, excluded those empty

    for listing in listings: # for loop to add each listing in the catgories list (if not already included)
        if listing.category not in categories:
            categories.append(listing.category)

    return render(request, "auctions/listing-categories.html",{
        "categories": categories
    })

# Clicking on the name of any category should take the user to a page that displays all of the active listings in that category.
def category(request, category):
    listings = Listing.objects.filter(category=category, status=True) # items with that 'category'
    return render(request, "auctions/category.html",{
        "listings": listings,
        "category": category
    })



# If the user is signed in and is the one who created the listing, the user should have the ability to “close” the auction from this page, which makes the highest bidder the winner of the auction and makes the listing no longer active.
def close_listing(request, listing_id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk=listing_id)
        listing_creator = listing.user

        if user == listing_creator: # checks if user is user creator and change listing status (false not available) and show closed message
            messages.add_message(request, messages.INFO, 'This auction is closed, congratulations!', extra_tags='alert alert-info')
            listing.status = False
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
