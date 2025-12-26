from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import MemberProfile

@login_required
def my_membership(request):
    membership, _ = MemberProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "resume_membership" in request.POST and membership.is_active_member:
            membership.auto_renew = True
            if membership.membership_expires:
                membership.next_billing_date = (membership.membership_expires + timedelta(days=1)).date()
            membership.save()
            return redirect("members:my_membership")

        if "cancel_membership" in request.POST and membership.is_active_member:
            membership.auto_renew = False
            membership.next_billing_date = None
            membership.save()
            return redirect("members:my_membership")

        if "subscribe_basic" in request.POST:
            membership.start_monthly_membership(level="basic")
            return redirect("members:my_membership")

        if "subscribe_premium" in request.POST:
            membership.start_monthly_membership(level="premium")
            return redirect("members:my_membership")

        if "switch_to_basic" in request.POST and membership.is_active_member:
            membership.membership_level = "basic"
            membership.save(update_fields=["membership_level"])
            return redirect("members:my_membership")

        if "switch_to_premium" in request.POST and membership.is_active_member:
            membership.membership_level = "premium"
            membership.save(update_fields=["membership_level"])
            return redirect("members:my_membership")

    return render(request, "members/my_membership.html", {"profile": membership, "basic_price": 39, "premium_price": 79})
