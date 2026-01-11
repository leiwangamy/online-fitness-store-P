"""
Cart utility functions for handling both authenticated and anonymous users
"""
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser
from .models import CartItem


def get_cart_items(request):
    """
    Get cart items for both authenticated and anonymous users.
    Returns a list of dicts with: product, quantity, line_total
    """
    items = []
    
    if request.user.is_authenticated:
        # Authenticated users: get from database
        cart_items = CartItem.objects.filter(
            user=request.user,
            product__is_active=True
        ).select_related("product").order_by("-added_at")
        
        for ci in cart_items:
            items.append({
                "product": ci.product,
                "quantity": ci.quantity,
                "line_total": ci.product.price * ci.quantity,
            })
    else:
        # Anonymous users: get from session
        cart = request.session.get('cart', {})
        from products.models import Product
        
        for product_id_str, quantity in cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.filter(
                    pk=product_id,
                    is_active=True
                ).first()
                
                if product:
                    items.append({
                        "product": product,
                        "quantity": quantity,
                        "line_total": product.price * quantity,
                    })
            except (ValueError, TypeError):
                continue
    
    return items


def get_cart_count(request):
    """Get total number of items in cart"""
    if request.user.is_authenticated:
        return CartItem.objects.filter(
            user=request.user,
            product__is_active=True
        ).count()
    else:
        cart = request.session.get('cart', {})
        return sum(cart.values()) if cart else 0


def add_to_session_cart(request, product_id, quantity=1):
    """Add item to session cart for anonymous users"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True


def remove_from_session_cart(request, product_id):
    """Remove item from session cart for anonymous users"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True


def update_session_cart_quantity(request, product_id, quantity):
    """Update quantity in session cart for anonymous users"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if quantity <= 0:
        if product_id_str in cart:
            del cart[product_id_str]
    else:
        cart[product_id_str] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True


def transfer_session_cart_to_user(request, user):
    """Transfer session cart to database cart when user logs in"""
    cart = request.session.get('cart', {})
    
    if not cart:
        return
    
    from products.models import Product
    from django.db import transaction
    
    with transaction.atomic():
        for product_id_str, quantity in cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.filter(
                    pk=product_id,
                    is_active=True
                ).first()
                
                if product:
                    cart_item, created = CartItem.objects.get_or_create(
                        user=user,
                        product=product,
                        defaults={'quantity': 0}
                    )
                    
                    if created:
                        cart_item.quantity = quantity
                    else:
                        cart_item.quantity += quantity
                    
                    cart_item.save()
            except (ValueError, TypeError):
                continue
    
    # Clear session cart after transfer
    request.session['cart'] = {}
    request.session.modified = True

