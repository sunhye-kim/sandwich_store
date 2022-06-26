from django.utils import timezone
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Q, Count
from django.db import transaction

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# module
from django.core.exceptions import * # 예외사항
from rest_framework import status # HTTP 상태코드
from rest_framework.response import Response # TemplateResponse 형식 객체

import traceback

from .models import SandwichIngredient, SandwichOrder # model


# Create your views here.
@api_view(['GET'])
def HelloAPI(request):
    return_data = {"name" : "Hello API!"}
    return JsonResponse(return_data)


# class InventoryManagement
@api_view(['GET'])
def get_data(request, page_num):
    # 페이징 처리, 10개씩
    limit_cnt = 10
    offset_cnt = 10 *(page_num-1)

    r_type = request.GET.get('type')
    r_name = request.GET.get('name')

    try:
        if r_type and r_name:
            all_sandwich_data = SandwichIngredient.objects.filter(Q(type=r_type) & Q(name=r_name)).exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt]
        elif r_name:
            all_sandwich_data = SandwichIngredient.objects.filter(name=r_name).exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt]
        elif r_type:
            all_sandwich_data = SandwichIngredient.objects.filter(type=r_type).exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt]
        else:
            all_sandwich_data = SandwichIngredient.objects.exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt]
        
        return_data = {
            "detail" : list(all_sandwich_data.values('type', 'name', 'price', 'remain_cnt')),
            "status" : 200,
        }

        return JsonResponse(return_data, safe=False)

    except ObjectDoesNotExist:
        print(traceback.format_exc())
        return Response({"message": "page Error({})".format(page_num)}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def set_sandwich_ingredient(request):
    is_errror = False

    r_type = request.POST.get('type')
    r_name = request.POST.get('name')
    r_plus_cnt = request.POST.get('remain_cnt')
    r_price = request.POST.get('price')

    sandwich_ingredient_data = SandwichIngredient.objects.filter(Q(type=r_type) & Q(name=r_name))

    # 데이터가 존재하면,
    if sandwich_ingredient_data.exists():
        ingredient_no = sandwich_ingredient_data.values()[0]['id']
        sandwich_inventory = SandwichIngredient.objects.get(pk=ingredient_no)

        sandwich_inventory.price = r_price
        sandwich_inventory.remain_cnt = int(sandwich_inventory.remain_cnt) + int(r_plus_cnt)
        sandwich_inventory.modify_dtime = timezone.now()
        sandwich_inventory.save()

    else: # 존재하지 않으면
        sandwich_ingredient = SandwichIngredient()
        sandwich_ingredient.type = r_type
        sandwich_ingredient.name = r_name
        sandwich_ingredient.remain_cnt = r_plus_cnt
        sandwich_ingredient.price = r_price
        sandwich_ingredient.reg_dtime = timezone.now()
        sandwich_ingredient.modify_dtime = timezone.now()

        sandwich_ingredient.save()

    if not is_errror:
        return_data = {
            "detail": "success",
            "status" : 200
        }
        
        return Response(return_data, status = status.HTTP_204_NO_CONTENT)

    else:
        return_data = {
            "detail": "failed",
            "status" : 500
        }
        return Response(return_data)


@api_view(['POST'])
def delete_data(request):
    r_type = request.POST['type']
    r_name = request.POST.get['name']
    
    try:
        sandwich_ingredient_data = SandwichIngredient.objects.filter(Q(type=r_type) & Q(name=r_name))

        # 데이터가 존재하면 진행
        if sandwich_ingredient_data.exists():
            ingredient_no = sandwich_ingredient_data.values()[0]['id']
            sandwich_inventory = SandwichIngredient.objects.get(pk=ingredient_no)
            sandwich_inventory.delete()

        # 데이터가 존재하지 않으면,
        else:
            return Response({"message": "Get data Error ({}, {})".format(r_type, r_name)}, status=status.HTTP_404_NOT_FOUND)

    # 받은 pk값으로 조회했을 때 해당하는 인스턴스가 없다면 출력할 에러 코드와 메시지를 설정한다.
    except SandwichIngredient.DoesNotExist:
        return Response({"message": "Delete Error ingredient_no({})".format(ingredient_no)}, status=status.HTTP_404_NOT_FOUND)

    return_data = {
        "status" : 200,
    }

    return Response(return_data, status = status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_sandwich_order_data(request, page_num):
    # 페이징 처리, 10개씩
    limit_cnt = 10
    offset_cnt = 10 * (page_num-1)

    r_type = request.GET.get('type')
    r_search_name = request.GET.get('search_name')

    try:
        if r_type and r_search_name:
            sandwich_order_data = (SandwichOrder.objects.values('sandwich_no')
                .annotate(dcount=Count('sandwich_no'))
                .filter(Q(is_delete=0)&Q(ingredient_type=r_type)&Q(ingredient_name=r_search_name))
                .order_by()[offset_cnt:offset_cnt+limit_cnt]
            )
        else:
            sandwich_order_data = (SandwichOrder.objects.values('sandwich_no')
                .annotate(dcount=Count('sandwich_no'))
                .filter(Q(is_delete=0))
                .order_by()[offset_cnt:offset_cnt+limit_cnt]
            )

        sandwich_list = []
        for _sandwich_order_data in sandwich_order_data:
            sandwich_dict = {}
            sandwich_dict['sandwich_no'] = _sandwich_order_data['sandwich_no']

            sandwich_ingredient_list = list()
            ingredient_data = SandwichOrder.objects.filter(sandwich_no=_sandwich_order_data['sandwich_no'])
            for _ingredient_data in ingredient_data.values():
                sandwich_ingredient_list.append(_ingredient_data['ingredient_name'])

            sandwich_dict['ingredient_list'] = sandwich_ingredient_list

            sandwich_list.append(sandwich_dict)
        
        return_data = {
            "status" : 200,
        }
        return_data['detail'] = sandwich_list
       

    except ObjectDoesNotExist:
        print(traceback.format_exc())
        return Response({"message": "Get data Error ({})".format(page_num)}, status=status.HTTP_404_NOT_FOUND)
    
    return JsonResponse(return_data, safe=False)


@api_view(['POST'])
def set_sandwich(request):
    r_bread = request.GET.get('bread')
    r_toping = request.GET.get('toping')
    r_cheeze = request.GET.get('cheeze')
    r_source = request.GET.get('source')

    if not r_bread or not r_toping or not r_cheeze or not r_source:
        return Response(
            {'error' : {
            'code' : 405,
            'message' : "All ingredient was not selected"}})

    bread = str(r_bread).replace(' ','').split(',')
    toping = str(r_toping).replace(' ','').split(',')
    cheeze = str(r_cheeze).replace(' ','').split(',')
    source = str(r_source).replace(' ','').split(',')

    if len(bread) > 1 or len(toping) > 2 or len(cheeze) > 1 or len(source) > 2:
        return Response(
            {'error' : {
            'code' : 405,
            'message' : "Some ingredient was overed"}})
    
    sandwich_dict = {
        "BREAD" : bread,
        "TOPING" : toping,
        "CHEEZE" : cheeze,
        "SOURCE" : source
    }

    sandwich_no_data = SandwichOrder.objects.all().order_by("-sandwich_no")
    if sandwich_no_data:
        sandwich_no = sandwich_no_data.values()[0]['id'] + 1
    else:
        sandwich_no = 0

    with transaction.atomic():
        
        redirect_url = '/inventory/get_sandwich_price/?' # 총합 계산을 위한 url 호출

        for type_key, value in sandwich_dict.items():
            for _ingredient in value:
                _ingredient_data = SandwichIngredient.objects.filter(Q(type=type_key) & Q(name=_ingredient))

                _ingredient_no = _ingredient_data.values('id')[0]['id']
                ingredient_no_management(_ingredient_no, minus=True)

                sandwich_order = SandwichOrder()
                sandwich_order.sandwich_no = sandwich_no
                sandwich_order.ingredient_type = type_key
                sandwich_order.ingredient_name = _ingredient
                sandwich_order.save()

                redirect_url += f'{type_key.lower()}={_ingredient}&' # 계산 총합 redirect

    return redirect(redirect_url[:-1])


@api_view(['GET'])
def get_sandwich_price(request):
    r_bread = request.GET.get('bread')
    r_toping = request.GET.get('toping')
    r_cheeze = request.GET.get('cheeze')
    r_source = request.GET.get('source')

    if not r_bread or not r_toping or not r_cheeze or not r_source:
        return Response(
            {'error' : {
            'code' : 405,
            'message' : "All ingredient was not selected"}})

    bread = str(r_bread).replace(' ','').split(',')
    toping = str(r_toping).replace(' ','').split(',')
    cheeze = str(r_cheeze).replace(' ','').split(',')
    source = str(r_source).replace(' ','').split(',')

    if len(bread) > 1 or len(toping) > 2 or len(cheeze) > 1 or len(source) > 2:
        return Response(
            {'error' : {
            'code' : 405,
            'message' : "Some ingredient was overed"}})
    
    sandwich_dict = {
        "BREAD" : bread,
        "TOPING" : toping,
        "CHEEZE" : cheeze,
        "SOURCE" : source
    }

    total_price = 0
    
    for type_key, value in sandwich_dict.items():
        for _ingredient in value:
            _ingredient_data = SandwichIngredient.objects.filter(Q(type=type_key) & Q(name=_ingredient))
            _ingredient_price = _ingredient_data.values('price')[0]['price']
            total_price += int(_ingredient_price)

    return_data = {
        "status" : 200,
        "detail" : {
            "total_price" : total_price,
        }
    }

    return JsonResponse(return_data, safe=False)


def ingredient_no_management(_ingredient_no, minus=True):
    if minus:
        bread_inventory_data = SandwichIngredient.objects.get(pk=_ingredient_no)
        bread_inventory_data.remain_cnt = int(bread_inventory_data.remain_cnt) - 1
        bread_inventory_data.save()
    
    else:
        bread_inventory_data = SandwichIngredient.objects.get(pk=_ingredient_no)
        bread_inventory_data.remain_cnt = int(bread_inventory_data.remain_cnt) + 1
        bread_inventory_data.save()


@api_view(['POST'])
def delete_sandwich_order_data(request):
    sandwich_no = request.POST['sandwich_no']

    if not sandwich_no:
        return Response(
            {'error' : {
            'code' : 405,
            'message' : "Check parameters"}})
    
    try:
        # pk(인스턴스의 id)값을 받아 어떤 인스턴스인지 특정
        # url slug로 pk값을 받도록 urls.py에서 설정해준다.
        sandwich_inventory = SandwichOrder.objects.filter(sandwich_no=sandwich_no)

        for _sandwich_inventory in sandwich_inventory.values():
            
            _ingredient_data = SandwichIngredient.objects.filter(Q(type=_sandwich_inventory['ingredient_type']) & Q(name=_sandwich_inventory['ingredient_name']))
            _ingredient_no = _ingredient_data.values('id')[0]['id']
            ingredient_no_management(_ingredient_no, minus=False)

            # 주문 취소
            try:
                sandwich_inventory_update = SandwichOrder.objects.get(id=_sandwich_inventory['id'])

            # 받은 pk값으로 조회했을 때 해당하는 인스턴스가 없다면 출력할 에러 코드와 메시지를 설정한다.
            except SandwichIngredient.DoesNotExist:
                return Response(
                    {'error' : {
                    'code' : 404,
                    'message' : "SandwichIngredient not found!"}})
            
            sandwich_inventory_update.is_delete = 1
            sandwich_inventory_update.save()

    # 받은 pk값으로 조회했을 때 해당하는 인스턴스가 없다면 출력할 에러 코드와 메시지를 설정한다.
    except SandwichOrder.DoesNotExist:
        return Response(
            {'error' : {
            'code' : 404,
            'message' : "SandwichOrder not found!"}})

    return_data = {
        "status" : 200,
    }
    
    return Response(return_data, status = status.HTTP_204_NO_CONTENT)

