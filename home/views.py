from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Product, Category


def home(request):
    """
    Home page with hero section, featured products, and latest blog posts
    """
    # Get featured products (limit to 3)
    # If no featured products, fall back to latest active products
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related("category").prefetch_related("images")[:3]
    
    # Fallback: if no featured products, show latest active products
    if not featured_products.exists():
        featured_products = Product.objects.filter(
            is_active=True
        ).select_related("category").prefetch_related("images").order_by("-id")[:3]
    
    # Get content from model (singleton pattern) with fallback
    content = None
    try:
        from core.models import FeaturedProductsContent
        content = FeaturedProductsContent.get_instance()
    except (ImportError, AttributeError, Exception):
        content = None
    
    # Get latest blog posts (limit to 1)
    latest_blog_posts = None
    try:
        from core.models import BlogPost
        latest_blog_posts = BlogPost.objects.filter(
            is_published=True
        ).order_by("-published_date", "-created_at").prefetch_related('images')[:1]
    except (ImportError, AttributeError, Exception):
        latest_blog_posts = None
    
    context = {
        "featured_products": featured_products,
        "content": content,
        "latest_blog_posts": latest_blog_posts,
    }
    
    return render(request, "home/home.html", context)
