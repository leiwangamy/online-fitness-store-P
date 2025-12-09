from django.db import models
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # product belongs to one category (optional)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    # 🔹 New: stock quantity
    quantity_in_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Available quantity"
    )

    # 🔹 New: tax flags
    charge_gst = models.BooleanField(
        default=True,
        verbose_name="Charge GST (5%)"
    )
    charge_pst = models.BooleanField(
        default=False,
        verbose_name="Charge PST (7%)"
    )

    # 🔹 Tax helper properties
    @property
    def gst_amount(self):
        """5% GST if applicable, otherwise 0."""
        return (self.price * Decimal("0.05") * (1 if self.charge_gst else 0)).quantize(
            Decimal("0.01")
        )

    @property
    def pst_amount(self):
        """7% PST if applicable, otherwise 0."""
        return (self.price * Decimal("0.07") * (1 if self.charge_pst else 0)).quantize(
            Decimal("0.01")
        )

    @property
    def price_with_tax(self):
        """Base price + GST + PST."""
        total = self.price + self.gst_amount + self.pst_amount
        return total.quantize(Decimal("0.01"))

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


class ProductVideo(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    title = models.CharField(max_length=200, blank=True)

    video_file = models.FileField(
        upload_to='product_videos/',
        blank=True,
        null=True
    )
    video_url = models.URLField(
        blank=True,
        null=True
    )
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Video {self.title or self.id}"


class ProductAudio(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='audios'
    )
    title = models.CharField(max_length=200, blank=True)

    audio_file = models.FileField(
        upload_to='product_audio/',
        blank=True,
        null=True
    )
    audio_url = models.URLField(
        blank=True,
        null=True
    )
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Audio {self.title or self.id}"
