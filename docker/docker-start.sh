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

# 檢查系統依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安裝，請先安裝Docker"
        exit 1
    fi
    
    # 檢查Docker Compose (新版本使用 docker compose)
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安裝或不支援，請先安裝Docker Compose"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git未安裝，請先安裝Git"
        exit 1
    fi
    
    log_success "系統依賴檢查完成"
}

# 準備本機目錄結構
prepare_directories() {
    log_info "準備本機目錄結構..."
    
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
        cd ..
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
    log_info "本機掛載目錄: $(pwd)/$LOCAL_DIR"
}

# 構建Docker映像
build_image() {
    log_info "構建Docker映像..."
    docker compose build --build-arg REPO_URL="$REPO_URL"
    log_success "Docker映像構建完成"
}

# 啟動服務
start_service() {
    log_info "啟動工作分配管理系統API服務..."
    docker compose up -d
    
    # 等待服務啟動
    log_info "等待服務啟動..."
    sleep 15
    
    # 檢查服務狀態
    if docker compose ps | grep -q "Up"; then
        log_success "服務啟動成功！"
        log_info "API服務地址: http://localhost:7777"
        log_info "健康檢查: http://localhost:7777/health"
        log_info "本機掛載目錄: $(pwd)/$LOCAL_DIR"
        log_info "結果輸出目錄: $(pwd)/$LOCAL_DIR/result"
        log_info "查看日誌: docker compose logs -f"
        
        # 嘗試健康檢查
        sleep 5
        if curl -f http://localhost:7777/health &> /dev/null; then
            log_success "API服務健康檢查通過"
        else
            log_warning "API服務可能尚未完全啟動，請稍候再試"
        fi
    else
        log_error "服務啟動失敗，請檢查日誌: docker compose logs"
        exit 1
    fi
}

# 停止服務
stop_service() {
    log_info "停止服務..."
    docker compose down
    log_success "服務已停止"
}

# 重啟服務
restart_service() {
    log_info "重啟服務..."
    docker compose restart
    log_success "服務重啟完成"
}

# 查看日誌
view_logs() {
    log_info "查看服務日誌..."
    docker compose logs -f
}

# 查看服務狀態
check_status() {
    log_info "檢查服務狀態..."
    docker compose ps
    
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
    docker compose down
    prepare_directories
    build_image
    start_service
}

# 清理資源
cleanup() {
    log_info "清理Docker資源..."
    docker compose down -v
    docker system prune -f
    log_success "清理完成"
    log_warning "注意: 本機 $LOCAL_DIR 目錄未被刪除"
}

# 顯示幫助信息
show_help() {
    echo "工作分配管理系統 - Docker管理腳本"
    echo "====================================="
    echo ""
    echo "使用方法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  start     準備目錄、構建並啟動服務"
    echo "  stop      停止服務"
    echo "  restart   重啟服務"
    echo "  status    查看服務狀態"
    echo "  logs      查看服務日誌"
    echo "  build     僅構建Docker映像"
    echo "  update    更新代碼"
    echo "  rebuild   重新構建並重啟服務"
    echo "  cleanup   清理Docker資源"
    echo "  help      顯示此幫助信息"
    echo ""
    echo "範例:"
    echo "  $0 start    # 一鍵啟動所有服務"
    echo "  $0 logs     # 查看服務日誌"
    echo "  $0 status   # 檢查服務狀態"
    echo "  $0 update   # 更新代碼"
    echo ""
    echo "GitHub倉庫: $REPO_URL"
    echo "本機目錄: $(pwd)/$LOCAL_DIR"
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
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            check_status
            ;;
        "logs")
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
            cleanup
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