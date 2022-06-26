from django.urls import path
from . import views


urlpatterns = [
    path("set_sandwich_ingredient_inventory/", views.SetSandwichIngredientInventory.as_view()),
    path("get_sandwich_ingredient_inventory/<int:page_num>/", views.GetSandwichIngredientInventory.as_view()),
    path("delete_data/", views.DelSandwichIngredientInventory.as_view()),
    path("get_sandwich_price/", views.GetSandwichPrice.as_view()),

    path("get_sandwich_order/<int:page_num>/", views.GetSandwichOrder.as_view()),
    path("set_sandwich/", views.SetSandwichOrder.as_view()),
    path("delete_sandwich_order/", views.DelSandwichOrder.as_view()),

]