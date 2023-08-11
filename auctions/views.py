from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listings, Comments, Bid

@login_required(login_url='/login')
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.filter(isactive=True).order_by("-date")
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


@login_required(login_url='/login')
def my_listings(request):

    # Created a set listing user had placed bid(s)
    bid_listings = set()

    # Loop thorugh all the bid
    for bid_object in Bid.objects.all():

        # Check if the current user have placed bid(s)
        if request.user == bid_object.buyer:

            # Append listing to the set list of listing that current user have placed a bid before
            bid_listings.add(bid_object.listing)

    # Render myListings page
    return render(request, "auctions/myListings.html", {
        "bid_listings": bid_listings,
        "owner_listings": Listings.objects.filter(owner=request.user).order_by("-date")
    })


@login_required(login_url='/login')
def create_listing(request):

    # Check if the request if POST method
    if request.method == "POST":

        # Get the user
        current_user = request.user

        # Get the data user want to post to server
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        image_url = request.POST["image_url"]
        category = Category.objects.get(label=request.POST["category"]) if request.POST["category"] else None

        # Create the new listing then save it
        new_listing = Listings(
            title=title,
            description=description,
            price=price,
            image_url=image_url,
            category=category,
            owner=current_user
        )
        new_listing.save()

        # Redirect to the listing page
        return HttpResponseRedirect(reverse("index"))

    # Otherwise, the request method is GET
    else:

        # Render the create listing page
        return render(request, "auctions/createListing.html", {
            "categories": Category.objects.all()
        })


@login_required(login_url='/login')
def categories(request):

    # Check if the request method is POST
    if request.method == "POST":

        # Get the category
        category = Category.objects.get(label=request.POST["category"])

        # Render index page with all listings with the specific category
        return render(request, "auctions/index.html", {
            "listings": Listings.objects.filter(isactive=True, category=category),
            "categories": Category.objects.all()
        })

    # Otherwise, the request method is GET
    else:

        # Render categories page
        return render(request, "auctions/categories.html", {
            "categories": Category.objects.all()
        })


@login_required(login_url='/login')
def listings(request, id):

    # Get the listing with id
    listing = Listings.objects.get(pk=id)

    # Check if listing is in watchlist of current user
    iswatchlist = request.user in listing.watchlist.all()

    # Get all the comments of the listing
    comments = Comments.objects.filter(listing=listing)

    # Check if the current user is owner of listing
    isowner = request.user == listing.owner

    # Check how many bids had been placed
    bid_counter = Bid.objects.filter(listing=listing).count()

    # Check the current highest bid
    highest_bid = Bid.objects.filter(listing=listing).order_by("-bid").first()

    # No winner yet
    winner = None

    # Check if there is one
    if highest_bid:

        # Check if the listing is closed
        if not listing.isactive:

            # Get the winner of the listing
            winner = highest_bid.buyer

        # Check the owner of the bid
        if highest_bid.buyer == request.user:

            # Give the message about the current highest bid
            bid_message = "Your bid is the current highest bid"

        # Otherwise display the name of person who has the highest bid
        else:

            # Give the message about the current highest bid
            bid_message = "Highest bid placed by " + highest_bid.buyer.username

    # If there is no one
    else:

        # No message deliver
        bid_message = None

    # Render listings page
    return render(request, "auctions/listings.html", {
            "listing": listing,
            "iswatchlist": iswatchlist,
            "comments": comments,
            "isowner": isowner,
            "bid_counter": bid_counter,
            "bid_message": bid_message,
            "winner": winner
        })


@login_required(login_url='/login')
def add_watchlist(request, id):

    # Get the listing with id
    listing = Listings.objects.get(pk=id)

    # Add the listing to the current user watchlist
    listing.watchlist.add(request.user)

    # Redirect back to listings page
    return HttpResponseRedirect(reverse("listings", args=(id, )))


@login_required(login_url='/login')
def remove_watchlist(request, id):

    # Get the listing with id
    listing = Listings.objects.get(pk=id)

    # Remove the listing from current user watchlist
    listing.watchlist.remove(request.user)

    # Redirect back to listings page
    return HttpResponseRedirect(reverse("listings", args=(id, )))


@login_required(login_url='/login')
def display_watchlist(request):

    # Get the current user
    current_user = request.user

    # Query all listing in watchlist of current user
    listings = current_user.watchlist.all()

    # Render page to display watchlist
    return render(request, "auctions/displayWatchlist.html", {
        "listings": listings
    })


@login_required(login_url='/login')
def add_comments(request, id):

    # Check the request method
    if request.method == "POST":

        # Check the request data user post
        if not request.POST["new_comment"]:

            # Redirect back to listings page
            return HttpResponseRedirect(reverse("listings", args=(id, )))

        # Create new comment object for new comment
        new_comment = Comments(
            author=request.user,
            listing=Listings.objects.get(pk=id),
            message=request.POST["new_comment"]
        )

        # Save new comment object
        new_comment.save()

        # Redirect back to listings page
        return HttpResponseRedirect(reverse("listings", args=(id, )))


