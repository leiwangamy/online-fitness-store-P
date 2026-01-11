"""
Signals to handle cart transfer when user logs in
"""
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .utils import transfer_session_cart_to_user


@receiver(user_logged_in)
def transfer_cart_on_login(sender, request, user, **kwargs):
    """
    Transfer session cart to database cart when user logs in.
    """
    if hasattr(request, 'session') and request.session.get('cart'):
        transfer_session_cart_to_user(request, user)

