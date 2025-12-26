from django import forms
import re


class ShippingAddressForm(forms.Form):
    ship_name = forms.CharField(
        label="Full name",
        max_length=100,
        widget=forms.TextInput(attrs={
            "autocomplete": "name",
        }),
    )

    ship_phone = forms.CharField(
        label="Phone number",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            "autocomplete": "tel",
        }),
    )

    ship_address1 = forms.CharField(
        label="Address line 1",
        max_length=255,
        widget=forms.TextInput(attrs={
            "autocomplete": "address-line1",
        }),
    )

    ship_address2 = forms.CharField(
        label="Address line 2",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "autocomplete": "address-line2",
        }),
    )

    ship_city = forms.CharField(
        label="City",
        max_length=100,
        widget=forms.TextInput(attrs={
            "autocomplete": "address-level2",
        }),
    )

    ship_province = forms.CharField(
        label="Province / State",
        max_length=100,
        widget=forms.TextInput(attrs={
            "autocomplete": "address-level1",
        }),
    )

    ship_postal_code = forms.CharField(
        label="Postal code",
        max_length=20,
        widget=forms.TextInput(attrs={
            "autocomplete": "postal-code",
        }),
    )

    ship_country = forms.CharField(
        label="Country",
        max_length=100,
        initial="Canada",
        widget=forms.TextInput(attrs={
            "autocomplete": "country",
            "readonly": True,
        }),
    )

    # -------------------------
    # Validation
    # -------------------------
    def clean_ship_phone(self):
        phone = self.cleaned_data.get("ship_phone", "")
        if phone:
            cleaned = re.sub(r"[^\d+]", "", phone)
            if len(cleaned) < 7:
                raise forms.ValidationError("Enter a valid phone number.")
            return cleaned
        return phone

    def clean_ship_postal_code(self):
        code = self.cleaned_data["ship_postal_code"].strip().upper()

        # Canadian postal code: A1A 1A1
        if not re.match(r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$", code):
            raise forms.ValidationError("Enter a valid Canadian postal code.")

        return code
