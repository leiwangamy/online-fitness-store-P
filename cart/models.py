from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


class CartItem(models.Model):
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
