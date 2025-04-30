# admin.py
from django.contrib import admin
from .models import User

# 註冊模型到 Django Admin
admin.site.register(User)
