from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictPrice

router = DefaultRouter()
router.register('predictprice', PredictPrice, basename='PredictPrice')

urlpatterns = [
    path('', include(router.urls)),  # 將路由的 URL 加入 urlpatterns
]