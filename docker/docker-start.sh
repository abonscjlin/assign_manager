#!/bin/bash

# 工作分配管理系統 - Docker啟動腳本
# ===========================================

set -e

# 顏色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub倉庫配置
REPO_URL="https://github.com/abonscjlin/assign_manager.git"
LOCAL_DIR="assign_manager"

# Docker命令前綴
DOCKER_CMD=""
DOCKER_COMPOSE_CMD=""

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

# 檢查Docker權限並設置命令前綴
check_docker_permissions() {
    log_info "檢查Docker權限..."
    
    # 測試Docker命令是否需要sudo
    if docker info >/dev/null 2>&1; then
        log_success "Docker權限正常"
        DOCKER_CMD="docker"
        DOCKER_COMPOSE_CMD="docker compose"
    elif sudo docker info >/dev/null 2>&1; then
        log_warning "需要sudo權限運行Docker"
        DOCKER_CMD="sudo docker"
        DOCKER_COMPOSE_CMD="sudo docker compose"
    else
        log_error "Docker不可用或權限不足"
        log_info "請嘗試以下解決方案："
        log_info "1. 將用戶添加到docker組: sudo usermod -aG docker \$USER"
        log_info "2. 重新登錄或重啟系統"
        log_info "3. 或者確保Docker daemon正在運行"
        exit 1
    fi
}

# 獲取腳本目錄並切換到Docker目錄
get_docker_dir() {
    # 獲取腳本所在目錄
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    DOCKER_DIR="$SCRIPT_DIR"
    
    # 如果不在docker目錄中，尋找docker目錄
    if [[ ! -f "$DOCKER_DIR/docker-compose.yml" ]]; then
        if [[ -f "$SCRIPT_DIR/../docker-compose.yml" ]]; then
            DOCKER_DIR="$SCRIPT_DIR/.."
        elif [[ -f "$SCRIPT_DIR/docker/docker-compose.yml" ]]; then
            DOCKER_DIR="$SCRIPT_DIR/docker"
        else
            log_error "找不到docker-compose.yml文件"
            exit 1
        fi
    fi
    
    log_info "Docker配置目錄: $DOCKER_DIR"
    cd "$DOCKER_DIR"
}

# 檢查系統依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安裝，請先安裝Docker"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git未安裝，請先安裝Git"
        exit 1
    fi
    
    # 檢查Docker權限並設置命令前綴
    check_docker_permissions
    
    # 切換到Docker配置目錄
    get_docker_dir
    
    # 檢查Docker Compose (在權限檢查後)
    if ! $DOCKER_COMPOSE_CMD version &> /dev/null; then
        log_error "Docker Compose未安裝或不支援，請先安裝Docker Compose"
        log_info "嘗試安裝Docker Compose:"
        log_info "1. 官方安裝: https://docs.docker.com/compose/install/"
        log_info "2. 或使用包管理器: sudo apt-get install docker-compose-plugin"
        exit 1
    fi
    
    log_success "系統依賴檢查完成"
}

# 準備本機目錄結構
prepare_directories() {
    log_info "準備本機目錄結構..."
    
    # 回到原始工作目錄
    ORIGINAL_DIR="$(pwd)"
    if [[ "$ORIGINAL_DIR" == */docker ]]; then
        ORIGINAL_DIR="$(dirname "$ORIGINAL_DIR")"
    fi
    cd "$ORIGINAL_DIR"
    
    # 檢查並創建assign_manager目錄
    if [ ! -d "$LOCAL_DIR" ]; then
        log_info "創建 $LOCAL_DIR 目錄..."
        mkdir -p "$LOCAL_DIR"
    fi
    
    # 檢查並克隆/更新代碼
    if [ ! -d "$LOCAL_DIR/.git" ]; then
        log_info "從GitHub克隆代碼..."
        git clone "$REPO_URL" "$LOCAL_DIR"
    else
        log_info "更新現有代碼..."
        cd "$LOCAL_DIR"
        git pull origin main
        cd "$ORIGINAL_DIR"
    fi
    
    # 檢查並創建result目錄
    if [ ! -d "$LOCAL_DIR/result" ]; then
        log_info "創建 $LOCAL_DIR/result 目錄..."
        mkdir -p "$LOCAL_DIR/result"
    fi
    
    # 檢查必要文件是否存在
    if [ ! -f "$LOCAL_DIR/employee_list.csv" ]; then
        log_warning "$LOCAL_DIR/employee_list.csv 不存在，將創建預設文件"
        echo "id,name,type" > "$LOCAL_DIR/employee_list.csv"
        echo "S001,資深技師1,SENIOR" >> "$LOCAL_DIR/employee_list.csv"
        echo "S002,資深技師2,SENIOR" >> "$LOCAL_DIR/employee_list.csv"
        echo "J001,一般技師1,JUNIOR" >> "$LOCAL_DIR/employee_list.csv"
        echo "J002,一般技師2,JUNIOR" >> "$LOCAL_DIR/employee_list.csv"
    fi
    
    if [ ! -f "$LOCAL_DIR/result.csv" ]; then
        log_warning "$LOCAL_DIR/result.csv 不存在，將使用倉庫中的預設文件"
    fi
    
    log_success "目錄結構準備完成"
    log_info "本機掛載目錄: $ORIGINAL_DIR/$LOCAL_DIR"
    
    # 回到Docker配置目錄
    cd "$DOCKER_DIR"
}

