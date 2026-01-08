from datetime import timedelta
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import DigitalDownload


def send_order_confirmation_email(request, order):
    """
    Send order confirmation email for ALL orders (physical, digital, or mixed).
    This includes a link to view the order details.
    """
    to_email = getattr(getattr(order, "user", None), "email", None)
    if not to_email:
        return
    
    # Build the order detail page URL
    order_path = reverse("orders:my_order_detail", args=[order.id])
    
    # Build a login URL that redirects to that order after login
    login_path = reverse("account_login")
    next_param = quote(order_path, safe="")
    login_path_with_next = f"{login_path}?next={next_param}"
    
    # Make absolute URLs
    order_url = request.build_absolute_uri(order_path)
    login_url = request.build_absolute_uri(login_path_with_next)
    
    subject = f"Order Confirmation - Order #{order.id}"
    message = (
        f"Thank you for your order!\n\n"
        f"Order Number: #{order.id}\n"
        f"Total: ${order.total}\n\n"
        f"View your order details:\n"
        f"{login_url}\n\n"
        f"If you're already signed in, you can view your order here:\n"
        f"{order_url}\n\n"
        f"We'll send you another email if your order contains digital downloads.\n"
    )
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't fail the order creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send order confirmation email for order #{order.id}: {e}")


def create_downloads_and_email(request, order, days_valid=7, max_downloads=0):
    """
    Call ONLY after payment is confirmed.
    Creates digital download records and sends email with download links.
    max_downloads: 0 or None => unlimited
    """

    # Robust items access (related_name="items" OR default orderitem_set)
    items_manager = getattr(order, "items", None)
    items = items_manager.all() if items_manager is not None else order.orderitem_set.all()

    expires_at = None
    if days_valid and days_valid > 0:
        expires_at = timezone.now() + timedelta(days=days_valid)

    downloads = []
    for item in items:
        product = item.product

        is_digital = bool(getattr(product, "is_digital", False))
        has_file = bool(getattr(product, "digital_file", None))
        has_url = bool(getattr(product, "digital_url", None))

        if not is_digital or not (has_file or has_url):
            continue

        dl, _ = DigitalDownload.objects.get_or_create(
            order=order,
            product=product,
            defaults={
                "expires_at": expires_at,
                "max_downloads": max_downloads or 0,
            },
        )
        downloads.append(dl)

    if not downloads:
        return

    to_email = getattr(getattr(order, "user", None), "email", None)
    if not to_email:
        return

    # 1) Build the specific order page URL (this is what you want!)
    order_path = reverse("orders:my_order_detail", args=[order.id])

    # Optional: add a query param so you can highlight the downloads section
    order_path = f"{order_path}?highlight=downloads"

    # 2) Build a login URL that redirects to that order after login
    login_path = reverse("account_login")
    next_param = quote(order_path, safe="")  # safe="" so ? & = are encoded
    login_path_with_next = f"{login_path}?next={next_param}"

    # 3) Make absolute
    # Best: request.build_absolute_uri(...) because it matches the real domain/protocol
    order_url = request.build_absolute_uri(order_path)
    login_url = request.build_absolute_uri(login_path_with_next)

    subject = f"Your digital downloads for Order #{order.id}"
    message = (
        "Thanks for your purchase!\n\n"
        "Open your order to download your digital items:\n\n"
        f"{login_url}\n\n"
        "If you're already signed in, it will go directly to your order page.\n"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't fail the order creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send digital download email for order #{order.id}: {e}")
