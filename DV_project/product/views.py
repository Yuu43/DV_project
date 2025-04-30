from django.shortcuts import render
from rest_framework import viewsets
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework import status
from sklearn.preprocessing import LabelEncoder
# from sklearn.externals import joblib
import xgboost as xgb
import numpy as np
import os
import requests

class PredictPrice(viewsets.ViewSet):
    # 加入 self 參數
    def get_exchange_rate(self):
        url = "https://api.exchangerate-api.com/v4/latest/USD"  # 使用實時匯率 API
        response = requests.get(url)
        data = response.json()
        return data['rates']['TWD']  # 返回美金對台幣的匯率
    
    def convert_usd_to_twd(self, usd_amount):
        exchange_rate = self.get_exchange_rate()  # 使用 self 調用該方法
        return usd_amount * exchange_rate



    def create(self, request):
        """
        接收 POST 請求，並使用 XGBoost 預測模型進行價格預測
        參數: 所有必須的特徵
        """

        try:
            # 確保模型文件存在
            model_path = 'DV_project/product/data/model_reduced.json'  # 更新模型路徑
            if not os.path.exists(model_path):
                return Response({'error': 'Model file not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 加載模型
            model = xgb.XGBRegressor()
            model.load_model(model_path)

            # 從 POST 請求中提取所有參數
            params = {
                'OverallQual': request.data.get('OverallQual'),  # 🏗️ 整體材料與做工的品質，對房價影響極大。數值越高（1-10），品質越好，房價通常越高。

                'BsmtQual': request.data.get('BsmtQual'),        # 🛠️ 地下室品質（Ex: Excellent, Gd: Good, Ta: Typical, Fa: Fair, NA: 無地下室）。地下室好壞會影響實用性與價值。

                'TotalBsmtSF': request.data.get('TotalBsmtSF'),  # 📏 地下室的總面積（平方英尺），地下室越大越有潛在價值（可做儲藏室、休閒室等）。

                'CentralAir': request.data.get('CentralAir'),    # ❄️ 是否有中央空調（Y/N）。有中央空調是現代化房屋的加分項，有助於提升舒適度與房價。

                '2ndFlrSF': request.data.get('2ndFlrSF'),        # 🏠 二樓面積（平方英尺），樓層面積越大，房屋整體使用空間越大，通常價格會越高。

                'GrLivArea': request.data.get('GrLivArea'),      # 👨‍👩‍👧‍👦 地面居住空間總面積（不含地下室），通常是影響房價的主要面積參數之一。

                'KitchenAbvGr': request.data.get('KitchenAbvGr'),# 🍽️ 地面上的廚房數量，通常為1，廚房數量多可能代表雙世代或豪宅結構。

                'KitchenQual': request.data.get('KitchenQual'),  # 🔪 廚房品質（Ex, Gd, Ta, Fa），高品質的廚房是買家非常看重的一點，對價格有顯著影響。

                'GarageType': request.data.get('GarageType'),    # 🚗 車庫類型（Attchd 附屬, Detchd 獨立, BuiltIn 建物內等），不同的車庫設計會影響房屋功能與價格。

                'GarageCars': request.data.get('GarageCars'),    # 🚘 車庫可容納的車輛數量，是衡量車庫實用性的重要因素，越多車位越加分。

                }

            # 檢查必須的參數是否都存在
            for param, value in params.items():
                if value is None:
                    return Response({'error': f'Missing parameter: {param}'}, status=status.HTTP_400_BAD_REQUEST)

            # 數值型參數轉換
            numeric_params = ['OverallQual', 'TotalBsmtSF', '2ndFlrSF', 'GrLivArea', 'KitchenAbvGr', 'GarageCars']
            for param in numeric_params:
                try:
                    params[param] = float(params[param])
                except (ValueError, TypeError):
                    return Response({'error': f'Invalid value for {param}'}, status=status.HTTP_400_BAD_REQUEST)

            # 類別型參數編碼
            label_encoders = ['BsmtQual', 'CentralAir', 'KitchenQual', 'GarageType']
            for col in label_encoders:
                if params[col] is not None:
                    le = LabelEncoder()
                    params[col] = le.fit_transform([params[col]])[0]
            for col in label_encoders:
                if params[col] is not None:
                    le = LabelEncoder()
                    params[col] = le.fit_transform([params[col]])[0]

            # 準備特徵數據
            feature_values = np.array([params[key] for key in params]).reshape(1, -1)

            # 預測
            prediction = model.predict(feature_values)

            # 測試：將預測的美金價轉換為台幣
            prediction_twd = self.convert_usd_to_twd(float(prediction[0]))

            print(f"預測售價 (台幣): {prediction_twd:.2f} TWD")

            # 返回預測結果
            return Response({'預測美金為': round(float(prediction[0]),1),
                             '轉換台幣為':round(prediction_twd,1)})

        except Exception as e:
            # 捕捉所有意外錯誤
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
