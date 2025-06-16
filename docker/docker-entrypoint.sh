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
    
    # 檢查是否已經有代碼目錄
    if [ -d "/app/.git" ]; then
        log_info "📂 發現現有代碼倉庫，嘗試更新..."
        cd /app
        
        # 獲取當前分支
        CURRENT_BRANCH=$(git branch --show-current)
        if [ -z "$CURRENT_BRANCH" ]; then
            CURRENT_BRANCH="main"
        fi
        
        log_info "🌿 當前分支: $CURRENT_BRANCH"
        
        # 保存本地修改（如果有）
        if ! git diff-index --quiet HEAD --; then
            log_warning "⚠️ 發現本地修改，將暫存..."
            git stash push -m "Auto-stash before container update $(date)"
        fi
        
        # 獲取遠程更新
        log_info "📥 獲取遠程更新..."
        git fetch origin
        
        # 檢查是否有更新
        LOCAL_COMMIT=$(git rev-parse HEAD)
        REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH 2>/dev/null || git rev-parse origin/main)
        
        if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
            log_info "🆕 發現遠程更新，正在拉取..."
            
            # 嘗試合併或重置
            if git pull origin $CURRENT_BRANCH; then
                log_success "✅ 代碼更新成功"
            else
                log_warning "⚠️ 合併失敗，嘗試硬重置..."
                git reset --hard origin/$CURRENT_BRANCH
                log_success "✅ 代碼重置到最新版本"
            fi
        else
            log_info "✅ 代碼已是最新版本"
        fi
        
        # 顯示當前提交信息
        log_info "📋 當前提交: $(git log --oneline -1)"
        
    else
        log_info "📥 首次運行，克隆代碼倉庫..."
        
        # 確保工作目錄是空的
        rm -rf /app/*
        rm -rf /app/.*
        
        # 克隆倉庫
        if git clone "$REPO_URL" /tmp/repo; then
            # 移動文件到工作目錄
            mv /tmp/repo/.git /app/
            mv /tmp/repo/* /app/ 2>/dev/null || true
            mv /tmp/repo/.* /app/ 2>/dev/null || true
            
            # 清理臨時目錄
            rm -rf /tmp/repo
            
            cd /app
            log_success "✅ 代碼克隆成功"
            log_info "📋 當前提交: $(git log --oneline -1)"
        else
            log_error "❌ 代碼克隆失敗"
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