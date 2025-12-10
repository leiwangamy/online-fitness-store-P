from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from members.models import Product   # Product model lives in members app


@login_required
def checkout(request):
    """
    Checkout page:
    - Shows order summary
    - Checks stock
    - Calculates tax + shipping
    - On POST (and if stock is OK), clears cart and redirects to success.
    """
    # Cart is stored in session: { "product_id": quantity }
    cart = request.session.get("cart", {})

    # Case 1: empty cart
    if not cart:
        return render(request, "payment/checkout.html", {"empty": True})

    # Get products in cart
    product_ids = cart.keys()
    products = Product.objects.filter(pk__in=product_ids, is_active=True)
    product_map = {str(p.pk): p for p in products}

    items = []
    subtotal = Decimal("0.00")
    insufficient_items = []

    for pid, qty in cart.items():
        product = product_map.get(str(pid))
        if not product:
            continue

        # 🔴 IMPORTANT: change "STOCK_FIELD_NAME" to your real field name
        # e.g. "stock", "inventory", "quantity", etc.
        stock = getattr(product, "STOCK_FIELD_NAME", None)

        # If your model has no stock field at all, you can just set:
        # stock = None
        # and the over-quantity check will be skipped.

        if stock is not None and qty > stock:
            insufficient_items.append(
                {
                    "product": product,
                    "requested": qty,
                    "available": stock,
                }
            )

        line_total = product.price * qty
        subtotal += line_total

        items.append(
            {
                "product": product,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    # --- Tax (5%) ---
    TAX_RATE = Decimal("0.05")
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))

    # --- Shipping rules (simple demo) ---
    if subtotal == 0:
        shipping = Decimal("0.00")
        shipping_label = "No shipping"
    elif subtotal >= 50:
        shipping = Decimal("0.00")
        shipping_label = "Free shipping for orders over $50"
    else:
        shipping = Decimal("5.00")
        shipping_label = "Flat $5 shipping"

    total = (subtotal + tax + shipping).quantize(Decimal("0.01"))

    # If user clicks "Place Order (demo)"
    if request.method == "POST" and not insufficient_items:
        # here is where real payment integration would go
        # for now we just clear the cart and redirect to a success page
        request.session["cart"] = {}
        return redirect("payment:success")

    context = {
        "empty": False,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "shipping_label": shipping_label,
        "total": total,
        "insufficient_items": insufficient_items,
    }
    return render(request, "payment/checkout.html", context)


@login_required
def success(request):
    """Simple success page after 'placing' the order."""
    return render(request, "payment/success.html")
