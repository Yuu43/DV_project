# 使用穩定版 Python（建議 3.11，而非 3.13，因為 3.13 可能有相容性問題）
FROM python:3.11

# 設定工作目錄
WORKDIR /app

# 複製專案檔案
COPY . /app/

# 安裝相依套件
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests
RUN pip install xgboost
RUN pip install numpy
RUN pip install --no-cache-dir scikit-learn xgboost
RUN pip install --no-cache-dir pandas
RUN pip install joblib
RUN pip install scikit-learn
RUN pip install requests


# 更新套件並安裝必要工具
RUN apt update && apt install -y wget unzip curl

# 安裝 Google Chrome 和 Chromedriver
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install \
    && rm google-chrome-stable_current_amd64.deb \
    && apt install -y chromium-driver



# 收集靜態檔案
RUN python manage.py collectstatic --noinput

# 確保資料庫遷移完成（避免 Nginx 啟動時 Django 還沒準備好）
RUN python manage.py migrate

# 開放 Django 預設的 8000 port
EXPOSE 8000

# 設定啟動指令，使用 Gunicorn 運行 Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000","--reload", "DV_project.wsgi:application"]

