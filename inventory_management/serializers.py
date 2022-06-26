from rest_framework import serializers
from .models import SandwichIngredient, SandwichOrder # model

from rest_framework import serializers
from .models import SandwichIngredient

class SandwichIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = SandwichIngredient
        fields = "__all__"
