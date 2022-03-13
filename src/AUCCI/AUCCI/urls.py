"""AUCCI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),
    path('listing/<str:name>/', views.listing, name='listing'),
    path('listing/', views.listing, name='listing'),
    path('delete_listing/<str:oid>/', views.delete_listing, name='delete_listing'),
    path('create_listing/', views.create_listing, name='create_listing'),
    path('categories/', views.categories, name='categories'),
    path('update_listing/<str:oid>/', views.update_listing, name='update_listing'),
    path('up/', views.up, name='up'),
]
