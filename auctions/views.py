from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Auction, Image


def index(request):
    return render(request, "auctions/index.html")


@login_required
def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        context = {'categories': categories}
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
        ask_price = request.POST.get('ask_price')
        
        listing = Auction(title=title, description=description, ask_price=ask_price, category=category, user=request.user)
        listing.save()
        
        images = request.FILES.getlist('images')
        for image in images:
            new_image = Image(image=image)
            new_image.save()
            listing.images.add(new_image)
        
        return redirect('index')
    

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
