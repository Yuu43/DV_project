# models.py
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)  # 用戶名
    password = models.CharField(max_length=255)  # 用戶的密碼

    def __str__(self):
        return self.username
