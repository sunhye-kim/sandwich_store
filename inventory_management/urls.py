from django.urls import path
from . import views


urlpatterns = [
    path("hello/", views.HelloAPI),
    path("set_sandwich_ingredient/", views.set_sandwich_ingredient),
    path("get_data/<int:page_num>/", views.get_data),
    path("delete_data/", views.delete_data),
    path("get_sandwich_price/", views.get_sandwich_price),

    path("set_sandwich/", views.set_sandwich),
    path("get_sandwich_order_data/<int:page_num>/", views.get_sandwich_order_data),
    path("delete_sandwich_order_data/", views.delete_sandwich_order_data),
]