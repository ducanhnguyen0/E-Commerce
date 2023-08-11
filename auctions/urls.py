from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("listings/<int:id>", views.listings, name="listings"),
    path("remove_watchlist/<int:id>", views.remove_watchlist, name="remove_watchlist"),
    path("add_watchlist/<int:id>", views.add_watchlist, name="add_watchlist"),
    path("display_watchlist", views.display_watchlist, name="display_watchlist"),
    path("add_comments/<int:id>", views.add_comments, name="add_comments"),
    path("add_bid/<int:id>", views.add_bid, name="add_bid"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
    path("my_listings", views.my_listings, name="my_listings")
]
