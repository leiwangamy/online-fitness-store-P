from django.contrib import admin
from .models import Product, ProductMedia


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1  # show 1 empty row by default (you can increase later)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    inlines = [ProductMediaInline]


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ("product", "media_type", "title", "sort_order")
    list_filter = ("media_type",)
