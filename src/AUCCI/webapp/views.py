from audioop import reverse
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib import messages
from .models import Product
from pymongo import MongoClient
from django.http import JsonResponse, HttpResponse
import datetime
from django.urls import path
from django.contrib.auth.decorators import login_required
import requests
import datetime
import json

BACKEND_URL = "http://aucci.herokuapp.com/"  # Subject to change

# View Functions
def index(request):
    if request.method == "POST":
        if request.POST.get("login_s"):
            return redirect("login")
        if request.POST.get("register_s"):
            return redirect("register")
    else:
        return render(request, "index.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("search")
        else:
            messages.info(
                request, "The Username and/or Password entered are incorrect!"
            )
            return redirect("login")
    else:
        return render(request, "login.html")


def register(request):
    if request.method == "POST":
        fname = request.POST["f_name"]
        lname = request.POST["l_name"]
        username = request.POST["username"]
        password = request.POST["pass"]
        verifypass = request.POST["confirmpass"]
        email = request.POST["email"]

        if password == verifypass:
            # User is the thing being imported, filter goes in the db and checks
            # if the email entered already exists.
            if User.objects.filter(email=email).exists():
                messages.info(
                    request, "Email already in use! Please go back and log in!"
                )
                # Send em back to register
                return redirect("register")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username not available! Try a different one!")
                return redirect("register")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=fname,
                    last_name=lname,
                )
                user.save()
                return redirect("login")
        else:
            messages.info(request, "Passwords did not match!")
            return redirect("register")

    else:
        return render(request, "register.html")


@login_required
def search(request):
    if request.method == "POST":
        gender = request.POST["gender"]
        brand = request.POST["brand"]
        category = request.POST["category"]
        primary_color = request.POST["primary-color"]
        size = request.POST["size"]

        criteria = {
            "gender": gender,
            "brand": brand,
            "category": category,
            "size": size,
            "primary-color": primary_color,
        }

        for c in criteria.keys():
            if criteria[c] == "Any":
                criteria[c] = "null"

        request_vals = "search_results/"

        counter = 0

        for crit in criteria.keys():
            request_vals += f"{crit}={criteria[crit]}"
            counter += 1
            if counter != 5:
                request_vals += ","

        return redirect(request_vals)

    else:
        return render(request, "search.html")


@login_required
def product(request, pk):
    username = request.user.username

    prod = listing_by_id(pk)
    product = convert_to_products(prod)[0]

    my_listing = False

    if username == product.username:
        my_listing = True

    expired = False

    bid_id = bid_id_by_listing_id(pk)
    # highest_bid_price = highest_bid(bid_id).json()["highestbid"]

    if request.method == "POST":
        bid_price = int(request.POST["bids"])
        # listing_id = request.POST["listing_id"]
        auction_price = int(request.POST["auction_price"])

        # bid_id = bid_id_by_listing_id(listing_id)

        if bid_price > auction_price:
            bid_data_raw = {"username": request.user.username, "bid": bid_price}
            bid_price_raw = {"price": bid_price}

            bid = make_bid(bid_id, bid_data_raw)
            add_my_bids = add_my_bid(bid_id, bid_data_raw)
            update_auction_price = update_listing_price(pk, bid_price_raw)

            return redirect("search")
    return render(
        request,
        "product_view.html",
        {"product": product, "my_listing": my_listing},
    )


@login_required
def search_results(request, pk):
    if request.method == "POST":
        ID = request.POST["Listing_ID"]
        return redirect(f"/product/{ID}")
    else:
        request_vals = pk.split(",")
        context = {}
        for key_pair in request_vals:
            val_to = key_pair.find("=")
            context[key_pair[0:val_to]] = key_pair[val_to + 1 :]

        counter = 0

        for c in context.keys():
            if context[c] == "null":
                counter += 1

        if counter == 5:
            prods = search_db()
        else:
            prods = listing_by_param(context)
        products = convert_to_products(prods)
        return render(request, "search_results.html", {"products": products})


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def mylistings(request):
    username = request.user.username
    prods = listing_by_username(username)
    products = convert_to_products(prods)
    for product in products:
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        curr_time = datetime.datetime.strptime(dt_string, "%d/%m/%Y %H:%M:%S")
        if curr_time >= product.maxtime:
            product.status = "Expired"
        else:
            product.status = "Active"

    return render(request, "mylistings.html", {"products": products})


