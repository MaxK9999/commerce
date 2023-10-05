from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, Category, Auction, Image, Bid, Comment


def index(request):
    active_listings = Auction.objects.filter(active=True).order_by('-id')
    watchlisted_auctions = []
    if request.user.is_authenticated:
        watchlisted_auctions = request.user.watchlist.all()
    context = {
        'active_listings': active_listings,
        'watchlisted_auctions': watchlisted_auctions,
        }
    
    return render(request, "auctions/index.html", context)
    

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
                "message": "Invalid username and/or password.",
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
                "message": "Passwords must match.",
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
def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        watchlisted_auctions = request.user.watchlist.all()
        context = {
            'categories': categories,
            'watchlisted_auctions': watchlisted_auctions,
            }
        return render(request, "auctions/create_listing.html", context)
    
    elif request.method == "POST":
        selected_category = request.POST.get('category')
        new_name = request.POST.get('new_category')
        
        if selected_category:
            category = Category.objects.get(id=selected_category)
        elif new_name:
            category, created = Category.objects.get_or_create(name=new_name)
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        valuta = request.POST.get('valuta')
        ask_price = request.POST.get('ask_price')
        
        listing = Auction(
            title=title, 
            description=description,
            valuta=valuta,
            ask_price=ask_price,
            category=category,
            user=request.user)
        listing.save()
        
        images = request.FILES.getlist('images')
        for image in images:
            new_image = Image(img=image)
            new_image.save()
            listing.images.add(new_image)
                
        
        return redirect('index')
    
    
@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Auction, id=listing_id)
    
    if request.user == listing.user:
        if listing.bids.count() > 0:
            highest_bid = listing.bids.order_by('-amount').first()
            highest_bid.is_winner = True
            highest_bid.save()
            
        listing.active = False
        listing.closed_at = timezone.now()
        listing.save()
        
        closed_listings = Auction.objects.filter(active=False).order_by('-closed_at')
        watchlisted_auctions = request.user.watchlist.all()
        
        return render(request, 'auctions/previous_auctions.html', {
            'closed_listings': closed_listings,
            'winner': highest_bid.user,
            'watchlisted_auctions': watchlisted_auctions
        })
    return render(request, 'auctions/index.html', {
        'listing': listing,
    })


def previous_auctions(request):
    closed_listings = Auction.objects.filter(active=False).order_by('-closed_at')
    watchlisted_auctions = []
    if request.user.is_authenticated:
        watchlisted_auctions = request.user.watchlist.all()    
    return render(request, "auctions/previous_auctions.html", {
        'closed_listings': closed_listings,
        'watchlisted_auctions': watchlisted_auctions,
    })
    
    
def listing(request, listing_id):
    listing_details = get_object_or_404(Auction, id=listing_id)
    images = listing_details.images.all()
    comments = listing_details.comments.all()
    watchlisted_auctions = []
    if request.user.is_authenticated:
        watchlisted_auctions = request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        'listing': listing_details,
        'images': images,
        'comments': comments,
        'watchlisted_auctions': watchlisted_auctions,
    })
    

@login_required
def watchlist(request, listing_id):
    auction = Auction.objects.get(pk=listing_id)
    user = request.user
    
    if auction in user.watchlist.all():
        user.watchlist.remove(auction)
    else:
        user.watchlist.add(auction)
    
    return redirect('listing', listing_id=listing_id)
    

@login_required
def watchlist_page(request):
    watchlisted_auctions = request.user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {
        'watchlisted_auctions': watchlisted_auctions
    })


@login_required
def watchlist_count(request):
    watchlisted_auctions = request.user.watchlist.all()
    return {
        'watchlisted_auctions': watchlisted_auctions
    }


@login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Auction, id=listing_id)
        bid_amount = float(request.POST.get('bid_amount'))
        highest_bid = listing.bids.aggregate(Max('amount'))['amount__max']
        watchlisted_auctions = request.user.watchlist.all()
        images = listing.images.all()
        
        if highest_bid is None or bid_amount > highest_bid:
            bid = Bid(user=request.user, listing=listing, amount=bid_amount)
            bid.save()
            listing.current_bid = bid_amount
            listing.save()
        else:
            watchlisted_auctions = request.user.watchlist.all()
            return render(request, 'auctions/listing.html', {
                'listing': listing,
                'watchlisted_auctions': watchlisted_auctions,
                'images': images,
            })
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'watchlisted_auctions': watchlisted_auctions,
        'images': images,
    })              
    

@login_required
def add_comment(request, listing_id):    
    if request.method == "POST":
        listing = get_object_or_404(Auction, id=listing_id)
        comment_text = request.POST.get('comment_text')
        
        new_comment = Comment(
            user=request.user,
            listing=listing,
            text=comment_text,
        )
        new_comment.save()
        
        return redirect('listing', listing_id=listing_id)