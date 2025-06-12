# 工作排程分析系統 - 參數配置檔案

# 導入模組
try:
    from employee_manager import get_actual_employee_counts
except ImportError:
    # 在初始化階段可能尚未建立employee_manager模組
    get_actual_employee_counts = None

# ===== 人力配置參數 =====
SENIOR_WORKERS = 5           # 資深員工人數
JUNIOR_WORKERS = 10          # 一般員工人數
WORK_HOURS_PER_DAY = 8 * 60  # 每人每日工時(分鐘)

# ===== 外部員工名單參數 =====
# 外部員工名單JSON格式範例：
# {
#     "senior_workers": ["張三", "李四", "王五"],
#     "junior_workers": ["陳六", "林七", "黃八", "周九", "吳十"]
# }
EXTERNAL_WORKER_LIST_FILE = "employee_list.csv"  # 外部員工名單CSV檔案
USE_EXTERNAL_WORKER_LIST = True  # 是否使用外部員工名單

# ===== 工作目標參數 =====
MINIMUM_WORK_TARGET = 300    # 每日最低工作完成目標

# ===== 工作時間參數 =====
# 資深員工各難度所需時間(分鐘)
SENIOR_TIME = {
    1: 60,  # 難度1：60分鐘
    2: 50,  # 難度2：50分鐘  
    3: 40,  # 難度3：40分鐘
    4: 30,  # 難度4：30分鐘
    5: 20,  # 難度5：20分鐘
    6: 10,  # 難度6：10分鐘
    7: 5    # 難度7：5分鐘
}

# 一般員工需要1.5倍時間
JUNIOR_TIME = {k: int(v * 1.5) for k, v in SENIOR_TIME.items()}

# ===== 優先權設定 =====
HIGH_PRIORITY_LEVELS = [1]      # 高優先權（必須100%完成）
MEDIUM_PRIORITY_LEVELS = [2, 3, 4, 5]  # 中優先權
LOW_PRIORITY_LEVELS = [6]       # 低優先權（可延後處理）

# ===== 難度分類 =====
HIGH_DIFFICULTY_LEVELS = [1, 2, 3]     # 高難度工作
MEDIUM_DIFFICULTY_LEVELS = [4, 5]      # 中難度工作  
LOW_DIFFICULTY_LEVELS = [6, 7]         # 低難度工作

# ===== 顯示參數 =====
def print_config():
    """顯示當前配置參數"""
    print("="*50)
    print("📋 當前系統配置參數")
    print("="*50)
    print(f"👥 人力配置:")
    print(f"   資深員工: {SENIOR_WORKERS} 人")
    print(f"   一般員工: {JUNIOR_WORKERS} 人")
    print(f"   每人日工時: {WORK_HOURS_PER_DAY} 分鐘")
    print(f"")
    print(f"🎯 工作目標:")
    print(f"   每日最低完成: {MINIMUM_WORK_TARGET} 件")
    print(f"")
    print(f"⏱️ 作業時間:")
    print(f"   資深員工時間: {SENIOR_TIME}")
    print(f"   一般員工時間: {JUNIOR_TIME}")
    print("="*50)

def get_runtime_config():
    """
    獲取運行時配置，包括實際員工數量
    
    Returns:
        dict: 包含所有配置參數的字典
    """
    try:
        if get_actual_employee_counts is not None:
            actual_senior_count, actual_junior_count = get_actual_employee_counts()
        else:
            from employee_manager import get_actual_employee_counts
            actual_senior_count, actual_junior_count = get_actual_employee_counts()
        
        return {
            'senior_workers': actual_senior_count,
            'junior_workers': actual_junior_count,
            'minimum_work_target': MINIMUM_WORK_TARGET,
            'work_hours_per_day': WORK_HOURS_PER_DAY,
            'senior_time': SENIOR_TIME,
            'junior_time': JUNIOR_TIME,
            'use_external_worker_list': USE_EXTERNAL_WORKER_LIST,
            'external_worker_list_file': EXTERNAL_WORKER_LIST_FILE
        }
    except ImportError:
        # 回退到預設值
        return {
            'senior_workers': SENIOR_WORKERS,
            'junior_workers': JUNIOR_WORKERS,
            'minimum_work_target': MINIMUM_WORK_TARGET,
            'work_hours_per_day': WORK_HOURS_PER_DAY,
            'senior_time': SENIOR_TIME,
            'junior_time': JUNIOR_TIME,
            'use_external_worker_list': USE_EXTERNAL_WORKER_LIST,
            'external_worker_list_file': EXTERNAL_WORKER_LIST_FILE
        }

def print_runtime_config():
    """打印運行時配置信息"""
    config = get_runtime_config()
    print(f"   資深員工: {config['senior_workers']} 人")
    print(f"   一般員工: {config['junior_workers']} 人")
    print(f"   工作目標: {config['minimum_work_target']} 件")
    print(f"   日工時: {config['work_hours_per_day']} 分鐘")
    return config

if __name__ == "__main__":
    print_config() 