@login_required
def my_bids(request):
    username = request.user.username
    bids = bids_by_user(username)
    all_bids = json.loads(bids)

    bids_made = False

    if len(all_bids) == 0:
        return render(request, "my_bids.html", {"bids_made": bids_made})
    else: 
        bids_made = True

    winning_bids = []

    for bid in all_bids:
        highest_bid_json = highest_bid(bid["bidid"]).json()
        highest_bidder = highest_bid_json["highestbidder"]
        highest_bid_price = highest_bid_json["highestbid"]

        if highest_bidder == request.user.username:
            winning_bids.append({"bidid": bid["bidid"], "bidprice": highest_bid_price})

    prods = []

    for bid in winning_bids:
        listing_id = listing_by_bid_id(bid["bidid"])
        highest_bid_price = bid["bidprice"]
        prod = listing_by_id(listing_id)
        prods.append(
            {
                "_id": str(prod[0]),
                "username": prod[0]["username"],
                "item": prod[0]["item"],
                "brand": prod[0]["brand"],
                "category": prod[0]["category"],
                "gender": prod[0]["gender"],
                "size": prod[0]["size"],
                "listtime": str(prod[0]["listtime"]),
                "price": str(highest_bid_price),
                "image": prod[0]["image"],
                "primary-color": prod[0]["primary-color"],
                "status": "Active",
            }
        )
    products = convert_to_products(prods)
    return render(request, "my_bids.html", {"products": products, "bids_made": bids_made})


@login_required
def signout(request):
    logout(request)
    return redirect("index")


@login_required
def settings_req(request):
    if request.method == "POST":
        new_fname = request.POST["NewFName"]
        new_lname = request.POST["NewLName"]
        password_old = request.POST["password_old"]
        password_new = request.POST["password_new"]
        password_new_confirm = request.POST["password_new_confirm"]
        user = request.user
        if new_fname and new_fname.strip():
            user.first_name = new_fname
            user.save()
        if new_lname and new_lname.strip():
            user.last_name = new_lname
            user.save()
        if password_old and password_old.strip():
            if (
                password_new
                and password_new_confirm
                and password_new.strip()
                and password_new_confirm.strip()
            ):
                user = auth.authenticate(username=user.username, password=password_old)
                if user is not None:
                    if password_new == password_new_confirm:
                        user.set_password(password_new)
                        user.save()
                        messages.info(
                            request,
                            "Password successfully changed! Please log in again!",
                        )
                        return redirect("profile")
                    else:
                        messages.info(request, "New passwords do not match!")
                        return redirect("settings")
                else:
                    messages.info(request, "The current password entered is incorrect!")
                    return redirect("settings")
        return redirect("profile")
    else:
        return render(request, "settings_view.html")


@login_required
@csrf_exempt
def create_listing(request):
    username = request.user.username

    if request.method == "POST":
        item = request.POST["title"]
        brand = request.POST["brand"]
        category = request.POST["category"]
        gender = request.POST["gender"]
        size = request.POST["size"]
        price = int(request.POST["price"])
        # image = request.POST["image"]
        primary_color = request.POST["primary-color"]

        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        listing = {
            "username": username,
            "item": item,
            "brand": brand,
            "category": category,
            "gender": gender,
            "size": size,
            "listtime": dt_string,
            "price": price,
            "min_price": price + 1,
            "image": "https://i.pinimg.com/originals/04/7b/7c/047b7cb4a8ce00ab8174824e1c8625de.jpg",
            "primary-color": primary_color,
        }
        json_item = json.dumps(listing)
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        url = BACKEND_URL + "create_listing/"
        response = requests.post(url, data=json_item, headers=headers)
        listingid = response.json()["_id"]
        # url = BACKEND_URL + "create_bid_item/" + listingid + "/"
        # listing_id_raw = {"_id": listingid}
        # listing_json = json.dumps(listing_id_raw)
        # response = requests.post(url, data=listing_json, headers=headers)
        listing_id_raw = {"_id": listingid}
        create_empty_bid = create_bid(listingid, listing_id_raw)
        return redirect("mylistings")
    else:
        return render(request, "create_listing.html")


def search_db():
    url = BACKEND_URL + "listing/"
    r = requests.get(url).json()
    return r


def listing_by_username(username):
    url = BACKEND_URL + "listing_by_user/" + username + "/"
    r = requests.get(url).json()
    return r


def listing_by_param(criteria):
    url_params = ""

    for c in criteria.keys():
        url_params += criteria[c] + "/"

    url = BACKEND_URL + "listing_by_params/" + url_params
    r = requests.get(url).json()
    return r


def bids_by_user(username):
    url = BACKEND_URL + "get_my_bids/" + username + "/"
    r = requests.get(url).json()
    return r


