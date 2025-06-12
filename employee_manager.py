#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
員工管理模組
===========

負責處理外部員工名單的讀取、解析和管理功能。

功能包括：
1. 從CSV檔案讀取員工名單
2. 將員工名單轉換為JSON格式
3. 驗證員工名單格式
4. 生成測試用員工名單
"""

import pandas as pd
import json
import os
from typing import Dict, List, Tuple
import config_params
from config_params import EXTERNAL_WORKER_LIST_FILE, USE_EXTERNAL_WORKER_LIST, SENIOR_WORKERS, JUNIOR_WORKERS

class EmployeeManager:
    """員工管理器"""
    
    def __init__(self, csv_file_path: str = None):
        """初始化員工管理器
        
        Args:
            csv_file_path: CSV檔案路徑，如果為None則使用config中的預設路徑
        """
        if csv_file_path is None:
            # 使用相對於腳本目錄的路徑
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_dir, EXTERNAL_WORKER_LIST_FILE)
        
        self.csv_file_path = csv_file_path
        self.employee_data = None
    
    def load_employee_list_from_csv(self) -> Dict[str, List[str]]:
        """從CSV檔案讀取員工名單
        
        Returns:
            Dict包含senior_workers和junior_workers的列表
        """
        try:
            if not os.path.exists(self.csv_file_path):
                raise FileNotFoundError(f"找不到員工名單檔案: {self.csv_file_path}")
            
            df = pd.read_csv(self.csv_file_path, encoding='utf-8')
            
            # 驗證必要的欄位
            required_columns = ['name', 'type']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"CSV檔案缺少必要欄位: {col}")
            
            # 分離資深員工和一般員工
            senior_workers = df[df['type'].str.upper() == 'SENIOR']['name'].tolist()
            junior_workers = df[df['type'].str.upper() == 'JUNIOR']['name'].tolist()
            
            self.employee_data = {
                'senior_workers': senior_workers,
                'junior_workers': junior_workers
            }
            
            print(f"✅ 成功讀取員工名單:")
            print(f"   資深員工: {len(senior_workers)} 人")
            print(f"   一般員工: {len(junior_workers)} 人")
            
            return self.employee_data
            
        except Exception as e:
            print(f"❌ 讀取員工名單失敗: {e}")
            raise
    
    def get_employee_json(self) -> str:
        """取得員工名單的JSON格式
        
        Returns:
            JSON字符串格式的員工名單
        """
        if self.employee_data is None:
            self.load_employee_list_from_csv()
        
        return json.dumps(self.employee_data, ensure_ascii=False, indent=2)
    
    def get_employee_dict(self) -> Dict[str, List[str]]:
        """取得員工名單的字典格式
        
        Returns:
            包含員工名單的字典
        """
        if self.employee_data is None:
            self.load_employee_list_from_csv()
        
        return self.employee_data
    
    def validate_employee_counts(self) -> Tuple[bool, str]:
        """驗證員工數量和格式
        
        Returns:
            (是否有效, 驗證訊息)
        """
        if self.employee_data is None:
            self.load_employee_list_from_csv()
        
        senior_count = len(self.employee_data['senior_workers'])
        junior_count = len(self.employee_data['junior_workers'])
        
        # 基本驗證：至少要有員工
        if senior_count == 0 and junior_count == 0:
            return False, "員工名單為空，至少需要一名員工"
        
        # 提供信息性驗證結果，不再強制要求符合config參數
        message = f"員工名單驗證完成 - 資深員工: {senior_count}人, 一般員工: {junior_count}人, 總計: {senior_count + junior_count}人"
        
        # 如果與config參數不符，給予提示但不判為錯誤
        if senior_count != SENIOR_WORKERS or junior_count != JUNIOR_WORKERS:
            message += f" (注意: config中設定為資深{SENIOR_WORKERS}人/一般{JUNIOR_WORKERS}人，將以實際名單為準)"
        
        return True, message
    
    def get_employee_counts(self) -> Tuple[int, int]:
        """取得員工數量
        
        Returns:
            (資深員工數量, 一般員工數量)
        """
        if self.employee_data is None:
            self.load_employee_list_from_csv()
        
        return len(self.employee_data['senior_workers']), len(self.employee_data['junior_workers'])
    
    def get_worker_lists(self) -> Tuple[List[str], List[str]]:
        """取得員工名單列表
        
        Returns:
            (資深員工列表, 一般員工列表)
        """
        if self.employee_data is None:
            self.load_employee_list_from_csv()
        
        return (self.employee_data['senior_workers'], 
                self.employee_data['junior_workers'])

def generate_test_employee_csv(output_path: str = None) -> str:
    """生成測試用的員工名單CSV檔案
    
    Args:
        output_path: 輸出檔案路徑，如果為None則使用預設路徑
    
    Returns:
        生成的檔案路徑
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, EXTERNAL_WORKER_LIST_FILE)
    
    # 生成測試員工名單
    test_employees = []
    
    # 資深員工 - 使用真實姓名
    senior_names = ["陈明华", "李建国", "王志强", "张雅琴", "刘德华"]
    for i, name in enumerate(senior_names[:SENIOR_WORKERS]):
        test_employees.append({
            'id': f"S{i+1:03d}",
            'name': name,
            'type': 'SENIOR',
            'department': '技術部',
            'experience_years': 5 + i,
            'specialization': ['數據分析', '系統設計', '架構規劃', '技術領導', '專案管理'][i % 5]
        })
    
    # 一般員工 - 使用真實姓名
    junior_names = ["黄小敏", "周文杰", "吴晓东", "郑雨晴", "刘思远", "宋嘉欣", "杨永康", "朱佳怡", "许志华", "何雅婷"]
    for i, name in enumerate(junior_names[:JUNIOR_WORKERS]):
        test_employees.append({
            'id': f"J{i+1:03d}",
            'name': name,
            'type': 'JUNIOR',
            'department': '操作部',
            'experience_years': 1 + (i % 3),
            'specialization': ['數據處理', '文檔整理', '基礎分析', '品質控制', '客戶服務'][i % 5]
        })
    
    # 創建DataFrame並保存
    df = pd.DataFrame(test_employees)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"✅ 測試員工名單CSV檔案已生成: {output_path}")
    print(f"   資深員工: {len([name for name in senior_names[:SENIOR_WORKERS]])} 人")
    print(f"   一般員工: {len([name for name in junior_names[:JUNIOR_WORKERS]])} 人")
    print(f"   總計: {len(test_employees)} 人")
    
    return output_path

