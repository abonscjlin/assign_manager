import os

def get_data_file_path(filename="result.csv"):
    """
    智能獲取數據文件的絕對路徑
    無論從哪個目錄運行，都能正確找到文件
    """
    if os.path.isabs(filename):
        return filename
    
    # 獲取當前模塊所在目錄（assign_manager）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

def get_result_file_path(filename):
    """
    獲取 result 目錄下文件的絕對路徑
    """
    if os.path.isabs(filename):
        return filename
    
    # 獲取當前模塊所在目錄（assign_manager）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.join(script_dir, "result")
    
    # 確保 result 目錄存在
    os.makedirs(result_dir, exist_ok=True)
    
    return os.path.join(result_dir, filename) 