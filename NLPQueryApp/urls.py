from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="nlpquery-home"),
    # path('home', views.homepage, name="homepage"),
    path('contacts', views.contactpage, name="contactpage")
]