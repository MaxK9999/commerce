from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/close_listing", views.close_listing, name="close_listing"),
    path("previous_auctions", views.previous_auctions, name="previous_auctions"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("watchlist_page", views.watchlist_page, name="watchlist_page"),
    path("listing/<int:listing_id>/place_bid", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/add_comment", views.add_comment, name="add_comment"),
]