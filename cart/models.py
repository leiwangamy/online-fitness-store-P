"""
Shopping Cart Models Module

This module defines the shopping cart functionality for the e-commerce platform.

Key Model:
- CartItem: Represents an item in a user's shopping cart

Features:
- One cart item per product per user (enforced by unique_together)
- Quantity management
- Automatic subtotal calculation
- Persistent cart (stored in database, not session)
- Cart items are filtered by active products only

Cart Lifecycle:
1. User adds product to cart → CartItem created/updated
2. User can update quantity or remove items
3. During checkout, cart items are converted to OrderItems
4. After successful order, cart is cleared

Usage Example:
    # Add item to cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Get user's cart
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate cart total
    total = sum(item.subtotal for item in cart_items)
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


class CartItem(models.Model):
    """
    Shopping Cart Item Model
    
    Represents a single product in a user's shopping cart.
    Each user can have only one CartItem per product (enforced by unique_together).
    
    Attributes:
        user: The user who owns this cart item
        product: The product being added to cart
        quantity: Number of units (default: 1)
        added_at: Timestamp when item was added to cart
    
    Properties:
        subtotal: Calculated subtotal (product.price * quantity)
    
    Example:
        cart_item = CartItem.objects.create(
            user=user,
            product=yoga_mat,
            quantity=2
        )
        print(cart_item.subtotal)  # yoga_mat.price * 2
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # one row per product per user
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} — {self.product} x {self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.product.price * self.quantity
