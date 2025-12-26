from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from .models import CartItem


TAX_RATE = Decimal("0.05")  # change if you want


def _is_digital_or_service(product: Product) -> bool:
    return bool(getattr(product, "is_digital", False) or getattr(product, "is_service", False))


def _max_stock(product: Product) -> int:
    """
    Digital/service: unlimited (use a large number)
    Physical: quantity_in_stock (default 0)
    """
    if _is_digital_or_service(product):
        return 999999

    return int(getattr(product, "quantity_in_stock", 0) or 0)


@login_required
@transaction.atomic
def add_to_cart(request, pk):
    """
    Add to cart or update quantity for a single product.
    - GET: add 1 (like "Add to Cart" button)
    - POST: supports quantity + override=True
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

    max_stock = _max_stock(product)
    if max_stock <= 0 and not _is_digital_or_service(product):
        # no stock for physical product
        return redirect("cart:cart_detail")

    # digital/service forced to 1
    if _is_digital_or_service(product):
        quantity = 1
        override = True
    else:
        if request.method == "POST":
            quantity = int(request.POST.get("quantity", 1))
            override = request.POST.get("override") == "True"
        else:
            quantity = 1
            override = False

    cart_item, _created = CartItem.objects.select_for_update().get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 0},
    )

    if quantity < 1:
        cart_item.delete()
        return redirect("cart:cart_detail")

    if override:
        new_qty = min(quantity, max_stock)
    else:
        new_qty = min(cart_item.quantity + quantity, max_stock)

    cart_item.quantity = new_qty
    cart_item.save(update_fields=["quantity"])

    return redirect("cart:cart_detail")


@login_required
def remove_from_cart(request, pk):
    CartItem.objects.filter(user=request.user, product_id=pk).delete()
    return redirect("cart:cart_detail")


@login_required
@transaction.atomic
def update_cart_item(request, pk):
    """
    Optional: if you have a dedicated 'Update' button in cart page.
    POST only.
    """
    if request.method != "POST":
        return redirect("cart:cart_detail")

    item = get_object_or_404(CartItem.objects.select_for_update(), user=request.user, pk=pk)

    if _is_digital_or_service(item.product):
        item.quantity = 1
        item.save(update_fields=["quantity"])
        return redirect("cart:cart_detail")

    max_stock = _max_stock(item.product)
    if max_stock <= 0:
        item.delete()
        return redirect("cart:cart_detail")

    quantity = int(request.POST.get("quantity", 1))
    if quantity < 1:
        item.delete()
    else:
        item.quantity = min(quantity, max_stock)
        item.save(update_fields=["quantity"])

    return redirect("cart:cart_detail")


@login_required
def cart_detail(request):
    cart_items = (
        CartItem.objects.filter(user=request.user, product__is_active=True)
        .select_related("product")
        .order_by("-added_at")
    )

    subtotal = Decimal("0.00")
    items = []

    for ci in cart_items:
        line_total = ci.product.price * ci.quantity
        subtotal += line_total
        items.append(
            {
                "id": ci.id,
                "product": ci.product,
                "quantity": ci.quantity,
                "line_total": line_total,
            }
        )

    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total_with_tax = (subtotal + tax).quantize(Decimal("0.01"))

    context = {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total_with_tax": total_with_tax,
    }
    return render(request, "cart/cart.html", context)
