# 工作分配管理系統 - API Server

這個資料夾包含了工作分配管理系統的API server相關檔案。

## 檔案說明

- `api_server.py` - 主要的Flask API服務器
- `test_api_server.py` - API功能測試腳本
- `manage_server.py` - API server管理腳本（推薦使用）
- `start_server.py` - 便利的啟動腳本
- `requirements_api.txt` - API server所需的Python套件
- `__init__.py` - Python模組初始化檔案

## 快速開始

### 1. 安裝依賴

```bash
# 回到專案根目錄
cd ..

# 使用現有的.venv虛擬環境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 安裝API server額外需要的套件
pip install -r server/requirements_api.txt
```

### 2. 管理API Server

#### 推薦方式：使用管理腳本
```bash
cd server

# 查看狀態
../.venv/bin/python manage_server.py status

# 啟動服務
../.venv/bin/python manage_server.py start

# 停止服務  
../.venv/bin/python manage_server.py stop

# 重新啟動
../.venv/bin/python manage_server.py restart
```

#### 其他啟動方式

##### 使用便利腳本
```bash
cd server
python start_server.py
```

##### 手動指定虛擬環境
```bash
# 從專案根目錄執行
./.venv/bin/python ./server/api_server.py
```

### 3. 測試API功能

```bash
# 從專案根目錄執行
./.venv/bin/python ./server/test_api_server.py
```

## API端點

- `GET /health` - 健康檢查
- `GET /api/config` - 取得系統配置
- `POST /api/assign` - 工作分配主要功能
- `POST /api/test/csv` - CSV檔案測試功能

## 服務位址

預設服務位址：`http://localhost:7777`

## 注意事項

- 確保專案根目錄的資料檔案（如employee_list.csv等）存在且格式正確
- API server會自動處理跨域請求
- 所有錯誤都會回傳詳細的英文錯誤訊息 