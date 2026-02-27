# gift_exchange/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.splash_view, name="splash"),
    path("eligibility/", views.eligibity_view, name="eligibility"),
    path("home/", views.landing_view, name="landing"),
    path("register/", views.register_view, name="register"),
    path("partials/register_success.html", views.register_success_view,
         name="register_success"),
    path("reveal/", views.reveal_view, name="reveal"),
    path("partials/reveal_result", views.reveal_result_view, name="reveal_result"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
