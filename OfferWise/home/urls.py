# app: offerwise
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("offer/new", views.offer_new, name="offer_new"),
    path("benchmarks", views.benchmarks, name="benchmarks"),
    path("simulator", views.simulator, name="simulator"),
    path("script", views.script_studio, name="script_studio"),
    path("review", views.review, name="review"),
    path("learning", views.learning_hub, name="learning_hub"),
]
