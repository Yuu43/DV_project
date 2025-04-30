# DV_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', include('DV_project.user.urls')),  # 引入 user 應用的 urls.py
    path('product/', include('DV_project.product.urls')),  # 引入 product 應用的 urls.py
]
