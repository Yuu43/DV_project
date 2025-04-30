from django.shortcuts import render
from rest_framework import viewsets
from django.db import transaction
from django.http import HttpResponse
from rest_framework.response import Response
from .models import User
from django.views.decorators.csrf import csrf_exempt
import environ
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.forms.models import model_to_dict



# 初始化 environ
env = environ.Env()
# 讀取 .env 文件
environ.Env.read_env()

# 獲取變數，例如 DEBUG 和 API_TOKEN
API_TOKEN = env.str("API_TOKEN", default="")


# Create your views here.
class Register(viewsets.ViewSet):
    @csrf_exempt
    def create(self,request):
        try:
            with transaction.atomic():
                username = request.data.get("username")
                password = request.data.get("password")
                # 檢查帳號是否已存在
                if User.objects.filter(username=username).exists():
                    return Response({'message': '帳號已存在'}, status=200)
                else:
                   
                    User.objects.create(
                        username=username,
                        password=password
                    )
                    return Response({'message': '註冊成功'}, status=200)
        
        except Exception as e:
            # 捕獲異常並返回 500
            return Response({'error': str(e)}, status=500)
        
class Login(viewsets.ViewSet):
    def create(self, request): 
        
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({'error': '請提供用戶名和密碼'}, status=400)

        
        # 從數據庫查找用戶
        user = User.objects.get(username=username)

            # 驗證密碼 (假設密碼是明文，建議改為加密驗證)
        if check_password(password, user.password):  
  
            # 生成 JWT Token
            
                metadata = User.objects.get(id=user)
                metadata_dict = model_to_dict(metadata)

                   # 生成 JWT Token
                refresh = RefreshToken.for_user(user)

                # 返回數據
                return Response({
                    'success': '登入成功',
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user_metadata': metadata_dict,
                }, status=200)
            
        else:
            return Response({'error': '密碼錯誤'}, status=200)