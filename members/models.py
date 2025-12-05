from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video_file", "Video file"),
        ("video_url", "Video URL"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    video = models.FileField(upload_to="product_videos/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.media_type} for {self.product.name}"