# 構建Docker映像
build_image() {
    log_info "構建Docker映像..."
    $DOCKER_COMPOSE_CMD build --build-arg REPO_URL="$REPO_URL"
    log_success "Docker映像構建完成"
}

# 啟動服務
start_service() {
    log_info "啟動工作分配管理系統API服務..."
    $DOCKER_COMPOSE_CMD up -d
    
    # 等待服務啟動
    log_info "等待服務啟動..."
    sleep 15
    
    # 檢查服務狀態
    if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
        log_success "服務啟動成功！"
        log_info "API服務地址: http://localhost:7777"
        log_info "健康檢查: http://localhost:7777/health"
        log_info "本機掛載目錄: $(pwd)/$LOCAL_DIR"
        log_info "結果輸出目錄: $(pwd)/$LOCAL_DIR/result"
        log_info "查看日誌: $DOCKER_COMPOSE_CMD logs -f"
        
        # 嘗試健康檢查
        sleep 5
        if curl -f http://localhost:7777/health &> /dev/null; then
            log_success "API服務健康檢查通過"
        else
            log_warning "API服務可能尚未完全啟動，請稍候再試"
        fi
    else
        log_error "服務啟動失敗，請檢查日誌: $DOCKER_COMPOSE_CMD logs"
        exit 1
    fi
}

# 停止服務
stop_service() {
    log_info "停止服務..."
    $DOCKER_COMPOSE_CMD down
    log_success "服務已停止"
}

# 重啟服務
restart_service() {
    log_info "重啟服務..."
    $DOCKER_COMPOSE_CMD restart
    log_success "服務重啟完成"
}

# 查看日誌
view_logs() {
    log_info "查看服務日誌..."
    $DOCKER_COMPOSE_CMD logs -f
}

# 查看服務狀態
check_status() {
    log_info "檢查服務狀態..."
    $DOCKER_COMPOSE_CMD ps
    
    log_info "檢查本機目錄..."
    echo "本機掛載目錄: $(pwd)/$LOCAL_DIR"
    echo "結果輸出目錄: $(pwd)/$LOCAL_DIR/result"
    ls -la "$LOCAL_DIR/" 2>/dev/null || log_warning "$LOCAL_DIR 目錄不存在"
    
    # 檢查健康狀態
    if curl -f http://localhost:7777/health &> /dev/null; then
        log_success "API服務運行正常"
    else
        log_warning "API服務可能未正常運行"
    fi
}

# 更新代碼
update_code() {
    log_info "更新代碼..."
    if [ -d "$LOCAL_DIR/.git" ]; then
        cd "$LOCAL_DIR"
        git pull origin main
        cd ..
        log_success "代碼更新完成"
        log_info "請重新構建並重啟服務: $0 rebuild"
    else
        log_error "$LOCAL_DIR 不是一個Git倉庫"
        exit 1
    fi
}

# 重新構建並重啟
rebuild_and_restart() {
    log_info "重新構建並重啟服務..."
    $DOCKER_COMPOSE_CMD down
    prepare_directories
    build_image
    start_service
}

