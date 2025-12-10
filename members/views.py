from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from .models import Product, Category


def product_list(request):
    category_slug = request.GET.get("category")   # read ?category=towels from URL
    categories = Category.objects.all()

    products = Product.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, "product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": category_slug,
    })


def home(request):
    selected_category = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)

    # Filter by category if selected
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # 🔍 Filter by search term (product name contains text)
    if search_query:
        products = products.filter(name__icontains=search_query)

    paginator = Paginator(products, 5)  # products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, "members/home.html", {
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
        "page_obj": page_obj,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, "members/product_detail.html", {"product": product})


# --- Cart helpers ---

def _get_cart(request):
    """
    Get the cart dict from the session, or create an empty one.
    Cart format: { "product_id": quantity, ... }
    """
    cart = request.session.get("cart")
    if cart is None:
        cart = {}
        request.session["cart"] = cart
    return cart


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = _get_cart(request)

    product_id = str(product.pk)
    current_qty = cart.get(product_id, 0)

    # Use the actual stock field from your Product model
    max_stock = getattr(product, "quantity_in_stock", 0)

    # If you want digital/service products to ignore stock, you could do:
    # if getattr(product, "is_digital", False) or getattr(product, "is_service", False):
    #     max_stock = 999999

    # No stock at all -> do nothing
    if max_stock <= 0:
        return redirect("cart_detail")

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        override = request.POST.get("override") == "True"

        if quantity < 1:
            # If user types 0, treat it as "remove"
            cart.pop(product_id, None)
        else:
            if override:
                # user updated quantity in cart page
                new_qty = min(quantity, max_stock)
            else:
                # adding extra units (e.g. from product page with quantity field)
                new_qty = min(current_qty + quantity, max_stock)

            cart[product_id] = new_qty
    else:
        # simple "Add to Cart" link/button (no quantity field)
        new_qty = min(current_qty + 1, max_stock)
        cart[product_id] = new_qty

    request.session["cart"] = cart
    return redirect("cart_detail")



def remove_from_cart(request, pk):
    cart = _get_cart(request)
    product_id = str(pk)
    if product_id in cart:
        del cart[product_id]
        request.session["cart"] = cart
    return redirect("cart_detail")


def cart_detail(request):
    cart = _get_cart(request)

    items = []
    subtotal = Decimal("0.00")

    # get the Product objects for items in cart
    product_ids = cart.keys()
    products = Product.objects.filter(pk__in=product_ids, is_active=True)
    product_map = {str(p.pk): p for p in products}

    for pid, qty in cart.items():
        product = product_map.get(pid)
        if not product:
            continue
        line_total = product.price * qty
        subtotal += line_total
        items.append(
            {
                "product": product,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    # simple tax (change rate if you want)
    TAX_RATE = Decimal("0.05")      # 5%
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total_with_tax = (subtotal + tax).quantize(Decimal("0.01"))

    context = {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total_with_tax": total_with_tax,
    }
    return render(request, "members/cart.html", context)


# --- Payment / checkout placeholder ---

@login_required
def payment(request):
    cart = _get_cart(request)

    if not cart:
        return render(request, "members/payment.html", {"empty": True})

    items = []
    total = Decimal("0.00")
    product_ids = cart.keys()
    products = Product.objects.filter(pk__in=product_ids, is_active=True)
    product_map = {str(p.pk): p for p in products}

    for pid, qty in cart.items():
        product = product_map.get(pid)
        if not product:
            continue
        line_total = product.price * qty
        total += line_total
        items.append(
            {
                "product": product,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    if request.method == "POST":
        # pretend payment ok, clear cart
        request.session["cart"] = {}
        return render(request, "members/payment_success.html", {"total": total})

    return render(request, "members/payment.html", {"items": items, "total": total})


def signup(request):
    """Simple registration view using Django's built-in UserCreationForm."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
