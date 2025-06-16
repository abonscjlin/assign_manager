# 工作分配管理系統 - Docker部署說明

## 概述

本文檔說明如何使用Docker容器化部署工作分配管理系統的API服務。系統會自動從GitHub克隆最新代碼並部署。

## 系統要求

- Docker >= 20.10
- Docker Compose >= 1.29
- Git（用於克隆代碼）
- 本機端口7777未被佔用

## 快速開始

### 1. 使用一鍵啟動腳本（推薦）

```bash
# 下載腳本到任意目錄
curl -O https://raw.githubusercontent.com/abonscjlin/assign_manager/main/docker/docker-start.sh
chmod +x docker-start.sh

# 一鍵啟動（自動克隆代碼、準備目錄、構建並啟動服務）
./docker-start.sh start

# 查看服務狀態
./docker-start.sh status

# 查看日誌
./docker-start.sh logs

# 停止服務
./docker-start.sh stop
```

### 2. 手動使用Docker Compose

```bash
# 先克隆Docker配置
git clone https://github.com/abonscjlin/assign_manager.git temp_docker
cp -r temp_docker/docker ./
rm -rf temp_docker

# 進入docker目錄
cd docker

# 構建並啟動服務
docker compose up -d

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f

# 停止服務
docker compose down
```

## 服務配置

### 端口映射
- 容器內部：7777端口
- 本機訪問：http://localhost:7777

### 目錄結構
系統會自動創建以下目錄結構：

```
當前目錄/
├── docker/                     # Docker配置目錄
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-start.sh
└── assign_manager/              # 自動克隆的專案目錄
    ├── server/                  # API服務代碼
    ├── result/                  # 分析結果輸出目錄（掛載）
    ├── employee_list.csv        # 技師清單文件（掛載）
    ├── result.csv              # 工作清單文件（掛載）
    └── ... 其他專案文件
```

### 目錄掛載
以下目錄會自動掛載到本機：

| 容器路徑 | 本機路徑 | 說明 | 權限 |
|---------|---------|-----|------|
| `/app/result` | `./assign_manager/result` | 分析結果輸出目錄 | 讀寫 |
| `/app/employee_list.csv` | `./assign_manager/employee_list.csv` | 技師清單文件 | 只讀 |
| `/app/result.csv` | `./assign_manager/result.csv` | 工作清單文件 | 只讀 |

### 環境變數
- `PYTHONPATH=/app` - Python路徑配置
- `PYTHONUNBUFFERED=1` - 即時輸出日誌
- `TZ=Asia/Taipei` - 時區設定
- `REPO_URL=https://github.com/abonscjlin/assign_manager.git` - GitHub倉庫地址

## API端點

服務啟動後，可以訪問以下端點：

- **健康檢查**: `GET http://localhost:7777/health`
- **工作分配**: `POST http://localhost:7777/api/assign`
- **系統配置**: `GET http://localhost:7777/api/config`
- **CSV測試**: `POST http://localhost:7777/api/test/csv`

詳細API文檔請參考專案中的 `API_文檔.md`

## 管理命令

### 啟動腳本選項

```bash
./docker-start.sh [選項]

選項:
  start     準備目錄、構建並啟動服務
  stop      停止服務
  restart   重啟服務
  status    查看服務狀態
  logs      查看服務日誌
  build     僅構建Docker映像
  update    更新代碼
  rebuild   重新構建並重啟服務
  cleanup   清理Docker資源
  help      顯示幫助信息
```

### Docker Compose命令

```bash
# 進入docker目錄
cd docker

# 構建映像
docker compose build

# 啟動服務（後台運行）
docker compose up -d

# 重啟服務
docker compose restart

# 停止並移除容器
docker compose down

# 查看日誌（即時）
docker compose logs -f

# 查看服務狀態
docker compose ps

# 進入容器Shell
docker compose exec assign-manager-api bash
```

## 更新和維護

### 1. 更新代碼
```bash
# 更新GitHub上的最新代碼
./docker-start.sh update

# 重新構建並重啟服務
./docker-start.sh rebuild
```