# 清理資源
cleanup() {
    log_info "清理Docker資源..."
    $DOCKER_COMPOSE_CMD down -v
    $DOCKER_CMD system prune -f
    log_success "清理完成"
    log_warning "注意: 本機 $LOCAL_DIR 目錄未被刪除"
}

# 修復Docker權限
fix_docker_permissions() {
    log_info "嘗試修復Docker權限..."
    log_info "將當前用戶添加到docker組..."
    
    if sudo usermod -aG docker $USER; then
        log_success "用戶已添加到docker組"
        log_warning "請重新登錄或重啟系統以使更改生效"
        log_info "或者運行: newgrp docker"
    else
        log_error "添加用戶到docker組失敗"
        exit 1
    fi
}

# 檢查Docker Compose安裝
check_compose_installation() {
    log_info "檢查Docker Compose安裝..."
    
    # 檢查不同的Docker Compose安裝方式
    if command -v docker-compose &> /dev/null; then
        log_info "發現 docker-compose (v1版本)"
        echo "Docker Compose v1版本: $(docker-compose --version)"
    fi
    
    if docker compose version &> /dev/null 2>&1; then
        log_info "發現 docker compose (v2版本)"
        echo "Docker Compose v2版本: $(docker compose version)"
    elif sudo docker compose version &> /dev/null 2>&1; then
        log_info "發現 docker compose (v2版本，需要sudo)"
        echo "Docker Compose v2版本 (sudo): $(sudo docker compose version)"
    fi
    
    # 提供安裝建議
    log_info "如果上述都沒有輸出，請安裝Docker Compose:"
    log_info "Ubuntu/Debian: sudo apt-get update && sudo apt-get install docker-compose-plugin"
    log_info "CentOS/RHEL: sudo yum install docker-compose-plugin"
    log_info "或參考官方文檔: https://docs.docker.com/compose/install/"
}

# 顯示幫助信息
show_help() {
    echo "工作分配管理系統 - Docker管理腳本"
    echo "====================================="
    echo ""
    echo "使用方法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  start       準備目錄、構建並啟動服務"
    echo "  stop        停止服務"
    echo "  restart     重啟服務"
    echo "  status      查看服務狀態"
    echo "  logs        查看服務日誌"
    echo "  build       僅構建Docker映像"
    echo "  update      更新代碼"
    echo "  rebuild     重新構建並重啟服務"
    echo "  cleanup     清理Docker資源"
    echo "  fix-perm    修復Docker權限問題"
    echo "  check-comp  檢查Docker Compose安裝"
    echo "  help        顯示此幫助信息"
    echo ""
    echo "範例:"
    echo "  $0 start        # 一鍵啟動所有服務"
    echo "  $0 logs         # 查看服務日誌"
    echo "  $0 status       # 檢查服務狀態"
    echo "  $0 update       # 更新代碼"
    echo "  $0 fix-perm     # 修復Docker權限"
    echo "  $0 check-comp   # 檢查Docker Compose"
    echo ""
    echo "GitHub倉庫: $REPO_URL"
    echo "本機目錄: $(pwd)/$LOCAL_DIR"
    echo ""
    echo "常見問題解決："
    echo "1. 權限問題: $0 fix-perm"
    echo "2. Compose問題: $0 check-comp"
    echo "3. 服務異常: $0 rebuild"
    echo "4. 清理重置: $0 cleanup && $0 start"
}

# 主函數
main() {
    case "${1:-start}" in
        "start")
            check_dependencies
            prepare_directories
            build_image
            start_service
            ;;
        "stop")
            check_dependencies
            stop_service
            ;;
        "restart")
            check_dependencies
            restart_service
            ;;
        "status")
            check_dependencies
            check_status
            ;;
        "logs")
            check_dependencies
            view_logs
            ;;
        "build")
            check_dependencies
            prepare_directories
            build_image
            ;;
        "update")
            update_code
            ;;
        "rebuild")
            check_dependencies
            rebuild_and_restart
            ;;
        "cleanup")
            check_dependencies
            cleanup
            ;;
        "fix-perm")
            fix_docker_permissions
            ;;
        "check-comp")
            check_compose_installation
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知選項: $1"
            show_help
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@" 