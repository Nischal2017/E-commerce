from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import redirect
from .models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
def index(request):
    context={}
    i=[]
    all_listings_active=AuctionItem.objects.filter(active=True)
    if request.user :
        for item in all_listings_active:
            if WatchList.objects.filter(user=request.user.id, item=item).exists():
                i.append(item.name)
    j=[]
    if request.user:
        for item in all_listings_active:
            if Bid.objects.filter(item=item).exists():
                bid_item=Bid.objects.filter(item=item).order_by('-new_bid')[0]
                if bid_item.user == request.user:
                    j.append(item.name)
    if request.user.is_authenticated:
        user= request.user.id
        if Winner.objects.filter(winning_user=user).exists():
            context['win']=True

    context["high_bids"]=j
    context["watchlist"]=i
    context["items"] = all_listings_active
    return render(request, "auctions/index.html",context)


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
        first= request.POST["first_name"]
        last= request.POST["last_name"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password,first_name=first,last_name=last)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
def create(request):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")
    if request.method=="POST":
        auction=AuctionItem()
        user_id = request.user.id
        auction.name= request.POST['name']
        auction.price=float(request.POST['price'])
        auction.description = request.POST.get('description','None')
        auction.photo=request.FILES['photo']
        auction.created_by=User.objects.get(pk=user_id)
        auction.category=request.POST['Category']
        auction.additional_description = request.POST.get(
            'additional_description','None')
        auction.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request,"auctions/create.html")
def listing(request,auction_item_id):
    context={}
    auction = AuctionItem.objects.get(pk=auction_item_id)
    context["items"] = auction
    if auction.active== False:
        return inactive_listing(request,auction)
    if request.method == "POST" and "new-bid-submit" in request.POST:
        try:
            current_highest_bid=Bid.objects.filter(item=auction).order_by('-new_bid')[0].new_bid
        except:
            current_highest_bid=0
        if float(request.POST["new-bid"]) >= float(auction.price) and float(current_highest_bid) < float(request.POST["new-bid"]):
            bid=Bid()
            bid.user= request.user
            bid.item=auction
            bid.new_bid = request.POST["new-bid"]
            bid.save()
            context['bid']=Bid.objects.filter(item=auction).order_by('-new_bid')[0]
        else:
            messages.warning(request, 'Bid must be higher than the previous bid')
    if request.user.username == auction.created_by:
        context["end"]= True
    if WatchList.objects.filter(user=request.user.id, item=auction).exists():
        context['present']=True
        if request.method =="POST" and 'remove-watchlist' in request.POST:
                watch = WatchList.objects.filter(user=request.user.id, item=auction)
                watch.delete()
                return redirect(reverse(listing, args=[auction_item_id, ]))
    elif request.method == "POST" :
        if 'add-watchlist' in request.POST:
            watch_item=WatchList()
            watch_item.user=User.objects.get(pk=request.user.id)
            watch_item.item=auction
            watch_item.save()
            return redirect(reverse(watchlist,args=[request.user.id,]))
    try:
        context['bid'] = Bid.objects.filter(item=auction).order_by('-new_bid')[0]
    except :
        context['bid']=None
    if request.method=="POST" and "close-listing" in request.POST:
        any_bids_on_item=Bid.objects.filter(item=auction).exists()
        if any_bids_on_item:
            win=Winner()
            win.item=auction
            win.winning_user = Bid.objects.filter(item=auction).order_by('-new_bid')[0].user
            win.save()
            auction.active= False
            auction.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.warning(request, 'Listing cannot be closed as no bids are placed on this listing')
            
    if Comment.objects.filter(item=auction).exists():
        context["comments"]=Comment.objects.filter(item=auction)
    if request.method == 'POST' and "comment-submit" in request.POST:
        com=Comment()
        com.author= request.user
        com.item=auction
        com.comment=request.POST['comment']
        com.rating=request.POST['rating']
        com.save()
    return render(request, "auctions/listing.html", context)
@login_required   
def watchlist(request,user_id):
    watchlist=WatchList.objects.filter(user=user_id)
    return render(request,"auctions/watchlist.html",context={
        "items":watchlist
    })
def inactive(request):
    context = {}
    i=[]
    inactive_listings=AuctionItem.objects.filter(active=False)
    for item in inactive_listings:
        if request.user.is_authenticated:
            if Winner.objects.filter(item=item,winning_user=request.user).exists():
                i.append(item.name)
    context['user_current']=i
    context["items"]=inactive_listings
    return render(request, "auctions/inactive.html", context)

def inactive_listing(request,item):
    context={}
    winner=Winner.objects.get(item=item)
    context['winner']=winner.winning_user
    context['item']=item
    context['bid'] = Bid.objects.filter(item=item).order_by('-new_bid')[0]
    return render(request,"auctions/win.html",context)
def categories(request):
    categories=["Baby","Beauty","Books","Camera & Photo","Clothing & Accessories",
                "Consumer Electronics","Grocery & Gourmet Food","Health & Personal Care",
                "Home & Garden","Industry & Scientific","Luggage & Travel Accessories",
                "Musical Instruments","Office Products","Outdoors","Personal Computers",
                "Pet Supplies","Shoes", "Handbags & Sunglasses","Software", "Sports",
                "Tools & Home Improvements", "Toys", "Video Games"]
    context={}
    context['categories']=categories
    return render(request,"auctions/categories.html",context)
def category_listings(request,category):
    context = {}
    i = []
    all_listings_active_category = AuctionItem.objects.filter(active=True,category=category)
    if request.user:
        for item in all_listings_active_category:
            if WatchList.objects.filter(user=request.user.id, item=item).exists():
                i.append(item.name)
    j = []
    if request.user:
        for item in all_listings_active_category:
            if Bid.objects.filter(item=item).exists():
                bid_item = Bid.objects.filter(
                    item=item).order_by('-new_bid')[0]
                if bid_item.user == request.user:
                    j.append(item.name)
    if request.user.is_authenticated:
        user = request.user.id
        if Winner.objects.filter(winning_user=user).exists():
            context['win'] = True

    context["high_bids"] = j
    context["watchlist"] = i
    context["items"] = all_listings_active_category
    context["category_present"]=True
    context["category"]= category
    return render(request, "auctions/index.html", context)