### 2. 手動更新
```bash
cd assign_manager
git pull origin main
cd ../docker
./docker-start.sh rebuild
```

## 故障排除

### 1. 端口被佔用
如果7777端口被佔用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:7777"  # 改用8080端口
```

### 2. 服務無法啟動
檢查日誌：
```bash
./docker-start.sh logs
# 或
cd docker && docker compose logs
```

### 3. Git克隆失敗
確保網路連接正常並且可以訪問GitHub：
```bash
git clone https://github.com/abonscjlin/assign_manager.git
```

### 4. 健康檢查失敗
等待更長時間讓服務完全啟動：
```bash
# 檢查服務狀態
curl http://localhost:7777/health

# 或查看詳細狀態
./docker-start.sh status
```

### 5. 目錄掛載問題
確保本機目錄存在且有適當權限：
```bash
# 檢查目錄結構
ls -la assign_manager/
ls -la assign_manager/result/

# 檢查權限
chmod 755 assign_manager/result/
```

### 6. 依賴安裝失敗
如果構建過程中依賴安裝失敗，可以重新構建：
```bash
./docker-start.sh cleanup
./docker-start.sh start
```

## 生產環境部署

### 1. 安全考量
- 修改預設端口
- 設置防火牆規則
- 使用反向代理（如Nginx）
- 啟用HTTPS
- 設置專用用戶運行容器

### 2. 性能優化
- 調整容器資源限制
- 使用生產級日誌配置
- 設置負載均衡（如需要）
- 定期清理日誌文件

### 3. 監控配置
- 設置容器監控
- 配置日誌收集
- 設置告警通知
- 監控磁碟使用量

## 文件結構

```
部署目錄/
├── docker/                      # Docker配置目錄
│   ├── Dockerfile              # Docker映像定義
│   ├── docker-compose.yml      # Docker Compose配置
│   ├── docker-start.sh         # 一鍵啟動腳本
│   ├── .dockerignore           # Docker忽略文件
│   └── Docker部署說明.md       # 本文檔
└── assign_manager/             # 自動克隆的專案目錄
    ├── server/
    │   └── api_server.py       # API服務主程式
    ├── result/                 # 結果輸出目錄（掛載）
    ├── employee_list.csv       # 技師清單（掛載）
    ├── result.csv             # 工作清單（掛載）
    └── ... 其他專案文件
```

## 常見使用場景

### 1. 首次部署
```bash
./docker-start.sh start
```

### 2. 日常啟動
```bash
./docker-start.sh start
```

### 3. 更新代碼
```bash
./docker-start.sh update
./docker-start.sh rebuild
```

### 4. 檢查狀態
```bash
./docker-start.sh status
```

### 5. 查看日誌
```bash
./docker-start.sh logs
```

### 6. 停止服務
```bash
./docker-start.sh stop
```

## 數據管理

### 備份重要數據
重要數據會保存在掛載的目錄中：
- `assign_manager/result/` - 所有分析結果
- `assign_manager/employee_list.csv` - 技師清單
- `assign_manager/result.csv` - 工作清單

建議定期備份這些文件：
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz assign_manager/result/ assign_manager/*.csv
```

### 自定義配置
如需自定義配置，可以修改 `assign_manager/` 目錄中的配置文件，然後重新構建：
```bash
./docker-start.sh rebuild
```

## 技術支援

### 系統信息
- GitHub倉庫: https://github.com/abonscjlin/assign_manager
- 容器化版本: v2.0
- 支援平台: Linux, macOS, Windows (Docker Desktop)

### 獲取幫助
如有問題，請：
1. 檢查日誌：`./docker-start.sh logs`
2. 查看服務狀態：`./docker-start.sh status`
3. 參考故障排除章節
4. 檢查GitHub Issues頁面
5. 聯繫技術支援團隊

### 報告問題
報告問題時，請提供：
- 操作系統版本
- Docker版本
- 錯誤日誌
- 重現步驟 