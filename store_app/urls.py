"""store_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path, include


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('inventory/', include('inventory_management.urls'))
# ]


from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view( 
    openapi.Info( 
        title="Sandwich Store", 
        default_version="v1", 
        description="Sandwich Store 를 위한 API 문서", 
        terms_of_service="https://www.google.com/policies/terms/", 
        contact=openapi.Contact(name="Sunhye Kim", email="sunwise9634@gmail.com"), 
    ), 
    public=True, 
    permission_classes=(permissions.AllowAny,), 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory_management.urls'))
]

# 이건 디버그일때만 swagger 문서가 보이도록 해주는 설정이라는 듯. urlpath도 이 안에 설정 가능해서, debug일때만 작동시킬 api도 설정할 수 있음.
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), 
    ]