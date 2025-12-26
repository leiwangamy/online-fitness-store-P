from django.urls import path
from . import views

app_name = "accounts"   # 👈 namespace

urlpatterns = [
    path("settings/", views.account_settings, name="account_settings"),
    path("logout/", views.logout_view, name="account_logout"),
    path("signup/", views.signup, name="signup"),

    # Optional (only if  use own signup view)
    # path("signup/", views.signup, name="signup"),
]
