from django.contrib import messages
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
            messages.error(request, "Username or password is incorrect.")
            return render(request, "auctions/login.html")
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
            messages.error(request, "Passwords must match!")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
        
        login(request, user)
        messages.success(request, "Registration succesfull.")
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
        
        if not title or not description or not valuta or not ask_price:
            messages.error(request, "All fields are required.")
            return redirect('create_listing')
        
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
                
        messages.success(request, "Listing created succesfully!")
        return redirect('index')
    
    
@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Auction, id=listing_id)
    highest_bid = None
    
    if request.user == listing.user:
        if listing.bids.count() > 0:
            highest_bid = listing.bids.order_by('-amount').first()
            highest_bid.is_winner = True
            highest_bid.save()
            listing.sold_price = highest_bid.amount
            listing.save()
            
        listing.active = False
        listing.closed_at = timezone.now()
        listing.save()
        
        closed_listings = Auction.objects.filter(active=False).order_by('-closed_at')
        watchlisted_auctions = request.user.watchlist.all()
        winner = highest_bid.user if highest_bid else None
        
        return render(request, 'auctions/previous_auctions.html', {
            'closed_listings': closed_listings,
            'winner': winner, #THIS LINE HAS BEEN CHANGED
            'watchlisted_auctions': watchlisted_auctions,
            'listing': listing,
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
    highest_bid = Bid.objects.filter(listing=listing_details).order_by('-amount').first()
    if request.user.is_authenticated:
        watchlisted_auctions = request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        'listing': listing_details,
        'images': images,
        'comments': comments,
        'watchlisted_auctions': watchlisted_auctions,
        'highest_bid': highest_bid,
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
            highest_bid = bid_amount
            
            messages.success(request, "Bid placed succesfully!")
            return redirect('listing', listing_id=listing_id)
        
        elif bid_amount < listing.ask_price or bid_amount <= highest_bid:
            
            messages.error(request, "Invalid bid amount.")
            return redirect('listing', listing_id=listing_id)

    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'watchlisted_auctions': watchlisted_auctions,
        'images': images,
        'highest_bid': highest_bid,
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
        
        messages.success(request, "Your comment has been placed!")
        return redirect('listing', listing_id=listing_id)
    

def categories(request):
    category_name = request.POST.get('category', '')
    categories = Category.objects.all()
    watchlisted_auctions = request.user.watchlist.all()
    
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            listings = Auction.objects.filter(category=category, active=True)
        except Category.DoesNotExist:
            listings = []
    else:
        listings = Auction.objects.filter(active=True)
                
    return render(request, "auctions/categories.html", {
        'listings': listings,
        'categories': categories,
        'selected_category': category_name,
        'watchlisted_auctions': watchlisted_auctions,
    })