def load_external_employee_list() -> Tuple[List[str], List[str]]:
    """載入外部員工名單
    
    Returns:
        (資深員工列表, 一般員工列表)
    """
    if not USE_EXTERNAL_WORKER_LIST:
        # 使用預設員工名單
        senior_workers = [f"SENIOR_WORKER_{i+1}" for i in range(SENIOR_WORKERS)]
        junior_workers = [f"JUNIOR_WORKER_{i+1}" for i in range(JUNIOR_WORKERS)]
        return senior_workers, junior_workers
    
    # 使用外部員工名單
    manager = EmployeeManager()
    
    # 驗證員工數量
    is_valid, message = manager.validate_employee_counts()
    if not is_valid:
        print(f"⚠️ 員工數量驗證失敗: {message}")
        print("🔄 回退使用預設員工名單")
        senior_workers = [f"SENIOR_WORKER_{i+1}" for i in range(SENIOR_WORKERS)]
        junior_workers = [f"JUNIOR_WORKER_{i+1}" for i in range(JUNIOR_WORKERS)]
        return senior_workers, junior_workers
    
    return manager.get_worker_lists()

def main():
    """主函數 - 用於測試和示範"""
    print("=== 員工管理模組測試 ===")
    
    # 生成測試CSV檔案
    csv_path = generate_test_employee_csv()
    
    # 測試讀取功能
    manager = EmployeeManager(csv_path)
    
    # 顯示JSON格式
    print(f"\n📄 員工名單JSON格式:")
    print(manager.get_employee_json())
    
    # 驗證員工數量
    is_valid, message = manager.validate_employee_counts()
    print(f"\n✅ 驗證結果: {message}")
    
    # 測試外部員工名單載入
    print(f"\n🔄 測試外部員工名單載入:")
    senior_list, junior_list = load_external_employee_list()
    print(f"   資深員工: {senior_list}")
    print(f"   一般員工: {junior_list}")

def get_actual_employee_counts():
    """
    獲取實際員工數量的統一函數
    
    Returns:
        tuple: (actual_senior_count, actual_junior_count)
    """
    try:
        senior_workers, junior_workers = load_external_employee_list()
        return len(senior_workers), len(junior_workers)
    except Exception as e:
        print(f"❌ 無法讀取員工清單，使用config預設值: {e}")
        # 延遲導入避免循環依賴
        import config_params
        return config_params.SENIOR_WORKERS, config_params.JUNIOR_WORKERS

def print_actual_employee_config():
    """
    打印實際員工配置的統一函數
    """
    actual_senior_count, actual_junior_count = get_actual_employee_counts()
    print(f"👥 員工配置: {actual_senior_count}名資深員工 + {actual_junior_count}名一般員工")
    return actual_senior_count, actual_junior_count

if __name__ == "__main__":
    main() 