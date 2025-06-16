# Docker 自動拉取功能說明

## 🔄 概述

工作分配管理系統的Docker配置已經增強，現在支持每次容器啟動時自動檢查並拉取最新代碼，確保始終運行最新版本。

## 🚀 功能特點

### 1. **智能代碼更新**
- ✅ 每次容器啟動時自動檢查GitHub倉庫
- ✅ 如果發現更新，自動拉取最新代碼
- ✅ 如果是首次運行，自動克隆整個倉庫
- ✅ 支持分支切換和配置

### 2. **安全的更新機制**
- 🔒 本地修改會被自動暫存（git stash）
- 🔒 更新失敗時自動回滾
- 🔒 保留容器配置和數據不變

### 3. **持久化存儲**
- 💾 Git歷史使用Docker Volume持久化
- 💾 結果文件掛載到宿主機目錄
- 💾 容器重啟時保持代碼狀態

## 🛠️ 使用方法

### 基本操作

```bash
# 啟動服務（自動拉取最新代碼）
./docker-start.sh start

# 快速啟動（使用緩存）
./docker-start.sh start-fast

# 強制更新代碼並重啟
./docker-start.sh update

# 查看服務狀態
./docker-start.sh status

# 查看日誌
./docker-start.sh logs
```

### 強制更新操作

```bash
# 強制更新代碼（會重新克隆倉庫）
./docker-start.sh update

# 完全清理並重新開始
./docker-start.sh clean
./docker-start.sh start
```

## 🔧 配置選項

### 環境變數配置

可以通過環境變數自定義倉庫和分支：

```bash
# 使用不同的倉庫
export REPO_URL="https://github.com/your-username/assign_manager.git"
./docker-start.sh start

# 使用不同的分支
export GIT_BRANCH="development"
./docker-start.sh start

# 一次性設置
REPO_URL="https://github.com/your-fork/assign_manager.git" GIT_BRANCH="feature-branch" ./docker-start.sh start
```

### Docker Compose配置

在 `docker-compose.yml` 中的相關配置：

```yaml
environment:
  - REPO_URL=${REPO_URL:-https://github.com/abonscjlin/assign_manager.git}
  - GIT_BRANCH=${GIT_BRANCH:-main}

volumes:
  # 持久化Git歷史
  - assign_manager_code:/app/.git
```

## 📋 更新流程詳解

### 容器啟動時的自動更新流程：

1. **檢查Git倉庫**
   ```
   📂 檢查 /app/.git 是否存在
   ```

2. **存在倉庫的情況**
   ```
   🔄 git fetch origin
   📊 比較本地和遠程提交
   🆕 發現更新時自動拉取
   ✅ 顯示當前提交信息
   ```

3. **首次運行的情況**
   ```
   📥 git clone 完整倉庫
   📁 設置工作目錄
   ✅ 顯示初始提交信息
   ```

4. **依賴安裝**
   ```
   📋 檢查 requirements.txt
   📦 自動安裝Python依賴
   ✅ 準備運行環境
   ```

5. **服務啟動**
   ```
   🌐 啟動API服務器
   🏥 健康檢查就緒
   📡 服務可用於外部調用
   ```

## 🚨 故障排除

### 常見問題和解決方案

#### 1. **代碼更新失敗**
```bash
# 查看詳細日誌
./docker-start.sh logs

# 強制重新克隆
./docker-start.sh update
```

#### 2. **權限問題**
```bash
# 修復Docker權限
./docker-start.sh fix-perm

# 或手動添加到docker組
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. **容器無法啟動**
```bash
# 檢查服務狀態
./docker-start.sh status

# 重建容器
./docker-start.sh rebuild

# 完全清理重新開始
./docker-start.sh clean
./docker-start.sh start
```

#### 4. **網絡連接問題**
```bash
# 檢查網絡連接
curl -I https://github.com

# 使用替代倉庫地址
export REPO_URL="https://ghproxy.com/https://github.com/abonscjlin/assign_manager.git"
./docker-start.sh start
```

## 📊 監控和日誌

### 查看更新日誌
```bash
# 實時查看容器日誌
./docker-start.sh logs

# 查看最近的日誌
docker logs assign-manager-api --tail 50

# 查看特定時間的日誌
docker logs assign-manager-api --since "1h"
```

### 檢查代碼版本
```bash
# 進入容器檢查
docker exec -it assign-manager-api bash
cd /app
git log --oneline -5
```

## 🔐 安全注意事項

1. **敏感信息**：環境變數和配置文件不會被Git追蹤
2. **網絡安全**：僅通過HTTPS克隆公開倉庫
3. **數據隔離**：容器數據與宿主機適當隔離
4. **權限控制**：使用最小權限原則

## 📈 性能優化

### 1. **緩存策略**
- 使用Docker Volume緩存Git歷史
- Python依賴緩存在映像層中
- 支持快速啟動模式

### 2. **網絡優化**
- 僅在檢測到更新時才拉取代碼
- 支持增量更新
- 可配置代理或鏡像源

### 3. **資源管理**
- 容器自動重啟策略
- 日誌大小限制
- 健康檢查機制

## 🎯 最佳實踐

1. **定期更新**：建議定期重啟容器以獲取最新代碼
2. **監控日誌**：關注更新過程的日誌輸出
3. **備份配置**：保留重要的配置文件備份
4. **測試環境**：在生產環境前先在測試環境驗證更新

## 🔗 相關文件

- `Dockerfile` - 容器構建配置
- `docker-compose.yml` - 服務編排配置  
- `docker-entrypoint.sh` - 容器啟動腳本
- `docker-start.sh` - 管理腳本
- `Docker部署說明.md` - 部署指南 