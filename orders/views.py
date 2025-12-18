from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from .forms import ShippingAddressForm
from .models import Order, OrderItem  # ✅ make sure OrderItem exists


# ---------- helpers (EDIT THESE 3 FUNCTIONS TO MATCH YOUR PROJECT) ----------

def get_cart_items(request):
    """
    Return a list of cart line items.
    Each item must have: product, quantity, line_total
    Replace this with your real cart source (session cart, cart app, etc.).
    """
    # Example if you store cart in session as: {product_id: quantity}
    cart = request.session.get("cart", {})
    items = []
    if not cart:
        return items

    # Import your Product model where it lives (members/products app)
    from members.models import Product  # <-- adjust if Product is in another app

    for product_id_str, qty in cart.items():
        product = Product.objects.get(id=int(product_id_str))
        quantity = int(qty)
        line_total = (product.price * quantity)
        items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })
    return items


def calculate_totals(items):
    subtotal = sum((Decimal(str(i["line_total"])) for i in items), Decimal("0.00"))
    tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))  # GST/HST 5%
    shipping = Decimal("15.00") if subtotal > 0 else Decimal("0.00")  # your flat rule
    total = (subtotal + tax + shipping).quantize(Decimal("0.01"))
    return subtotal, tax, shipping, total


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True


# ------------------------------ main view ------------------------------

@login_required
def checkout(request):
    # 1) Pull cart items + totals for display
    items = get_cart_items(request)
    empty = (len(items) == 0)

    subtotal, tax, shipping, total = calculate_totals(items)

    # Optional: stock checking (keep structure so your template can use it)
    insufficient_items = []
    # If you have product stock tracking, add checks here:
    # for i in items:
    #     product = i["product"]
    #     requested = i["quantity"]
    #     available = product.stock
    #     if requested > available:
    #         insufficient_items.append({"product": product, "requested": requested, "available": available})

    shipping_label = "Flat $15 shipping for physical products"

    # 2) Default shipping data from profile (account address)
    profile = request.user.memberprofile  # adjust if your related name differs
    initial = {
        "ship_name": getattr(profile, "full_name", request.user.get_username()),
        "ship_phone": getattr(profile, "phone", ""),
        "ship_address1": getattr(profile, "address_line1", ""),
        "ship_address2": getattr(profile, "address_line2", ""),
        "ship_city": getattr(profile, "city", ""),
        "ship_province": getattr(profile, "province", ""),
        "ship_postal_code": getattr(profile, "postal_code", ""),
        "ship_country": getattr(profile, "country", "Canada") or "Canada",
    }

    # 3) Handle POST
    if request.method == "POST":
        action = request.POST.get("action")  # <-- from your button
        use_account = request.POST.get("use_account_address") == "on"

        form = ShippingAddressForm(request.POST)

        # If cart empty, block order
        if empty:
            messages.warning(request, "Your cart is empty.")
            return redirect("home")

        # If stock problem, block order
        if insufficient_items:
            messages.error(request, "Some items are not available in the requested quantity.")
            return redirect("cart_detail")

        # Only create order when they clicked Place Order
        if action == "place_order":
            if not form.is_valid():
                # show form errors on same page
                return render(request, "checkout.html", {
                    "form": form,
                    "items": items,
                    "subtotal": subtotal,
                    "tax": tax,
                    "shipping": shipping,
                    "shipping_label": shipping_label,
                    "total": total,
                    "empty": empty,
                    "insufficient_items": insufficient_items,
                })

            data = initial if use_account else form.cleaned_data

            # Create Order + OrderItems safely in a transaction
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    status="Paid",  # demo; later use "Pending" until payment success
                    total=total,
                    # If your Order model has these fields, add them:
                    # subtotal=subtotal, tax=tax, shipping=shipping,
                )

                # Save shipping snapshot onto Order
                for field, value in data.items():
                    setattr(order, field, value)
                order.save()

                # Create OrderItem rows
                for i in items:
                    OrderItem.objects.create(
                        order=order,
                        product=i["product"],
                        quantity=i["quantity"],
                        line_total=Decimal(str(i["line_total"])),
                        # If your model uses price instead, adjust accordingly
                    )

                # Clear cart
                clear_cart(request)

            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect("payment_success")  # adjust if your URL name differs

        # If action is missing or different, just reload page
        messages.info(request, "Please click Place Order to continue.")

    # 4) GET (or fallthrough)
    form = ShippingAddressForm(initial=initial)

    return render(request, "checkout.html", {
        "form": form,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "shipping_label": shipping_label,
        "total": total,
        "empty": empty,
        "insufficient_items": insufficient_items,
    })
