from django.urls import path
from . import views

app_name = "members"

urlpatterns = [
    path("membership/", views.my_membership, name="my_membership"),
]
