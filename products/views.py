from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product, Category


def product_list(request):
    """
    Product list page with pagination, optional category filter via:
    ?category=<slug>
    ?page=<n>
    """
    selected_category = request.GET.get("category", "").strip()

    categories = Category.objects.all()
    # Prefetch images for efficient loading
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Order by newest first
    products = products.order_by("-id")

    # Paginate results (5 products per page - you can change this number)
    paginator = Paginator(products, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "home/home.html", {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": "",  # No search on product list page
        "total_products": products.count(),
    })


def home(request):
    """
    Home page:
    - category filter: ?category=<slug>
    - search: ?q=<text>
    - pagination: ?page=<n>
    """
    selected_category = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()

    # Prefetch images for efficient loading
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

    if selected_category:
        products = products.filter(category__slug=selected_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    products = products.order_by("-id")

    paginator = Paginator(products, 5)  # change per-page number if you want
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all()

    return render(request, "home/home.html", {
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
        "page_obj": page_obj,
        "total_products": products.count(),
    })


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images", "videos", "audios"),
        pk=pk,
        is_active=True
    )
    return render(request, "products/product_detail.html", {"product": product})
