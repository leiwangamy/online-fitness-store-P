# fitness_club/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),

    path("payment/", include("payment.urls")),
    path("", include("members.urls")),   # home + cart + account + etc
    path("orders/", include("orders.urls")),  # only if you really have orders app urls
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
