from django.shortcuts import render
from .models import Product


def home(request):
    # Get all active products from the database
    products = Product.objects.filter(is_active=True).order_by("name")
    return render(request, "members/home.html", {"products": products})
