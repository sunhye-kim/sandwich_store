from typing import List
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect

# module
from django.core.exceptions import * # 예외사항
from rest_framework import status # HTTP 상태코드
from rest_framework.response import Response # TemplateResponse 형식 객체

from .models import SandwichIngredient, SandwichOrder # model
from .serializers import SandwichIngredientSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view


import traceback


# Create your views here.
@api_view(['GET'])
def HelloAPI(request):
    return_data = {"name" : "Hello API!"}
    return JsonResponse(return_data)


# class InventoryManagement
@api_view(['GET'])
def get_data(request, page_num): # query_set이 없을 때
    try:
        all_sandwich_data = SandwichIngredient.objects.all()
        pagination_sandwich_data = Paginator(all_sandwich_data, 10).get_page(page_num)

        sandwich_data_list = pagination_sandwich_data.object_list
        return_data = {
            "detail" : list(sandwich_data_list.values()),
            "status" : 200,
        }

        return JsonResponse(return_data, safe=False)

    except ObjectDoesNotExist:
        print(traceback.format_exc())
        return Response({"message": "존재하지 않는 stock_no({})".format(page_num)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def insert_data(request):
    sandwich_ingredient = SandwichIngredient()

    sandwich_ingredient.title = request.POST['type']
    sandwich_ingredient.name = request.POST['name']
    sandwich_ingredient.remain_cnt = request.POST['remain_cnt']
    sandwich_ingredient.price = request.POST['price']
    sandwich_ingredient.reg_dtime = timezone.now()
    sandwich_ingredient.modify_dtime = timezone.now()
    sandwich_ingredient.save()

    return HttpResponseRedirect('/api/get_data/1/')


@api_view(['POST'])
def update_data(request):
    stock_no = request.POST['stock_no']
    
    sandwich_inventory = SandwichIngredient.objects.get(pk=stock_no)
    sandwich_inventory.price = request.POST['price']
    sandwich_inventory.save()

    return HttpResponseRedirect('/api/get_data/1/')


@api_view(['POST'])
def delete_data(request):
    stock_no = request.POST['stock_no']
    
    sandwich_inventory = SandwichIngredient.objects.get(pk=stock_no)
    sandwich_inventory.delete()

    return HttpResponseRedirect('/api/get_data/1/')