def convert_to_products(dict_tuples):
    products = []
    for tup in dict_tuples:
        datetime_store = tup["listtime"]
        listtime_obj = datetime.datetime.strptime(datetime_store, "%d/%m/%Y %H:%M:%S")
        week = datetime.timedelta(days=7)
        target_time = listtime_obj + week
        products.append(
            Product(
                username=tup["username"],
                image=tup["image"],
                category=tup["category"],
                item=tup["item"],
                price=tup["price"],
                maxtime=target_time,
                gender=tup["gender"],
                brand=tup["brand"],
                size=tup["size"],
                product_id=tup["_id"],
                color=tup["primary-color"],
                min_price=str(float(tup["price"]) + 1),
            )
        )
    return products


def listing_by_id(oid):
    url_params = oid
    url = BACKEND_URL + "listing_by_id/" + url_params + "/"
    r = requests.get(url).json()
    return r


def listing_by_bid_id(bidid):
    url_params = bidid
    url = BACKEND_URL + "get_listing_by_bid_id/" + url_params + "/"
    r = requests.get(url).json()
    listing_id = r["listingid"]
    return listing_id


def bid_id_by_listing_id(oid):
    url_params = oid
    url = BACKEND_URL + "get_bid_id_by_listing_id/" + oid + "/"
    r = requests.get(url).json()
    bid_id = r["bidid"]
    return bid_id


def create_bid(listingid, listingiddata):
    url_params = listingid
    url = BACKEND_URL + "create_bid_item/" + url_params + "/"
    listing_id_json = json.dumps(listingiddata)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.post(url, data=listing_id_json, headers=headers)
    return r


def make_bid(bidid, biddata):
    url_params = bidid
    url = BACKEND_URL + "update_bid_item/" + url_params + "/"
    bid_json = json.dumps(biddata)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.patch(url, bid_json, headers=headers)
    return r


def add_my_bid(bidid, biddata):
    url_params = bidid
    url = BACKEND_URL + "mybids/" + url_params + "/"
    bid_json = json.dumps(biddata)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.post(url, data=bid_json, headers=headers)
    return r


def highest_bid(bidid):
    url_params = bidid
    url = BACKEND_URL + "get_highest_bidder/" + url_params + "/"
    r = requests.get(url)
    return r


def update_listing_price(oid, highestbid):
    url_params = oid
    url = BACKEND_URL + "update_listing_price/" + url_params + "/"
    price_json = json.dumps(highestbid)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.patch(url, price_json, headers=headers)
    return r


def delete_listing(oid):
    url_params = oid
    url = BACKEND_URL + "delete_listing/" + url_params + "/"
    r = requests.delete(url).json()
    return r


def helper(criteria):
    p1 = Product(
        img_src="https://cache.mrporter.com/variants/images/30629810019697407/in/w358_q60.jpg",
        listing_id="12jjasdfjw2e",
        category="Men's Jacket",
        title="Gucci Sweater",
        current_auction_price=69.98,
        time_created="23h:42m:15s",
    )
    p2 = Product(
        img_src="https://ca.louisvuitton.com/images/is/image/HKN44WUSO618_PM2_Front%20view",
        listing_id=2,
        category="Men's Sweater",
        title="LV Sweater",
        current_auction_price=122.12,
        time_created="22m:44s",
    )
    p3 = Product(
        img_src="https://i.pinimg.com/originals/04/7b/7c/047b7cb4a8ce00ab8174824e1c8625de.jpg",
        category="Men's Hoodies",
        title="OVO Hoodie",
        current_auction_price=1322.12,
        time_created="03h:22m:44s",
    )
    p4 = Product(
        img_src="https://eu.louisvuitton.com/images/is/image/HHD20WQJQ631_PM2_Front%20view",
        category="Men's Jeans",
        title="LV Jeans",
        current_auction_price=61.08,
        time_created="03h:42m:25s",
    )
    p5 = Product(
        img_src="https://cdn.shopify.com/s/files/1/2482/7148/products/Bape_Classic_Shark_Tee_BlackGrey_2048x2048.jpg?v=1567473485",
        category="Men's Shirt",
        title="Bape Shirt",
        current_auction_price=123.28,
        time_created="13h:02m:00s",
    )
    p6 = Product(
        img_src="https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1576864808/522514_Z402L_4635_001_100_0000_Light-GG-velvet-jacket.jpg",
        category="Men's Blazer",
        title="Gucci Blazer",
        current_auction_price=869.98,
        time_created="00h:00m:15s",
    )
    p7 = Product(
        img_src="https://img.ihahabags.ru/202107/s-886722-prada-sweater-long-sleeved-for-unisex.jpg",
        category="Men's Sweater",
        title="Prada Sweater",
        current_auction_price=1001.28,
        time_created="13h:42m:19s",
    )

    products = [p1, p2, p3, p4, p5, p6, p7]

    return products
