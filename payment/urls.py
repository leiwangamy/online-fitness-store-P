# payment/urls.py

from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("", views.checkout, name="checkout"),          # /payment/
    path("success/", views.success, name="success"),    # /payment/success/
]
