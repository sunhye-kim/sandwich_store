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

from drf_yasg.utils import swagger_auto_schema

import traceback

from .models import SandwichIngredient, SandwichOrder # model

from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

sandwich_type = {
    "빵" : "BREAD",
    "토핑" : "TOPING",
    "소스" : "SOURCE",
    "치즈" : "CHEEZE"
}

# 샌드위치 재료 재고 데이터 가져오기
# 제외 : 재고가 0인 데이터는 제외한다
class GetSandwichIngredientInventory(APIView):
    type = openapi.Parameter('type', openapi.IN_QUERY, description='샌드위치 재료 타입(빵,토핑,치즈,소스)', required=False, type=openapi.TYPE_STRING)
    name = openapi.Parameter('name', openapi.IN_QUERY, description='샌드위치 재료(바게트,토마토,모짜렐라,올리브오일 등)', required=False, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 재료 재고 데이터 가져오기 (재고가 0인 데이터 제외)'], manual_parameters=[type,name], responses={200: "Success"})
    def get(self, request, page_num):
        # 페이징 처리, 10개씩
        limit_cnt = 10
        offset_cnt = 10 *(page_num-1)

        r_type = request.GET.get('type') # 빵,토핑,치즈,소스 만 가능
        r_name = request.GET.get('name')

        try:
            r_type = sandwich_type[r_type] # 재고 데이터 대치 (빵 -> BREAD, 토핑 -> TOPING)
        except:
            return Response({"message": "Check parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 파라미터별 검색 로직 
            if r_type and r_name:
                all_sandwich_data = (SandwichIngredient.objects.
                                    filter(Q(type=r_type) & Q(name=r_name)).
                                    exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt])
            elif r_name:
                all_sandwich_data = (SandwichIngredient.objects.
                                    filter(name=r_name).
                                    exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt])
            elif r_type:
                all_sandwich_data = (SandwichIngredient.objects.
                                    filter(type=r_type).
                                    exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt])
            else:
                all_sandwich_data = (SandwichIngredient.objects.
                                    exclude(remain_cnt=0)[offset_cnt:offset_cnt+limit_cnt])
            
            return_data = {
                "detail" : list(all_sandwich_data.values('type', 'name', 'price', 'remain_cnt')),
                "status" : 200,
            }

            return JsonResponse(return_data, safe=False)

        except ObjectDoesNotExist:
            print(traceback.format_exc())
            return Response({"message": "page Error({})".format(page_num)}, status=status.HTTP_404_NOT_FOUND)
    

