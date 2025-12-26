from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Product, Category


def home(request):
    """
    Home page:
    - category filter: ?category=<slug>
    - search: ?q=<text>
    - pagination: ?page=<n>
    - 5 products per page (matches products/views.py)
    """
    selected_category = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()

    # Query active products with related data
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

    # Filter by category if selected
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Filter by search query if provided
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Order by newest first
    products = products.order_by("-id")

    # Paginate results (5 products per page - matches products/views.py)
    paginator = Paginator(products, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Get all categories for filter links
    categories = Category.objects.all()

    # Debug: Check product count (remove in production)
    total_count = products.count()
    
    context = {
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
        "page_obj": page_obj,  # Use paginated page_obj
        "total_products": total_count,  # For debugging
    }
    
    return render(request, "home/home.html", context)
