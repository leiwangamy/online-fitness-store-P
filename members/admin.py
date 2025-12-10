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
    'is_digital',
    'is_service',
    'is_active',
    )
    list_filter = (
    'category',
    'is_active',
    'charge_gst',
    'charge_pst',
    'is_digital',
    'is_service',
    )
    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "description", "price", "is_active", "category")
        }),
        ("Tax & Stock", {
            "fields": ("quantity_in_stock", "charge_gst", "charge_pst")
        }),
        ("Digital Product", {
            "fields": ("is_digital",),
            "classes": ("collapse",)
        }),
        ("Service Product (Classes / Coaching)", {
            "fields": ("is_service", "service_date", "service_time",
                       "service_duration_minutes", "service_location"),
            "classes": ("collapse",)
        }),
    )
    search_fields = ('name',)
    inlines = [ProductImageInline, ProductVideoInline, ProductAudioInline]

