#!/bin/bash

# 工作分配管理系統 - Docker Entrypoint 腳本
# ===============================================

set -e

# 顏色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 設置默認倉庫URL
DEFAULT_REPO_URL="https://github.com/abonscjlin/assign_manager.git"
REPO_URL=${REPO_URL:-$DEFAULT_REPO_URL}

log_info "🚀 工作分配管理系統 Docker 容器啟動中..."
log_info "📦 倉庫地址: $REPO_URL"

# 檢查並更新代碼
update_code() {
    log_info "🔄 檢查並更新代碼..."
    
    # 檢查是否已經有有效的Git倉庫
    cd /app
    if [ -d "/app/.git" ] && git rev-parse --git-dir >/dev/null 2>&1; then
        log_info "📂 發現現有代碼倉庫，嘗試更新..."
        
        # 獲取當前分支
        CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
        if [ -z "$CURRENT_BRANCH" ]; then
            CURRENT_BRANCH="main"
        fi
        
        log_info "🌿 當前分支: $CURRENT_BRANCH"
        
        # 保存本地修改（如果有）
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            log_warning "⚠️ 發現本地修改，將暫存..."
            git stash push -m "Auto-stash before container update $(date)" 2>/dev/null || true
        fi
        
        # 獲取遠程更新
        log_info "📥 獲取遠程更新..."
        if ! git fetch origin 2>/dev/null; then
            log_warning "⚠️ 無法獲取遠程更新，可能網絡問題，繼續使用本地代碼"
            log_info "📋 當前提交: $(git log --oneline -1 2>/dev/null || echo '無法獲取提交信息')"
            return 0
        fi
        
        # 檢查是否有更新
        LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null)
        REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH 2>/dev/null || git rev-parse origin/main 2>/dev/null)
        
        if [ -n "$LOCAL_COMMIT" ] && [ -n "$REMOTE_COMMIT" ] && [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
            log_info "🆕 發現遠程更新，正在拉取..."
            
            # 嘗試合併或重置
            if git pull origin $CURRENT_BRANCH 2>/dev/null; then
                log_success "✅ 代碼更新成功"
            else
                log_warning "⚠️ 合併失敗，嘗試硬重置..."
                if git reset --hard origin/$CURRENT_BRANCH 2>/dev/null; then
                    log_success "✅ 代碼重置到最新版本"
                else
                    log_warning "⚠️ 重置失敗，繼續使用當前代碼"
                fi
            fi
        else
            log_info "✅ 代碼已是最新版本"
        fi
        
        # 顯示當前提交信息
        log_info "📋 當前提交: $(git log --oneline -1 2>/dev/null || echo '無法獲取提交信息')"
        
    else
        log_info "📥 首次運行或Git倉庫損壞/未初始化，準備克隆代碼倉庫..."

        # 如果 /app/.git 存在並且是一個目錄 (通常是volume掛載點)，則清空其內容
        # 這樣可以保留掛載點，同時為新的 .git 數據做準備
        if [ -d "/app/.git" ]; then
            log_info "🧹 清理現有的 /app/.git 目錄內容 (保留掛載點)..."
            # 使用 find 刪除內容，避免直接 rm -rf 掛載點
            find "/app/.git/" -mindepth 1 -delete 2>/dev/null || true
        fi

        # 清理 /app 目錄下的其他文件和目錄，但要小心保留 .git 掛載點本身
        log_info "🧹 清理 /app 工作目錄 (保留 .git 掛載點)..."
        # 使用 find 刪除 /app 下的內容，除了 .git 目錄本身及其內容
        find /app -mindepth 1 -not -path "/app/.git" -not -path "/app/.git/*" -delete 2>/dev/null || true

        log_info "📥 克隆倉庫 (分支: ${GIT_BRANCH:-main}) 到臨時目錄 /tmp/repo..."
        # 使用 GIT_BRANCH 環境變量，如果未設置則默認為 main
        # 克隆特定分支，使用 --depth 1 進行淺克隆以加快速度
        if git clone --depth 1 --branch "${GIT_BRANCH:-main}" "$REPO_URL" /tmp/repo; then
            log_info "🚚 移動代碼到 /app..."

            # 將克隆的 .git 目錄內容移動到 /app/.git (掛載點)
            if [ -d "/app/.git" ]; then
                log_info "🧬 移動 .git 數據到掛載的 /app/.git..."
                # 確保目標是空的 (已被上面的find清理過，但再次確認)
                find "/app/.git/" -mindepth 1 -delete 2>/dev/null || true 
                # 移動 .git 的內容 (包括隱藏文件)
                shopt -s dotglob
                mv /tmp/repo/.git/* "/app/.git/" 2>/dev/null || true
                shopt -u dotglob
                log_info "✅ .git 數據成功移動到 /app/.git"
            else
                # 如果 /app/.gits 不是預期的掛載點 (理論上不應發生)
                # 則直接移動整個 .git 目錄
                log_warning "⚠️ /app/.git 不是預期掛載點，將移動整個 .git 目錄"
                mv /tmp/repo/.git /app/
            fi

            # 移動應用程式文件 (除了.git目錄本身)
            log_info "📄 移動應用程式檔案..."
            # 確保 /app 目錄存在
            mkdir -p /app
            # 先將 /tmp/repo 下的非 .git 內容複製到 /app
            # 使用 rsync 可以更好地處理目錄和文件
            rsync -av --exclude='.git' /tmp/repo/ /app/ 2>/dev/null || true
            
            # 清理臨時目錄
            rm -rf /tmp/repo

            cd /app
            # 驗證現在 /app 是否為有效的Git倉庫
            if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
                log_success "✅ 代碼克隆並設置成功"
                log_info "🌿 當前分支: $(git branch --show-current 2>/dev/null || echo '無法確定分支')"
                log_info "📋 當前提交: $(git log --oneline -1 2>/dev/null || echo '無法獲取提交信息')"
            else
                log_error "❌ 克隆後 /app 不是有效的Git倉庫。請檢查volume掛載和權限。"
                # 可以考慮列出/app和/app/.git的內容以供調試
                ls -la /app
                if [ -d /app/.git ]; then ls -la /app/.git; fi
                exit 1
            fi
        else
            log_error "❌ 代碼克隆失敗 (git clone --depth 1 --branch '${GIT_BRANCH:-main}' '$REPO_URL' /tmp/repo)"
            exit 1
        fi
    fi
}

# 安裝Python依賴
install_dependencies() {
    log_info "📦 安裝Python依賴..."
    cd /app
    
    # 按優先順序安裝依賴
    if [ -f "requirements.txt" ]; then
        log_info "📋 使用 requirements.txt 安裝依賴"
        pip install --no-cache-dir -r requirements.txt
    elif [ -f "setup.py" ]; then
        log_info "📋 使用 setup.py 安裝依賴"
        pip install --no-cache-dir pandas numpy flask flask-cors requests
        pip install --no-cache-dir -e .
    else
        log_info "📋 手動安裝基本依賴"
        pip install --no-cache-dir pandas numpy flask flask-cors requests
    fi
    
    log_success "✅ Python依賴安裝完成"
}

# 檢查必要文件
check_files() {
    log_info "🔍 檢查必要文件..."
    cd /app
    
    # 檢查API服務器文件
    if [ ! -f "server/api_server.py" ]; then
        log_error "❌ API服務器文件不存在: server/api_server.py"
        exit 1
    fi
    
    # 檢查配置文件
    if [ ! -f "config_params.py" ]; then
        log_warning "⚠️ 配置文件不存在: config_params.py"
    fi
    
    # 創建result目錄（如果不存在）
    if [ ! -d "result" ]; then
        log_info "📁 創建result目錄"
        mkdir -p result
    fi
    
    log_success "✅ 文件檢查完成"
}

# 主要流程
main() {
    log_info "🏁 開始容器初始化流程..."
    
    # 1. 更新代碼
    update_code
    
    # 2. 安裝依賴
    install_dependencies
    
    # 3. 檢查文件
    check_files
    
    # 4. 啟動API服務
    log_info "🌐 啟動API服務..."
    log_success "✅ 容器初始化完成，啟動API服務"
    log_info "📡 API服務地址: http://localhost:7777"
    log_info "🏥 健康檢查: http://localhost:7777/health"
    
    # 啟動Python API服務器
    cd /app
    exec python server/api_server.py
}

# 執行主要流程
main "$@" 