from django.urls import path

from . import views_orders, views_downloads

app_name = "orders"

urlpatterns = [
    path("my-orders/", views_orders.my_orders, name="my_orders"),
    path("my_orders_detail/<int:order_id>/", views_orders.my_order_detail, name="my_order_detail"),
    path("download/<uuid:token>/", views_downloads.digital_download, name="digital_download"),
]