@login_required(login_url='/login')
def add_bid(request, id):

    # Check the request method
    if request.method == "POST":

        # Check the request method data user post
        if not request.POST["bid"]:

            # Redirect back to listings page
            return HttpResponseRedirect(reverse("listings", args=(id, )))

        # Get the bid from user
        bid = float(request.POST["bid"])

        # Get the current listing
        listing = Listings.objects.get(pk=id)

        # Check if listing is in watchlist of current user
        iswatchlist = request.user in listing.watchlist.all()

        # Get all the comments of the listing
        comments = Comments.objects.filter(listing=listing)

        # Check if the current user is owner of listing
        isowner = request.user == listing.owner

        # Check how many bids had been placed
        bid_counter = Bid.objects.filter(listing=listing).count()

        # Check the current highest bid
        highest_bid = Bid.objects.filter(listing=listing).order_by("-bid").first()

        # Check if there is one
        if highest_bid:

            # Check the owner of the bid
            if highest_bid.buyer == request.user:

                # Give the message about the current highest bid
                bid_message = "Your bid is the current highest bid"

            # Otherwise display the name of person who has the highest bid
            else:

                # Give the message about the current highest bid
                bid_message = "Highest bid placed by " + highest_bid.buyer.username

        # If there is no one
        else:

            # No message deliver
            bid_message = None

        # Compare the bid with the current bid
        if bid > listing.price:

            # Update the new bid
            new_bid = Bid(
                bid=bid,
                buyer=request.user,
                listing=listing
            )

            # Save the new bid object
            new_bid.save()

            # Update new bid for the listing
            listing.price = bid

            # Save the listing changes
            listing.save()

            # Check how many bids had been placed
            bid_counter = Bid.objects.filter(listing=listing).count()

            # Check the current highest bid
            highest_bid = Bid.objects.filter(listing=listing).order_by("-bid").first()

            # Check if there is one
            if highest_bid:

                # Check the owner of the bid
                if highest_bid.buyer == request.user:

                    # Give the message about the current highest bid
                    bid_message = "Your bid is the current highest bid"

                # Otherwise display the name of person who has the highest bid
                else:

                    # Give the message about the current highest bid
                    bid_message = "Highest bid placed by " + highest_bid.buyer.username

            # If there is no one
            else:

                # No message deliver
                bid_message = None

            # Render listings page
            return render(request, "auctions/listings.html", {
                    "listing": listing,
                    "updated": True,
                    "message": "Bid was placed successfully!",
                    "iswatchlist": iswatchlist,
                    "comments": comments,
                    "isowner": isowner,
                    "bid_counter": bid_counter,
                    "bid_message": bid_message
                })

        # Otherwise, bid was failed to be placed
        else:
            # Render listings page
            return render(request, "auctions/listings.html", {
                    "listing": listing,
                    "updated": False,
                    "message": "Bid was failed to be placed!",
                    "iswatchlist": iswatchlist,
                    "comments": comments,
                    "isowner": isowner,
                    "bid_counter": bid_counter,
                    "bid_message": bid_message
                })


@login_required(login_url='/login')
def close_listing(request, id):

    # Get the listing
    listing = Listings.objects.get(pk=id)

    # Change the status of listing to inactive
    listing.isactive = False

    # Save the changes
    listing.save()

    # Check if listing is in watchlist of current user
    iswatchlist = request.user in listing.watchlist.all()

    # Get all the comments of the listing
    comments = Comments.objects.filter(listing=listing)

    # Check if the current user is owner of listing
    isowner = request.user == listing.owner

    # Check how many bids had been placed
    bid_counter = Bid.objects.filter(listing=listing).count()

    # Check the current highest bid
    highest_bid = Bid.objects.filter(listing=listing).order_by("-bid").first()

    # No winner yet
    winner = None

    # Check if there is one
    if highest_bid:

        # Check if the listing is closed
        if not listing.isactive:

            # Get the winner of the listing
            winner = highest_bid.buyer

        # Check the owner of the bid
        if highest_bid.buyer == request.user:

            # Give the message about the current highest bid
            bid_message = "Your bid is the current highest bid"

        # Otherwise display the name of person who has the highest bid
        else:

            # Give the message about the current highest bid
            bid_message = "Highest bid placed by " + highest_bid.buyer.username

    # If there is no one
    else:

        # No message deliver
        bid_message = None

    # Render listings page
    return render(request, "auctions/listings.html", {
            "listing": listing,
            "iswatchlist": iswatchlist,
            "comments": comments,
            "isowner": isowner,
            "bid_counter": bid_counter,
            "bid_message": bid_message,
            "winner": winner
        })

