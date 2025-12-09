from django.contrib import admin
from .models import Product, ProductImage, ProductVideo, ProductAudio, Category




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1


class ProductAudioInline(admin.TabularInline):
    model = ProductAudio
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category', 
        'price',
        'quantity_in_stock',
        'charge_gst',
        'charge_pst',
        'is_active',
        # Optional, only if you added this @property in the model:
        # 'price_with_tax',
    )
    list_filter = (
        'category', 
        'is_active',
        'charge_gst',
        'charge_pst',
    )
    search_fields = ('name',)
    inlines = [ProductImageInline, ProductVideoInline, ProductAudioInline]

