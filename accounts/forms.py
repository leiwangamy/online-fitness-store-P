from django import forms
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

class AccountEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "phone",
            "address1", "address2",
            "city", "province",
            "postal_code", "country",
        )
