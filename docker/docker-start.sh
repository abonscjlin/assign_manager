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
LOCAL_DIR="."

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

# 準備本機目錄結構並更新代碼
prepare_directories() {
    log_info "準備本機目錄結構並更新代碼..."
    
    # 回到原始工作目錄（項目根目錄）
    ORIGINAL_DIR="$(pwd)"
    if [[ "$ORIGINAL_DIR" == */docker ]]; then
        ORIGINAL_DIR="$(dirname "$ORIGINAL_DIR")"
    fi
    cd "$ORIGINAL_DIR"
    
    # 檢查當前目錄是否為Git倉庫
    if [ ! -d ".git" ]; then
        log_error "當前目錄不是Git倉庫！"
        log_info "請確保在正確的項目根目錄中運行此腳本"
        exit 1
    fi
    
    # 從GitHub拉取最新代碼
    log_info "從GitHub拉取最新代碼..."
    
    # 安全地拉取代碼（不破壞本地docker配置）
    git fetch origin
    
    # 檢查是否有遠程更新
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_info "發現遠程更新，嘗試合併..."
        # 保存docker目錄
        if [ -d "docker" ]; then
            cp -r docker docker_backup
        fi
        
        # 嘗試合併
        if git pull origin main; then
            log_info "成功合併遠程更新"
        else
            log_warning "合併失敗，恢復本地docker配置"
            if [ -d "docker_backup" ]; then
                rm -rf docker
                mv docker_backup docker
            fi
        fi
        
        # 清理備份
        rm -rf docker_backup
    else
        log_info "本地代碼已是最新"
    fi
    
    # 顯示當前提交
    log_info "當前提交: $(git log --oneline -1)"
    
    # 檢查並創建使用者目錄下的專用Docker目錄
    DOCKER_USER_DIR="$HOME/docker/assign_manager"
    if [ ! -d "$DOCKER_USER_DIR" ]; then
        log_info "創建專用Docker目錄: $DOCKER_USER_DIR..."
        mkdir -p "$DOCKER_USER_DIR"
    fi
    
    # 創建result子目錄
    if [ ! -d "$DOCKER_USER_DIR/result" ]; then
        log_info "創建result目錄: $DOCKER_USER_DIR/result..."
        mkdir -p "$DOCKER_USER_DIR/result"
    fi
    
    # 檢查並創建項目本地的result目錄（供開發使用）
    if [ ! -d "result" ]; then
        log_info "創建項目本地result目錄..."
        mkdir -p "result"
    fi
    
    # 同步輸入檔案到Docker專用目錄
    log_info "同步輸入檔案到Docker專用目錄..."
    
    # 同步employee_list.csv
    if [ -f "employee_list.csv" ]; then
        log_info "同步 employee_list.csv..."
        cp "employee_list.csv" "$DOCKER_USER_DIR/"
    else
        log_warning "employee_list.csv 不存在，將創建預設文件"
        echo "id,name,type" > "$DOCKER_USER_DIR/employee_list.csv"
        echo "S001,資深技師1,SENIOR" >> "$DOCKER_USER_DIR/employee_list.csv"
        echo "S002,資深技師2,SENIOR" >> "$DOCKER_USER_DIR/employee_list.csv"
        echo "J001,一般技師1,JUNIOR" >> "$DOCKER_USER_DIR/employee_list.csv"
        echo "J002,一般技師2,JUNIOR" >> "$DOCKER_USER_DIR/employee_list.csv"
    fi
    
    # 同步result.csv  
    if [ -f "result.csv" ]; then
        log_info "同步 result.csv..."
        cp "result.csv" "$DOCKER_USER_DIR/"
    else
        log_warning "result.csv 不存在，將使用倉庫中的預設文件或創建空文件"
        # 創建一個最小的CSV檔案以避免容器啟動錯誤
        echo "measure_record_oid,upload_end_time,promise_time,task_status,task_status_name,institution_id,data_effective_rate,num_af,num_pvc,num_sveb,delay_days,is_vip,is_top_job,is_simple_work,priority,actual_record_days,source_file,difficulty,x_value" > "$DOCKER_USER_DIR/result.csv"
    fi
    
    log_info "檔案同步完成"
    
    log_success "目錄結構準備完成"
    log_info "項目根目錄: $ORIGINAL_DIR"
    log_info "Docker專用目錄: $DOCKER_USER_DIR"
    
    # 回到Docker配置目錄
    cd "$DOCKER_DIR"
}

# 構建Docker映像
build_image() {
    log_info "構建Docker映像..."
    # 每次都重新構建以確保使用最新代碼
    $DOCKER_COMPOSE_CMD build --no-cache --build-arg REPO_URL="$REPO_URL"
    log_success "Docker映像構建完成"
}

