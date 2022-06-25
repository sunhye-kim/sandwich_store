from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    return_data = {"name" : "sunhye"}

    return JsonResponse(return_data)