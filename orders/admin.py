# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem  # add DigitalDownload here if it's in orders app


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    # Only keep this if your ProductAdmin supports autocomplete (search_fields)
    autocomplete_fields = ("product",)

    readonly_fields = ("line_total_admin",)
    fields = ("product", "quantity", "price", "line_total_admin")

    @admin.display(description="Line total")
    def line_total_admin(self, obj):
        qty = getattr(obj, "quantity", 0) or 0
        price = getattr(obj, "price", None)
        if price is None and getattr(obj, "product", None):
            price = getattr(obj.product, "price", 0)
        return (price or 0) * qty


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "status",
        "shipping_carrier", "tracking_number",
        "total", "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("status", "shipping_carrier", "created_at")
    date_hierarchy = "created_at"
    search_fields = ("=id", "user__username", "user__email", "tracking_number")
    inlines = (OrderItemInline,)

    readonly_fields = (
        "shipping_full_admin",
        "subtotal", "tax", "shipping", "total",
        "created_at", "updated_at",
    )

    fieldsets = (
        ("Order Info", {
            "fields": ("user", "status", "shipping_carrier", "tracking_number")
        }),
        ("Shipping Address", {
            "fields": (
                "ship_name", "ship_phone",
                "ship_address1", "ship_address2",
                "ship_city", "ship_province", "ship_postal_code", "ship_country",
                "shipping_full_admin",
            )
        }),
        ("Financial Summary", {
            "fields": ("subtotal", "tax", "shipping", "total")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    @admin.display(description="Shipping full")
    def shipping_full_admin(self, obj):
        parts = [
            getattr(obj, "ship_name", "") or "",
            getattr(obj, "ship_phone", "") or "",
            getattr(obj, "ship_address1", "") or "",
            getattr(obj, "ship_address2", "") or "",
            " ".join([p for p in [
                getattr(obj, "ship_city", "") or "",
                getattr(obj, "ship_province", "") or "",
                getattr(obj, "ship_postal_code", "") or "",
            ] if p]).strip(),
            getattr(obj, "ship_country", "") or "",
        ]
        lines = [p.strip() for p in parts if p and p.strip()]
        return format_html("<br>".join(lines)) if lines else "-"
