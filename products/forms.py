# products/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Product


class ProductAdminForm(forms.ModelForm):
    SERVICE_AVAILABILITY_CHOICES = (
        ("", "---------"),          # allow blank when not service
        ("unlimited", "Unlimited seats"),
        ("limited", "Limited seats"),
    )

    service_availability = forms.ChoiceField(
        choices=SERVICE_AVAILABILITY_CHOICES,
        required=False,
        help_text="For service products only.",
    )

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # nicer description box in admin
        if "description" in self.fields:
            self.fields["description"].widget = forms.Textarea(attrs={"rows": 4})

        # set initial dropdown based on instance
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            if instance.is_service:
                self.fields["service_availability"].initial = (
                    "unlimited" if instance.service_seats is None else "limited"
                )
            else:
                self.fields["service_availability"].initial = ""

    def clean(self):
        cleaned = super().clean()

        is_service = bool(cleaned.get("is_service"))
        is_digital = bool(cleaned.get("is_digital"))

        digital_file = cleaned.get("digital_file")
        digital_url = cleaned.get("digital_url")

        availability = cleaned.get("service_availability")  # unlimited / limited / ""
        seats = cleaned.get("service_seats")

        # 1) type conflict
        if is_service and is_digital:
            raise ValidationError("A product cannot be both digital and service.")

        # 2) digital requires file or url
        if is_digital and not (digital_file or digital_url):
            raise ValidationError("Digital product must have a digital_file or digital_url.")

        # 3) service availability -> seats logic
        if is_service:
            # if user didn't touch dropdown, infer from seats
            if not availability:
                availability = "unlimited" if seats in (None, 0) else "limited"

            if availability == "unlimited":
                cleaned["service_seats"] = None
            elif availability == "limited":
                if seats in (None, 0):
                    raise ValidationError("Limited seats service must have service_seats (>= 1).")
        else:
            # not service => clear service fields (keep DB clean)
            cleaned["service_seats"] = None
            cleaned["service_date"] = None
            cleaned["service_time"] = None
            cleaned["service_duration_minutes"] = None
            cleaned["service_location"] = ""

            # also clear dropdown so admin doesn't display stale data
            cleaned["service_availability"] = ""

        return cleaned
