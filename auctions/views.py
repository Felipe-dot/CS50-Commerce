from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import AuctionListingForm, BidForm, CommentForm


from .models import User, AuctionListing, Category

def index(request):
    user = request.user
    listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listing_detail(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    user = request.user
    is_watching = user.is_authenticated and listing.watchlist.filter(id=user.id).exists()
    is_owner = user == listing.created_by
    is_winner = user == listing.winner

    if listing.bids.exists():
        current_price = listing.bids.order_by('-amount').first().amount
    else:
        current_price = listing.starting_bid

    if request.method == "POST":
        if 'bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                new_bid = bid_form.save(commit=False)
                new_bid.bid_by = user
                new_bid.listing = listing
                if new_bid.amount > listing.starting_bid and (not listing.bids.exists() or new_bid.amount > listing.bids.order_by('-amount').first().amount):
                    new_bid.save()
                    messages.success(request, 'Your bid was successfully placed!')
                else:
                    messages.error(request, 'Your bid must be higher than the current highest bid.')
        elif 'comment' in request.POST:
            comment_data = request.POST.getlist('comment')
            comment_form = CommentForm({'comment': comment_data[0]})
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.commented_by = user
                new_comment.listing = listing
                new_comment.save()
                messages.success(request, 'Your comment was successfully added!')
        elif 'close' in request.POST and is_owner:
            listing.is_active = False
            highest_bid = listing.bids.order_by('-amount').first()
            if highest_bid:
                listing.winner = highest_bid.bid_by
            listing.save()
            messages.success(request, 'The auction was successfully closed!')
        elif 'watch' in request.POST:
            if is_watching:
                listing.watchlist.remove(user)
                is_watching = False
                messages.success(request, 'Removed from your watchlist.')
            else:
                listing.watchlist.add(user)
                is_watching = True
                messages.success(request, 'Added to your watchlist.')
        return redirect('listing_detail', listing_id=listing.id)

    bid_form = BidForm()
    comment_form = CommentForm()
    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "is_watching": is_watching,
        "is_owner": is_owner,
        "is_winner": is_winner,
        "current_price": current_price,
    })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
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

def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            return redirect('index')
    else:
        form = AuctionListingForm()
    return render(request, "auctions/create_listing.html", {
        "form": form
    })

def category_listings_view(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    listings = AuctionListing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })

def watchlist_view(request):
    user = request.user
    if(user.is_authenticated):
        watchlist_items = user.watchlist.all()
    else:
        watchlist_items = []
    
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })