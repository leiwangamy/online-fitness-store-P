from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # Product belongs to one category (optional)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    # Stock quantity (for physical products, or simple service stock)
    quantity_in_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Available quantity",
    )

    # Tax flags
    charge_gst = models.BooleanField(default=True, verbose_name="Charge GST (5%)")
    charge_pst = models.BooleanField(default=False, verbose_name="Charge PST (7%)")

    # 👉 PRODUCT TYPE FLAGS
    is_digital = models.BooleanField(default=False)   # Instant download product
    is_service = models.BooleanField(default=False)   # Yoga class, coaching, etc.

    # 👉 SERVICE-ONLY FIELDS
    # Seats: if set -> limited seats; if blank -> unlimited seats
    service_seats = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of seats. Leave blank for unlimited.",
    )
    service_date = models.DateField(blank=True, null=True)
    service_time = models.TimeField(blank=True, null=True)
    service_duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Length of class in minutes",
    )
    service_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. Studio Room A, Zoom link, park location",
    )

    # ----- Tax helper properties -----
    @property
    def gst_amount(self):
        return (
            self.price
            * Decimal("0.05")
            * (1 if self.charge_gst else 0)
        ).quantize(Decimal("0.01"))

    @property
    def pst_amount(self):
        return (
            self.price
            * Decimal("0.07")
            * (1 if self.charge_pst else 0)
        ).quantize(Decimal("0.01"))

    @property
    def price_with_tax(self):
        total = self.price + self.gst_amount + self.pst_amount
        return total.quantize(Decimal("0.01"))

    # ----- Helper: type checks -----
    @property
    def is_physical(self):
        """Convenience flag: physical = not digital and not service."""
        return not self.is_digital and not self.is_service

    # ----- Helper: availability text for templates -----
    @property
    def availability_text(self):
        """
        Human-friendly availability info to show on product pages.
        - Digital: 'Instant download'
        - Service: 'X seats left' / 'Unlimited seats' / 'Fully booked'
        - Physical: 'In stock: N' / 'Out of stock'
        """
        if self.is_digital:
            return "Instant download"

        if self.is_service:
            if self.service_seats is None:
                return "Unlimited seats"
            if self.service_seats > 0:
                return f"{self.service_seats} seats left"
            return "Fully booked"

        # Physical product
        if self.quantity_in_stock > 0:
            return f"In stock: {self.quantity_in_stock}"
        return "Out of stock"

    # ⭐ MAIN IMAGE HELPERS
    @property
    def main_image(self):
        """Return main image if exists, else first image, else None."""
        # 1. Try main image
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image.url

        # 2. Fallback to first uploaded
        first = self.images.first()
        if first:
            return first.image.url

        # 3. Nothing found
        return None

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="product_images/")
    alt_text = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    # ⭐ Which image is the main one on the card
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ensure only one main image per product
            ProductImage.objects.filter(
                product=self.product,
                is_main=True,
            ).exclude(id=self.id).update(is_main=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


class ProductVideo(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    title = models.CharField(max_length=200, blank=True)
    video_file = models.FileField(
        upload_to="product_videos/",
        blank=True,
        null=True,
    )
    video_url = models.URLField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Video {self.title or self.id}"


class ProductAudio(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="audios",
    )
    title = models.CharField(max_length=200, blank=True)
    audio_file = models.FileField(
        upload_to="product_audio/",
        blank=True,
        null=True,
    )
    audio_url = models.URLField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - Audio {self.title or self.id}"


class MemberProfile(models.Model):
    """
    Extra info for each user: whether they are an active member,
    and optional start/end dates.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile',
    )
    is_member = models.BooleanField(default=False)
    membership_started = models.DateTimeField(blank=True, null=True)
    membership_expires = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} – member={self.is_member}"

    @property
    def is_active_member(self):
        """
        Returns True if membership flag is ON and
        not expired (or no expiry date set).
        """
        if not self.is_member:
            return False
        if self.membership_expires and self.membership_expires < timezone.now():
            return False
        return True


# ---------- signals to auto-create MemberProfile ----------

User = get_user_model()


@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):
    if created:
        MemberProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_member_profile(sender, instance, **kwargs):
    if hasattr(instance, 'member_profile'):
        instance.member_profile.save()
