from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("product", views.product, name="product"),
    path("search_results", views.search_results, name="search_results"),
]
