# members/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    # cart
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),

    # account/address
    path("address/edit/", views.address_edit, name="address_edit"),
    path("account/profile/", views.account_profile, name="account_profile"),

    # user pages
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:pk>/", views.my_order_detail, name="my_order_detail"),
    path("my-membership/", views.my_membership, name="my_membership"),
]
