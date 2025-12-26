from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from .forms import AccountEmailForm, ProfileForm
from profiles.models import Profile

from django.urls import reverse

def signup(request):
    # (Not used if allauth handles signup)
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home:home")
    else:
        form = UserCreationForm()
    return render(request, "account/signup.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home:home")


@login_required
def account_settings(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        email_form = AccountEmailForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if email_form.is_valid() and profile_form.is_valid():
            email_form.save()
            profile_form.save()
            messages.success(request, "Your account info has been updated.")
            return redirect("accounts:account_settings")
    else:
        email_form = AccountEmailForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, "account/account_settings.html", {
        "email_form": email_form,
        "profile_form": profile_form,
    })