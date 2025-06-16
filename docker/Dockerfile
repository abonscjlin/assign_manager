# 使用官方Python 3.9運行時作為基礎映像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴和Git
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 從GitHub克隆代碼
ARG REPO_URL=https://github.com/abonscjlin/assign_manager.git
RUN git clone ${REPO_URL} /app

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 安裝API server所需的額外依賴
RUN pip install --no-cache-dir \
    flask>=2.0.0 \
    flask-cors>=3.0.0

# 創建result目錄（如果不存在）
RUN mkdir -p /app/result

# 暴露API server端口
EXPOSE 7777

# 設置健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# 啟動API server
CMD ["python", "server/api_server.py"] 