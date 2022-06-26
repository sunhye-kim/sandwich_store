from traceback import print_exception
from rest_framework import serializers
from .models import SandwichIngredient, SandwichOrder # model

from rest_framework import serializers
from .models import SandwichIngredient


class SandwichSerializer(serializers.Serializer):
    bread = serializers.CharField(help_text='빵')
    toping = serializers.CharField(help_text='토핑')
    source = serializers.CharField(help_text='소스')
    cheeze = serializers.CharField(help_text='치즈')


class SandwichIngredientSerializer(serializers.Serializer):
    type = serializers.CharField(help_text='타입')
    name = serializers.CharField(help_text='이름')
    remain_cnt = serializers.IntegerField(help_text='남은개수')
    price = serializers.IntegerField(help_text='가격')


class IngredientSerializer(serializers.Serializer):
    type = serializers.CharField(help_text='타입')
    name = serializers.CharField(help_text='이름')


class SandwichNoSerializer(serializers.Serializer):
    sandwich_no = serializers.IntegerField(help_text='샌드위치번호')
