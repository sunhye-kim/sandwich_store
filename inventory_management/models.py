from email.policy import default
from django.db import models
from django.utils import timezone

class StockTypeCode(models.TextChoices):
    BREAD = "BREAD", "빵"
    TOPING = "TOPING", "토핑"
    CHEEZE = "CHEEZE", "치즈"
    SOURCE = "SOURCE", "소스"

 # 현재 재고관리 상황
class SandwichIngredient(models.Model):
    type = models.CharField(max_length=50, choices=StockTypeCode.choices, null=False) # 재고 타입
    name = models.CharField(max_length=50, null=False) # 재고 이름
    remain_cnt = models.PositiveIntegerField(default=0) # 남은 재고 개수
    price = models.PositiveIntegerField(default=0) # 가격
    reg_dtime = models.DateTimeField(default=timezone.now) # 재고 등록일시
    modify_dtime = models.DateTimeField(default=timezone.now) # 재고 수정일시

    class Meta:
        ordering = ["type", "name"]

    
    # def __str__(self):
    #     return self.

 # 샌드위치
class SandwichOrder(models.Model):
    sandwich_no = models.PositiveIntegerField() # 샌드위치 번호
    ingredient_type = models.CharField(max_length=50, null=False) # 재료 타입
    ingredient_name = models.CharField(max_length=50, null=False) # 재료명
    is_delete = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sandwich_no"]
    

    
