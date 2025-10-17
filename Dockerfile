# =====================================================
# 🐳 Streamlit 聖經大車拼 Dockerfile
# =====================================================
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝必要系統套件
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libxext6 curl && \
    rm -rf /var/lib/apt/lists/*

# 複製套件清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式檔案
COPY . .

# 設定環境變數（Streamlit 運行設定）
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# 開放 Streamlit 預設 port
EXPOSE 8501

# 啟動命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
