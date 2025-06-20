# 工作排程分析系統 - 參數配置檔案

# 導入模組
try:
    from employee_manager import get_actual_employee_counts
except ImportError:
    # 在初始化階段可能尚未建立employee_manager模組
    get_actual_employee_counts = None

# ===== 人力配置參數 =====
# 預設值，如果無法讀取實際技師名單時使用
DEFAULT_SENIOR_WORKERS = 5           # 預設資深技師人數
DEFAULT_JUNIOR_WORKERS = 10          # 預設一般技師人數
WORK_HOURS_PER_DAY = 8 * 60         # 每人每日工時(分鐘)

# 動態獲取實際技師數量
def get_dynamic_worker_counts(external_senior_count=None, external_junior_count=None):
    """
    動態獲取技師數量，優先順序：
    1. 外部API傳入的參數
    2. 從employee_list.csv讀取的實際數量
    3. 預設配置值
    
    Args:
        external_senior_count: API傳入的資深技師數量
        external_junior_count: API傳入的一般技師數量
    
    Returns:
        tuple: (senior_count, junior_count)
    """
    # 如果API有傳入參數，優先使用
    if external_senior_count is not None and external_junior_count is not None:
        return external_senior_count, external_junior_count
    
    # 嘗試從實際技師名單讀取
    try:
        # 嘗試使用全局已導入的函數或動態導入
        try:
            if 'get_actual_employee_counts' in globals() and get_actual_employee_counts is not None:
                actual_senior_count, actual_junior_count = get_actual_employee_counts()
            else:
                from employee_manager import get_actual_employee_counts as get_counts
                actual_senior_count, actual_junior_count = get_counts()
                
            # 如果只有部分API參數，混合使用
            senior_count = external_senior_count if external_senior_count is not None else actual_senior_count
            junior_count = external_junior_count if external_junior_count is not None else actual_junior_count
            
            return senior_count, junior_count
        except ImportError:
            # 無法讀取實際技師數量，使用預設值與API參數
            senior_count = external_senior_count if external_senior_count is not None else DEFAULT_SENIOR_WORKERS
            junior_count = external_junior_count if external_junior_count is not None else DEFAULT_JUNIOR_WORKERS
            return senior_count, junior_count
    except Exception:
        # 任何其他錯誤，回退到預設值
        senior_count = external_senior_count if external_senior_count is not None else DEFAULT_SENIOR_WORKERS
        junior_count = external_junior_count if external_junior_count is not None else DEFAULT_JUNIOR_WORKERS
        return senior_count, junior_count

# 為了向後相容性，保留原有變數名稱，但現在它們會動態計算
try:
    SENIOR_WORKERS, JUNIOR_WORKERS = get_dynamic_worker_counts()
except:
    SENIOR_WORKERS = DEFAULT_SENIOR_WORKERS
    JUNIOR_WORKERS = DEFAULT_JUNIOR_WORKERS

# ===== 外部技師名單參數 =====
# 外部技師名單JSON格式範例：
# {
#     "senior_workers": ["張三", "李四", "王五"],
#     "junior_workers": ["陳六", "林七", "黃八", "周九", "吳十"]
# }
EXTERNAL_WORKER_LIST_FILE = "employee_list.csv"  # 外部技師名單CSV檔案
USE_EXTERNAL_WORKER_LIST = True  # 是否使用外部技師名單

# ===== 工作目標參數 =====
MINIMUM_WORK_TARGET = 300    # 每日最低工作完成目標

# ===== 工作時間參數 =====
# 資深技師各難度所需時間(分鐘) - 難度1為最簡單，7為最難
SENIOR_TIME = {
    1: 5,   # 難度1（最簡單）：5分鐘
    2: 10,  # 難度2：10分鐘  
    3: 20,  # 難度3：20分鐘
    4: 30,  # 難度4：30分鐘
    5: 40,  # 難度5：40分鐘
    6: 50,  # 難度6：50分鐘
    7: 60   # 難度7（最難）：60分鐘
}

# 一般技師需要1.5倍時間
JUNIOR_TIME = {k: int(v * 1.5) for k, v in SENIOR_TIME.items()}

# ===== 優先權設定 =====
HIGH_PRIORITY_LEVELS = [1]      # 高優先權（必須100%完成）
MEDIUM_PRIORITY_LEVELS = [2, 3, 4, 5]  # 中優先權
LOW_PRIORITY_LEVELS = [6]       # 低優先權（可延後處理）

# ===== 難度分類 =====
LOW_DIFFICULTY_LEVELS = [1, 2, 3]      # 低難度工作（簡單）
MEDIUM_DIFFICULTY_LEVELS = [4, 5]      # 中難度工作  
HIGH_DIFFICULTY_LEVELS = [6, 7]        # 高難度工作（複雜）

# ===== 顯示參數 =====
def print_config():
    """顯示當前配置參數"""
    print("="*50)
    print("📋 當前系統配置參數")
    print("="*50)
    print(f"👥 人力配置:")
    print(f"   資深技師: {SENIOR_WORKERS} 人")
    print(f"   一般技師: {JUNIOR_WORKERS} 人")
    print(f"   每人日工時: {WORK_HOURS_PER_DAY} 分鐘")
    print(f"")
    print(f"🎯 工作目標:")
    print(f"   每日最低完成: {MINIMUM_WORK_TARGET} 件")
    print(f"")
    print(f"⏱️ 作業時間:")
    print(f"   資深技師時間: {SENIOR_TIME}")
    print(f"   一般技師時間: {JUNIOR_TIME}")
    print("="*50)

def get_runtime_config(external_senior_count=None, external_junior_count=None):
    """
    獲取運行時配置，支持外部參數
    
    Args:
        external_senior_count: API傳入的資深技師數量
        external_junior_count: API傳入的一般技師數量
    
    Returns:
        dict: 包含所有配置參數的字典
    """
    # 使用動態技師數量計算
    senior_count, junior_count = get_dynamic_worker_counts(external_senior_count, external_junior_count)
    
    return {
        'senior_workers': senior_count,
        'junior_workers': junior_count,
        'minimum_work_target': MINIMUM_WORK_TARGET,
        'work_hours_per_day': WORK_HOURS_PER_DAY,
        'senior_time': SENIOR_TIME,
        'junior_time': JUNIOR_TIME,
        'use_external_worker_list': USE_EXTERNAL_WORKER_LIST,
        'external_worker_list_file': EXTERNAL_WORKER_LIST_FILE,
        'source': {
            'senior_workers_source': 'external_api' if external_senior_count is not None else 'employee_list_csv',
            'junior_workers_source': 'external_api' if external_junior_count is not None else 'employee_list_csv'
        }
    }

def print_runtime_config():
    """打印運行時配置信息"""
    config = get_runtime_config()
    print(f"   資深技師: {config['senior_workers']} 人")
    print(f"   一般技師: {config['junior_workers']} 人")
    print(f"   工作目標: {config['minimum_work_target']} 件")
    print(f"   日工時: {config['work_hours_per_day']} 分鐘")
    return config

if __name__ == "__main__":
    print_config() 