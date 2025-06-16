# Docker自動拉取功能說明

## 🚀 功能概述

現在Docker啟動腳本已經支援自動從GitHub拉取最新代碼，確保每次啟動的容器都使用最新版本的代碼。

## 📋 可用命令

### 主要啟動命令

| 命令 | 說明 | 用途 | 耗時 |
|------|------|------|------|
| `start` | 拉取最新代碼、完全重建並啟動服務 | **生產部署推薦** | ~35秒 |
| `start-fast` | 快速啟動服務（使用Docker緩存） | 開發測試使用 | ~22秒 |

### 構建命令

| 命令 | 說明 | 緩存策略 |
|------|------|----------|
| `build` | 重新構建Docker映像 | 不使用緩存 |
| `build-fast` | 快速構建Docker映像 | 使用Docker緩存 |

### 其他命令

| 命令 | 說明 |
|------|------|
| `stop` | 停止服務 |
| `restart` | 重啟服務 |
| `status` | 查看服務狀態 |
| `logs` | 查看服務日誌 |
| `update` | 僅更新代碼 |
| `rebuild` | 重新構建並重啟服務 |
| `cleanup` | 清理Docker資源 |

## 🔄 自動拉取流程

### 完整啟動流程 (`start`)

1. **檢查依賴**：驗證Docker和Git環境
2. **準備目錄**：創建必要的本機目錄結構
3. **自動拉取**：
   ```bash
   git fetch origin
   git reset --hard origin/main
   git clean -fd
   ```
4. **顯示最新提交**：確認拉取到的版本
5. **完全重建**：使用 `--no-cache` 重新構建Docker映像
6. **啟動服務**：啟動容器並進行健康檢查

### 快速啟動流程 (`start-fast`)

1. **檢查依賴**：驗證Docker和Git環境
2. **準備目錄**：創建必要的本機目錄結構
3. **自動拉取**：同樣會拉取最新代碼
4. **快速構建**：使用Docker緩存加速構建
5. **啟動服務**：啟動容器並進行健康檢查

## 📊 性能對比

根據實際測試結果：

- **完整啟動** (`start`)：約35秒
  - 優點：確保最新代碼，完全重建
  - 適用：生產部署、重要更新

- **快速啟動** (`start-fast`)：約22秒  
  - 優點：速度快，依然會拉取最新代碼
  - 適用：開發測試、頻繁重啟

## 🛡️ 安全特性

### 本地變更保護

自動拉取過程會：
- `git reset --hard origin/main`：重置所有本地變更
- `git clean -fd`：清理未追蹤的文件
- 確保本地狀態與GitHub倉庫完全一致

### 錯誤處理

- 自動檢測Git倉庫狀態
- 處理合併衝突和分支問題
- 顯示詳細的日誌信息

## 💡 使用建議

### 🌟 推薦用法

1. **生產部署**：
   ```bash
   ./docker/docker-start.sh start
   ```

2. **開發測試**：
   ```bash
   ./docker/docker-start.sh start-fast
   ```

3. **查看狀態**：
   ```bash
   ./docker/docker-start.sh status
   ```

4. **查看日誌**：
   ```bash
   ./docker/docker-start.sh logs
   ```

### 🔧 故障排除

如果遇到問題，按順序嘗試：

1. **檢查權限**：
   ```bash
   ./docker/docker-start.sh fix-perm
   ```

2. **完全重置**：
   ```bash
   ./docker/docker-start.sh cleanup
   ./docker/docker-start.sh start
   ```

3. **檢查Docker Compose**：
   ```bash
   ./docker/docker-start.sh check-comp
   ```

## 📂 目錄結構

```
/項目根目錄/
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── docker-start.sh          # 管理腳本
│   └── Docker自動拉取功能說明.md   # 本文檔
└── assign_manager/              # 自動創建的掛載目錄
    ├── result/                  # 結果輸出目錄
    ├── requirements.txt         # Python依賴
    └── ...                      # GitHub代碼
```

## 🔍 驗證最新代碼

啟動後可以驗證是否使用了最新代碼：

```bash
# 檢查容器內的Git提交
docker exec assign-manager-api bash -c "cd /app && git log --oneline -3"

# 檢查容器內的文件時間戳
docker exec assign-manager-api ls -la /app/

# 檢查API健康狀態
curl http://localhost:7777/health
```

## 🎯 核心優勢

1. **自動化**：每次啟動都自動獲取最新代碼
2. **可靠性**：強制重置確保代碼一致性
3. **靈活性**：提供快速和完整兩種啟動模式
4. **透明度**：詳細的日誌輸出和狀態報告
5. **易用性**：一個命令完成所有操作

## 📝 更新日誌

- **2025-06-16**：實現自動拉取功能
- **2025-06-16**：添加requirements.txt支援
- **2025-06-16**：優化Docker構建流程
- **2025-06-16**：新增快速啟動模式

---

現在你可以確信每次使用 `./docker/docker-start.sh start` 都會獲得最新的代碼！🎉 