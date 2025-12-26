# members/admin.py
from django.contrib import admin
from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "membership_level",
        "is_member",
        "is_active_member_display",
        "membership_started",
        "membership_expires",
        "auto_renew",
        "next_billing_date",
    )
    list_filter = ("membership_level", "is_member", "auto_renew")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("membership_started", "membership_expires")

    @admin.display(boolean=True, description="Active now?")
    def is_active_member_display(self, obj):
        return obj.is_active_member
