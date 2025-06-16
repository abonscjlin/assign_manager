# 使用Python 3.9 slim基礎映像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 設置GitHub倉庫URL環境變數
ENV REPO_URL=https://github.com/abonscjlin/assign_manager.git

# 創建啟動腳本
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露端口
EXPOSE 7777

# 設置環境變量
ENV PYTHONPATH=/app
ENV FLASK_APP=server/api_server.py
ENV FLASK_ENV=production

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# 使用entrypoint腳本啟動
ENTRYPOINT ["/entrypoint.sh"]