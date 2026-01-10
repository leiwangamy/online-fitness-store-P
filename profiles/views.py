from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ProfileAllForm
from .models import Profile
from orders.models import Order

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileAllForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect to 'next' parameter if provided, otherwise to profile page
            next_url = request.GET.get('next') or request.POST.get('next') or "profiles:account_profile"
            return redirect(next_url)
    else:
        form = ProfileAllForm(instance=profile)

    return render(request, "profile/address_edit.html", {"form": form, "next": request.GET.get('next', '')})

@login_required
def account_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile/account_profile.html", {"profile": profile, "edit_mode": False})

@login_required
def billing_payments(request):
    """Display billing and payment history (orders)"""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "profile/billing_payments.html", {"orders": orders})
