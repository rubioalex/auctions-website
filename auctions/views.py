from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import User, Listing, Watchlist, Bid, Comment, Category
from .forms import NewListingForm, NewComment


def index(request):
    all_listings = Listing.objects.order_by("-created_at").filter(is_closed=False)
    
    listing_watchlist_dict = {}
    if request.user.is_authenticated:
        for listing in all_listings:
            if Watchlist.objects.filter(user=request.user, listing=listing).exists():
                listing_watchlist_dict[listing.id] = True
            
    return render(request, "auctions/index.html", {
        "all_listings": all_listings,
        "listing_watchlist_dict": listing_watchlist_dict
    })
    
    
    
def closed_listings(request):
    closed_listings = Listing.objects.order_by("-created_at").filter(is_closed=True)
    
    return render(request, "auctions/closed_listings.html", {
        "closed_listings": closed_listings
    })



def login_view(request):
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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



def register(request):
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
                "message": "Username already taken."
            })
            
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/register.html")



@login_required
def createListing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            if 'image' not in request.FILES:
                default_image_url = settings.DEFAULT_LISTING_IMAGE_URL
                form.instance.image = default_image_url
            
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
                
            return redirect("detail", listing_id=listing.id)
        
        else:
            if not request.POST['starting_bid'].isdigit() or\
                int(request.POST['starting_bid']) <= 0:
                error_message = "Please enter a valid Starting Bid"

                print(form.errors)
            
    else:
        form = NewListingForm()
        error_message = None
        
    return render(request, 'auctions/create.html', {
        "form": form,
        "title": "New Listing",
        "error_message": error_message
    })
    
    
    
@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user == listing.created_by:
        listing.is_closed = True
        listing.save()
        
    return redirect("closed_listings")
    
    
    
def listingDetails(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    current_bid = Bid.objects.filter(listing=listing).order_by("-amount").first
    comments = Comment.objects.filter(listing=listing)
    form = NewComment()
    
    if request.user.is_authenticated:
        listing_in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    else:
        listing_in_watchlist = False
    
    return render(request, "auctions/detail.html", {
        "listing": listing,
        "listing_in_watchlist": listing_in_watchlist,
        "current_bid": current_bid,
        "comment_form": form,
        "comments": comments
    })
    
    
    
@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    if not Watchlist.objects.filter(user=request.user, listing=listing).exists():
        watchlist_item = Watchlist(user=request.user, listing=listing)
        watchlist_item.save()
        
    return redirect("watchlist")



@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing).first()
    if watchlist_item:
        watchlist_item.delete()
        
    return redirect("watchlist")


@login_required
def watchlist(request):
    if request.user.is_authenticated:
        watchlist_listings = Listing.objects.order_by("-created_at").filter(watchlist__user=request.user)
        
        return render(request, "auctions/watchlist.html", {
            "watchlist_listings": watchlist_listings
        })
        
        
        
@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user.is_authenticated:
        listing_in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    else:
        listing_in_watchlist = False
        
    comments = Comment.objects.filter(listing=listing)
    form = NewComment()
    
    if request.method == "POST":
        bid_amount = request.POST.get('bid_amount')
        if bid_amount:
            try:
                bid_amount = float(bid_amount)
                
                if bid_amount >= listing.starting_bid:
                    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
                    if not highest_bid or bid_amount > highest_bid.amount:
                        bid = Bid(user=request.user, listing=listing, amount=bid_amount)
                        bid.save()
                        message = "Bid placed successfully!"
                    else:
                        message = "Your bid must be higher than the current highest bid."
                else:
                    message = "Your bid must be higher than the starting bid."
            
            except ValueError:
                message = "Please enter a valid bid amount"
        
        else:
            message = "Bid amount cannot be empty."
            
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
            
    return render(request, "auctions/detail.html", {
        "message": message,
        "listing": listing,
        "listing_in_watchlist": listing_in_watchlist,
        "current_bid": highest_bid,
        "comments": comments,
        "comment_form": form
    })



@login_required
def my_items(request):
    if request.user.is_authenticated:
        my_listings = Listing.objects.filter(created_by=request.user).exclude(is_closed=True)
        return render(request, "auctions/my_items.html", {
            "listings": my_listings
        })
        
        
        
@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
        
    if request.method =="POST":
        form = NewComment(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return redirect("detail", listing_id=listing_id)
        
        
        
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
    
    
    
def listings_by_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    
    listings = Listing.objects.order_by("-created_at").filter(category=category, is_closed=False)
    
    return render(request, "auctions/listings_by_category.html", {
        "listings": listings,
        "category": category
    })