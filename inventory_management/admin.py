from django.contrib import admin
from inventory_management.models import SandwichIngredient

# Register your models here.
@admin.register(SandwichIngredient)
class SandwichIngredientAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'remain_cnt')