# 快速構建Docker映像（不清除緩存）
build_image_fast() {
    log_info "快速構建Docker映像..."
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
        log_info "Docker專用目錄: $HOME/docker/assign_manager"
        log_info "結果輸出目錄: $HOME/docker/assign_manager/result"
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

# 快速啟動服務（使用緩存）
start_service_fast() {
    log_info "快速啟動服務（使用緩存）..."
    check_dependencies
    prepare_directories
    build_image_fast
    start_service
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
    
    log_info "檢查掛載目錄..."
    DOCKER_USER_DIR="$HOME/docker/assign_manager"
    echo "Docker專用目錄: $DOCKER_USER_DIR"
    echo "結果輸出目錄: $DOCKER_USER_DIR/result"
    echo "輸入檔案:"
    echo "  - employee_list.csv: $DOCKER_USER_DIR/employee_list.csv"
    echo "  - result.csv: $DOCKER_USER_DIR/result.csv"
    echo ""
    ls -la "$DOCKER_USER_DIR/" 2>/dev/null || log_warning "$DOCKER_USER_DIR 目錄不存在"
    
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
    log_warning "注意: Docker專用目錄 $HOME/docker/assign_manager 未被刪除"
}

# 完全清理系統（包括所有Docker資源）- 危險操作
clean_all() {
    log_warning "警告: 這將清理所有Docker資源，包括其他項目！"
    echo -n "確定要繼續嗎？輸入 'YES' 確認: "
    read -r confirmation
    
    if [ "$confirmation" != "YES" ]; then
        log_info "操作已取消"
        return 0
    fi
    
    log_info "執行完全系統清理..."
    $DOCKER_COMPOSE_CMD down -v
    $DOCKER_CMD system prune -af --volumes
    log_success "完全系統清理完成"
}

# 完全清理並重建
clean() {
    log_info "完全清理assign-manager容器和映像..."
    
    # 停止並移除容器和網絡
    log_info "停止並移除assign-manager容器和網絡..."
    $DOCKER_COMPOSE_CMD down -v
    
    # 移除相關映像
    log_info "移除assign-manager相關映像..."
    IMAGES=$($DOCKER_CMD images --format "{{.Repository}}:{{.Tag}}" | grep -E "(assign-manager|docker-assign-manager)" || true)
    
    if [ -n "$IMAGES" ]; then
        echo "找到以下相關映像："
        echo "$IMAGES"
        
        for IMAGE in $IMAGES; do
            log_info "移除映像: $IMAGE"
            $DOCKER_CMD rmi "$IMAGE" || log_warning "無法移除映像: $IMAGE"
        done
    else
        log_info "未找到assign-manager相關映像"
    fi
    
    # 清理未使用的網絡（僅限docker_default等相關網絡）
    log_info "清理項目相關的未使用網絡..."
    NETWORKS=$($DOCKER_CMD network ls --format "{{.Name}}" | grep -E "(docker_default|assign.*manager)" || true)
    
    if [ -n "$NETWORKS" ]; then
        for NETWORK in $NETWORKS; do
            log_info "移除網絡: $NETWORK"
            $DOCKER_CMD network rm "$NETWORK" 2>/dev/null || log_warning "無法移除網絡: $NETWORK (可能仍在使用中)"
        done
    fi
    
    log_success "完全清理完成"
    log_info "現在可以運行 '$0 start' 來啟動全新的容器"
    log_warning "注意: 僅清理了assign-manager相關的容器和映像，其他Docker資源未受影響"
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
    echo "  start       拉取最新代碼、完全重建並啟動服務（推薦）"
    echo "  start-fast  快速啟動服務（使用Docker緩存）"
    echo "  stop        停止服務"
    echo "  restart     重啟服務"
    echo "  status      查看服務狀態"
    echo "  logs        查看服務日誌"
    echo "  build       重新構建Docker映像（不使用緩存）"
    echo "  build-fast  快速構建Docker映像（使用緩存）"
    echo "  update      僅更新代碼"
    echo "  rebuild     重新構建並重啟服務"
    echo "  cleanup     清理Docker資源"
    echo "  clean       完全清理assign-manager容器和映像"
    echo "  clean-all   清理所有Docker資源（危險操作）"
    echo "  fix-perm    修復Docker權限問題"
    echo "  check-comp  檢查Docker Compose安裝"
    echo "  help        顯示此幫助信息"
    echo ""
    echo "範例:"
    echo "  $0 start        # 拉取最新代碼並完全重建（推薦）"
    echo "  $0 start-fast   # 快速啟動（開發時使用）"
    echo "  $0 logs         # 查看服務日誌"
    echo "  $0 status       # 檢查服務狀態"
    echo "  $0 update       # 僅更新代碼"
    echo "  $0 clean        # 清理assign-manager相關資源"
    echo "  $0 clean-all    # 清理所有Docker資源（危險）"
    echo "  $0 fix-perm     # 修復Docker權限"
    echo ""
    echo "GitHub倉庫: $REPO_URL"
    echo "Docker專用目錄: $HOME/docker/assign_manager"
    echo ""
    echo "常見問題解決："
    echo "1. 權限問題: $0 fix-perm"
    echo "2. Compose問題: $0 check-comp"
    echo "3. 服務異常: $0 rebuild"
    echo "4. 完全重置: $0 clean && $0 start"
    echo "5. 清理資源: $0 cleanup"
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
        "start-fast")
            start_service_fast
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
        "build-fast")
            check_dependencies
            prepare_directories
            build_image_fast
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
        "clean")
            check_dependencies
            clean
            ;;
        "clean-all")
            check_dependencies
            clean_all
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