# DV_project/user/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Register,Login

router = DefaultRouter()
router.register('register', Register, basename='register')  # 使用 register 作為路由前綴
router.register('login', Login, basename='login')  # 使用 register 作為路由前綴

urlpatterns = [
    path('', include(router.urls)),  # 將路由的 URL 加入 urlpatterns
]
