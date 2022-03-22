from audioop import reverse
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

BACKEND_URL = "http://127.0.0.1:8000/"  # Subject to change

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
        primary_color = request.POST["primary_color"]
        size = request.POST["size"]

        criteria = {
            "gender": gender,
            "brand": brand,
            "category": category,
            "primary_color": primary_color,
            "size": size,
        }

        for c in criteria.keys():
            if criteria[c] == "Any":
                criteria[c] = "NULL"

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

    return render(request, "product_view.html", {"listing_id": pk})


@login_required
def search_results(request, pk):
    request_vals = pk.split(",")
    context = {}
    for key_pair in request_vals:
        val_to = key_pair.find("=")
        context[key_pair[0:val_to]] = key_pair[val_to + 1 :]

    products = search_db(context)

    products_objs = []

    print(products)

    # for product in products:
    #     print(type(product))
    #     products_objs.append(
    #         Product(
    #             username=product["username"],
    #             image=product["image"],
    #             category=product["category"],
    #             item=product["item"],
    #             price=product["price"],
    #             listtime=product["listtime"],
    #             timelimit=product["timelimit"],
    #             gender=product["gender"],
    #             brand=product["brand"],
    #             size=product["size"],
    #             _id=product["_id"],
    #         )
    #     )

    if request.method == "POST":
        ID = request.POST["Listing_ID"]
        return redirect(f"/product/{ID}")
    else:
        return render(request, "search_results.html", {"products": products})


@login_required
def profile(request):
    return render(request, "profile.html")


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


def search_db(criteria):
    url_params = ""
    url = BACKEND_URL + "listing/" + url_params
    r = requests.get(url)
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
