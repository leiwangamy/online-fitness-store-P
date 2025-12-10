# payment/urls.py

from django.urls import path
from . import views

app_name = "payment"   # so we can use {% url 'payment:checkout' %}

urlpatterns = [
    path("", views.checkout, name="checkout"),          # /payment/
    path("success/", views.success, name="success"),    # /payment/success/
]
