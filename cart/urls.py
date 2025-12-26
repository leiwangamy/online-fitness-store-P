from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    # Cart detail page
    path("", views.cart_detail, name="cart_detail"),

    # Add product to cart
    path("add/<int:pk>/", views.add_to_cart, name="add_to_cart"),

    # Remove product from cart
    path("remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),

    # Optional: update quantity from cart page
    path("update/<int:pk>/", views.update_cart_item, name="update_cart_item"),
]
