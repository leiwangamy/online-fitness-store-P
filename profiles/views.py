from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ProfileAllForm
from .models import Profile

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileAllForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profiles:address_edit")
    else:
        form = ProfileAllForm(instance=profile)

    return render(request, "profile/address_edit.html", {"form": form})

@login_required
def account_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile/account_profile.html", {"profile": profile, "edit_mode": False})
