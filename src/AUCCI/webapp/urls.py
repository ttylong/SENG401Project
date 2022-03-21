from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index2"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("product", views.product, name="product"),
    path("search_results", views.search_results, name="search_results"),
    path("search_results/<str:pk>", views.product, name="product"),
    path("profile", views.profile, name="profile"),
    path("logout", views.signout, name="logout"),
    path("settings_view", views.settings_req, name="settings"),
]
