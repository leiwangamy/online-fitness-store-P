from django import forms

class ShippingAddressForm(forms.Form):
    ship_name = forms.CharField(max_length=100)
    ship_phone = forms.CharField(max_length=30, required=False)

    ship_address1 = forms.CharField(max_length=255)
    ship_address2 = forms.CharField(max_length=255, required=False)

    ship_city = forms.CharField(max_length=100)
    ship_province = forms.CharField(max_length=100)
    ship_postal_code = forms.CharField(max_length=20)
    ship_country = forms.CharField(max_length=100, initial="Canada")