# 샌드위치 재료 데이터 추가
# 최초 인서트되는 데이터는 추가, 이미 존재하는 데이터는 업데이트
class SetSandwichIngredientInventory(APIView):
    type = openapi.Parameter('type', openapi.IN_QUERY, description='샌드위치 재료 타입(빵,토핑,치즈,소스)', required=False, type=openapi.TYPE_STRING)
    name = openapi.Parameter('name', openapi.IN_QUERY, description='샌드위치 재료(바게트,토마토,모짜렐라,올리브오일 등)', required=False, type=openapi.TYPE_STRING)
    plus_cnt = openapi.Parameter('plus_cnt', openapi.IN_QUERY, 
                                description='추가할 데이터 개수 (최초 인서트 시 개수만큼 추가, 존재하는 데이터 인서트 시 파라미터 개수만큼 더하기', 
                                required=False, type=openapi.TYPE_STRING)
    price = openapi.Parameter('price', openapi.IN_QUERY, description='샌드위치 재료 가격 (insert, update)', required=False, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 재고 데이터 추가 및 업데이트'], manual_parameters=[type,name,plus_cnt,price], responses={200: "Success"})
    def post(self, request):
        r_type = request.POST.get('type')
        r_name = request.POST.get('name')
        r_plus_cnt = request.POST.get('remain_cnt')
        r_price = request.POST.get('price')

        try:
            r_type = sandwich_type[r_type] # 재고 데이터 대치 (빵 -> BREAD, 토핑 -> TOPING)
        except:
            return Response({"message": "Check parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # 데이터 존재 여부 확인
        sandwich_ingredient_data = (SandwichIngredient.objects.
                                    filter(Q(type=r_type) & Q(name=r_name)))

        if sandwich_ingredient_data.exists(): # 재고 데이터 대치 (빵 -> BREAD, 토핑 -> TOPING)
            ingredient_no = sandwich_ingredient_data.values()[0]['id']
            sandwich_inventory = SandwichIngredient.objects.get(pk=ingredient_no)

            sandwich_inventory.price = r_price
            sandwich_inventory.remain_cnt = int(sandwich_inventory.remain_cnt) + int(r_plus_cnt)
            sandwich_inventory.modify_dtime = timezone.now()
            sandwich_inventory.save()

        else: # 존재하지 않으면 인서트
            sandwich_ingredient = SandwichIngredient()
            sandwich_ingredient.type = r_type
            sandwich_ingredient.name = r_name
            sandwich_ingredient.remain_cnt = r_plus_cnt
            sandwich_ingredient.price = r_price
            sandwich_ingredient.reg_dtime = timezone.now()
            sandwich_ingredient.modify_dtime = timezone.now()

            sandwich_ingredient.save()

        return_data = {
            "detail": "success",
            "status" : 200
        }
        
        return Response(return_data, status = status.HTTP_204_NO_CONTENT)


# 샌드위치 재고 데이터 삭제
# type, name 별 삭제
class DelSandwichIngredientInventory(APIView):
    type = openapi.Parameter('type', openapi.IN_QUERY, description='샌드위치 재료 타입(빵,토핑,치즈,소스)', required=True, type=openapi.TYPE_STRING)
    name = openapi.Parameter('name', openapi.IN_QUERY, description='샌드위치 재료(바게트,토마토,모짜렐라,올리브오일 등)', required=True, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 재고 데이터 삭제'], manual_parameters=[type,name], responses={200: "Success"})
    def post(self, request):
        try:
            r_type = request.POST['type']
            r_name = request.POST['name']
            r_type = sandwich_type[r_type]
        except:
            return Response({"message": "Check parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 데이터 존재여부 확인
            sandwich_ingredient_data = (SandwichIngredient.objects.
                                        filter(Q(type=r_type)&Q(name=r_name)))

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


# 샌드위치 주문 데이터 가져오기
# type, name 별로 검색 가능
class GetSandwichOrder(APIView):
    search_type = openapi.Parameter('type', openapi.IN_QUERY, description='샌드위치 재료 타입(빵,토핑,치즈,소스) - 필터링 시에만 사용', required=False, type=openapi.TYPE_STRING)
    search_name = openapi.Parameter('name', openapi.IN_QUERY, description='샌드위치 재료(바게트,토마토,모짜렐라,올리브오일 등) - 필터링 시에만 사용', required=False, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 주문 데이터 가져오기'], manual_parameters=[search_type,search_name], responses={200: "Success"})
    def get(self, request, page_num):
        # 페이징 처리, 10개씩
        limit_cnt = 10
        offset_cnt = 10 * (page_num-1)

        r_search_type = request.GET.get('search_type')
        r_search_name = request.GET.get('search_name')

        try:
            r_search_type = sandwich_type[r_search_type]# 재고 데이터 대치 (빵 -> BREAD, 토핑 -> TOPING)

        except:
            return Response({"message": "Check parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 삭제된 데이터는 조회 안됨 (is_delete = 0)
            if r_search_type and r_search_name: # 검색 데이터 있을 때는 검색 쿼리 실행
                sandwich_order_data = (SandwichOrder.objects.values('sandwich_no').
                                    annotate(dcount=Count('sandwich_no')).
                                    filter(Q(is_delete=0)&Q(ingredient_type=r_search_type)&Q(ingredient_name=r_search_name)).
                                    order_by()[offset_cnt:offset_cnt+limit_cnt])
            else: # 검색 데이터 없으면 전체 데이터 조회
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
                ingredient_data = (SandwichOrder.objects.
                                filter(sandwich_no=_sandwich_order_data['sandwich_no']))
                
                # 샌드위치 재료 데이터 조회
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


# 샌드위치 주문 데이터 저장
class SetSandwichOrder(APIView):
    bread = openapi.Parameter('bread', openapi.IN_QUERY, description='샌드위치 재료 타입(빵) - 식빵, 호밀빵, 치아바타 등, 최대 1개', required=True, type=openapi.TYPE_STRING)
    toping = openapi.Parameter('toping', openapi.IN_QUERY, description='샌드위치 재료 타입(토핑) - 햄, 베이컨, 치킨, 양상추, 토마토 등, 최대 2개', required=True, type=openapi.TYPE_STRING)
    cheeze = openapi.Parameter('cheeze', openapi.IN_QUERY, description='샌드위치 재료 타입(치즈) - 모짜렐라치즈, 슈레드치즈, 체다치즈 등, 최대 1개', required=True, type=openapi.TYPE_STRING)
    source = openapi.Parameter('source', openapi.IN_QUERY, description='샌드위치 재료 타입(소스) - 허니머스타드, 불닭소스, 스위트어니언. 케찹, 올리브오일 등, 최대 2개', required=True, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 주문 데이터 저장하기'], manual_parameters=[bread,toping,cheeze,source], responses={200: "Success"})
    @transaction.atomic()
    def post(self,request):
        r_bread = request.GET.get('bread')
        r_toping = request.GET.get('toping')
        r_cheeze = request.GET.get('cheeze')
        r_source = request.GET.get('source')

        if not r_bread or not r_toping or not r_cheeze or not r_source: # 데이터 없으면 데러
            return Response(
                {'error' : {
                'code' : 405,
                'message' : "All ingredient was not selected"}})

        # 샌드위치 데이터 str -> list, ex) '토마토,햄' -> ['토마토','햄']
        bread = str(r_bread).replace(' ','').split(',')
        toping = str(r_toping).replace(' ','').split(',')
        cheeze = str(r_cheeze).replace(' ','').split(',')
        source = str(r_source).replace(' ','').split(',')

        # 각각 최대 개수 이상 되면 에러
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

        sandwich_no_data = (SandwichOrder.objects.
                            all().order_by("-sandwich_no"))
        if sandwich_no_data: # 샌드위치 데이터가 있으면, 다음 sanswich_no로 +1
            sandwich_no = sandwich_no_data.values()[0]['id'] + 1
        else: # 최초 인서트는 1
            sandwich_no = 1
        
        # 인서트할 데이터 중에 재료가 없는거, 0개인게 없는지 확인
        for type_key, value in sandwich_dict.items():
            for _ingredient in value:
                _ingredient_data = SandwichIngredient.objects.filter(Q(type=type_key) & Q(name=_ingredient))

                if not _ingredient_data.exists():
                    return Response(
                        {'error' : {
                        'code' : 404,
                        'message' : "SandwichIngredient not found!"}})

                if _ingredient_data.values()[0]['remain_cnt'] == 0:
                    return Response(
                        {'error' : {
                        'code' : 404,
                        'message' : "SandwichIngredient not remained"}})

        redirect_url = '/inventory/get_sandwich_price/?' # 총합 계산을 위한 url 호출

        #데이터 인서트
        with transaction.atomic():
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


# 샌드위치 가격 데이터 불러오기
class GetSandwichPrice(APIView):
    bread = openapi.Parameter('bread', openapi.IN_QUERY, description='샌드위치 재료 타입(빵) - 식빵, 호밀빵, 치아바타 등, 최대 1개', required=False, type=openapi.TYPE_STRING)
    toping = openapi.Parameter('toping', openapi.IN_QUERY, description='샌드위치 재료 타입(토핑) - 햄, 베이컨, 치킨, 양상추, 토마토 등, 최대 2개', required=False, type=openapi.TYPE_STRING)
    cheeze = openapi.Parameter('cheeze', openapi.IN_QUERY, description='샌드위치 재료 타입(치즈) - 모짜렐라치즈, 슈레드치즈, 체다치즈 등, 최대 1개', required=False, type=openapi.TYPE_STRING)
    source = openapi.Parameter('source', openapi.IN_QUERY, description='샌드위치 재료 타입(소스) - 허니머스타드, 불닭소스, 스위트어니언. 케찹, 올리브오일 등, 최대 2개', required=False, type=openapi.TYPE_STRING)

    @swagger_auto_schema(tags=['샌드위치 주문 데이터 가격 받아오기'], manual_parameters=[bread,toping,cheeze,source], responses={200: "Success"})
    def get(self, request):
        r_bread = request.GET.get('bread')
        r_toping = request.GET.get('toping')
        r_cheeze = request.GET.get('cheeze')
        r_source = request.GET.get('source')

        if not r_bread or not r_toping or not r_cheeze or not r_source: # 필수 데이터
            return Response(
                {'error' : {
                'code' : 405,
                'message' : "All ingredient was not selected"}})

        # 샌드위치 데이터 str -> list, ex) '토마토,햄' -> ['토마토','햄']
        bread = str(r_bread).replace(' ','').split(',')
        toping = str(r_toping).replace(' ','').split(',')
        cheeze = str(r_cheeze).replace(' ','').split(',')
        source = str(r_source).replace(' ','').split(',')

        # 각각 최대 개수 이상 되면 에러
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
        
        # 데이터 총 가격 데이터 
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


# 샌드위치 주문 데이터 삭제
class DelSandwichOrder(APIView):
    sandwich_no = openapi.Parameter('sandwich_no', openapi.IN_QUERY, description='샌드위치 번호', required=True, type=openapi.TYPE_NUMBER)

    @swagger_auto_schema(tags=['샌드위치 주문 데이터 삭제하기'], manual_parameters=[sandwich_no], responses={200: "Success"})
    def post(request):
        try:
            sandwich_no = request.POST['sandwich_no']
        except:
            return Response({"message": "Check parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # pk(인스턴스의 id)값을 받아 어떤 인스턴스인지 특정
            # url slug로 pk값을 받도록 urls.py에서 설정해준다.
            sandwich_inventory = SandwichOrder.objects.filter(sandwich_no=sandwich_no)

            for _sandwich_inventory in sandwich_inventory.values():
                
                # 재고 데이터 +1
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


# 재고 데이터 관리 (+1, -1)
def ingredient_no_management(_ingredient_no, minus=True):
    # 재고 데이터 -1
    if minus:
        bread_inventory_data = SandwichIngredient.objects.get(pk=_ingredient_no)
        bread_inventory_data.remain_cnt = int(bread_inventory_data.remain_cnt) - 1
        bread_inventory_data.save()
    
    #재고 데이터  +1
    else:
        bread_inventory_data = SandwichIngredient.objects.get(pk=_ingredient_no)
        bread_inventory_data.remain_cnt = int(bread_inventory_data.remain_cnt) + 1
        bread_inventory_data.save()
