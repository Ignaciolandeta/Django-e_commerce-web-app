from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("create-listing", views.create_listing, name="create-listing"),    
    path("watchlist", views.watchlist, name="watchlist"),
    path("add-remove-watchlist/<int:listing_id>", views.add_remove_watchlist, name="add-remove-watchlist"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("listing-categories", views.listing_categories, name="listing-categories"),
    path("category/<str:category>", views.category, name="category"),
    path("close-listing/<int:listing_id>", views.close_listing, name="close-listing"),
    path("logout", views.logout_view, name="logout"),

]
