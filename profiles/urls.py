from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("address/edit/", views.profile_edit, name="address_edit"),
    path("", views.account_profile, name="account_profile"),   
]
