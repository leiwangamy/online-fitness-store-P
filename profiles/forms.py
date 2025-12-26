from django import forms
from .models import Profile

class ProfileAllForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "phone",
            "address1", "address2",
            "city", "province",
            "postal_code", "country",
        )
