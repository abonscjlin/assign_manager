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

# 從GitHub克隆代碼
ARG REPO_URL=https://github.com/abonscjlin/assign_manager.git
RUN git clone $REPO_URL /app

# 安裝Python依賴（按優先順序）
# 1. 如果存在requirements.txt，優先使用
# 2. 否則使用setup.py
# 3. 最後手動安裝基本依賴
RUN if [ -f requirements.txt ]; then \
        echo "使用requirements.txt安裝依賴" && \
        pip install --no-cache-dir -r requirements.txt; \
    elif [ -f setup.py ]; then \
        echo "使用setup.py安裝依賴" && \
        pip install --no-cache-dir pandas numpy flask flask-cors requests && \
        pip install --no-cache-dir -e .; \
    else \
        echo "手動安裝基本依賴" && \
        pip install --no-cache-dir pandas numpy flask flask-cors requests; \
    fi

# 暴露端口
EXPOSE 7777

# 設置環境變量
ENV PYTHONPATH=/app
ENV FLASK_APP=server/api_server.py
ENV FLASK_ENV=production

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# 啟動命令
CMD ["python", "server/api_server.py"]