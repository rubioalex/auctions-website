from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed_listings", views.closed_listings, name="closed_listings"),
    path("<int:listing_id>/close-auction", views.close_auction, name="close_auction"),
    path("<int:listing_id>", views.listingDetails, name="detail"),
    
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.listings_by_category, name="listings_by_category"),
    
    path("create", views.createListing, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("myitems", views.my_items, name="my_items"),
    
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name="add_to_watchlist"),
    path('remove_from_watchlist/<int:listing_id>/', views.remove_from_watchlist, name="remove_from_watchlist"),
    
    path("<int:listing_id>/place-bid/", views.place_bid, name="place_bid"),
    path("<int:listing_id>/add-comment", views.add_comment, name="add_comment"),
]
