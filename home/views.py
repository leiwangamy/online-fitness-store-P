from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Product, Category


def home(request):
    """
    Home page with hero section and featured products
    """
    # Get featured products (limit to 3)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related("category").prefetch_related("images")[:3]
    
    context = {
        "featured_products": featured_products,
    }
    
    return render(request, "home/home.html", context)
