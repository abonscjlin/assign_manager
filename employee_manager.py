#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技師管理模組
===========

負責處理外部技師名單的讀取、解析和管理功能。

功能包括：
1. 從CSV檔案讀取技師名單
2. 將技師名單轉換為JSON格式
3. 驗證技師名單格式
4. 生成測試用技師名單
"""

import pandas as pd
import json
import os
from typing import Dict, List, Tuple
import config_params
from config_params import EXTERNAL_WORKER_LIST_FILE, USE_EXTERNAL_WORKER_LIST, SENIOR_WORKERS, JUNIOR_WORKERS

class EmployeeManager:
    """技師管理器 - 處理技師清單的載入、轉換和管理"""
    
    def __init__(self):
        """初始化技師管理器"""
        self.employee_df = None
        self.is_loaded = False
        
    def load_employee_list_from_csv(self, csv_file=None):
        """
        從CSV檔案載入技師清單
        
        Args:
            csv_file (str, optional): CSV檔案路徑，預設使用配置中的路徑
        
        Returns:
            bool: 載入是否成功
        """
        try:
            if csv_file is None:
                csv_file = EXTERNAL_WORKER_LIST_FILE
            
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"找不到技師清單檔案: {csv_file}")
            
            # 讀取CSV檔案
            self.employee_df = pd.read_csv(csv_file)
            
            # 驗證必要欄位
            required_columns = ['id', 'type']
            missing_columns = [col for col in required_columns if col not in self.employee_df.columns]
            
            if missing_columns:
                raise ValueError(f"技師清單檔案缺少必要欄位: {missing_columns}")
            
            # 驗證技師類型
            valid_types = ['SENIOR', 'JUNIOR']
            invalid_types = self.employee_df[~self.employee_df['type'].isin(valid_types)]
            
            if not invalid_types.empty:
                raise ValueError(f"發現無效的技師類型: {invalid_types['type'].unique()}")
            
            # 檢查是否有重複的ID
            duplicate_ids = self.employee_df[self.employee_df.duplicated(subset=['id'])]
            if not duplicate_ids.empty:
                raise ValueError(f"發現重複的技師ID: {duplicate_ids['id'].tolist()}")
            
            self.is_loaded = True
            
            # 統計載入結果
            senior_count = len(self.employee_df[self.employee_df['type'] == 'SENIOR'])
            junior_count = len(self.employee_df[self.employee_df['type'] == 'JUNIOR'])
            
            print(f"✅ 技師清單載入成功: 資深技師 {senior_count} 人, 一般技師 {junior_count} 人")
            return True
            
        except Exception as e:
            print(f"❌ 技師清單載入失敗: {str(e)}")
            self.is_loaded = False
            return False
    
    def get_employee_dict(self):
        """
        取得技師字典格式（用於向後兼容）
        
        Returns:
            dict: 包含senior_workers和junior_workers的字典
        """
        if not self.is_loaded or self.employee_df is None:
            raise RuntimeError("技師清單尚未載入，請先執行 load_employee_list_from_csv()")
        
        # 分離資深和一般技師，使用ID作為技師標識
        senior_employees = self.employee_df[self.employee_df['type'] == 'SENIOR']['id'].tolist()
        junior_employees = self.employee_df[self.employee_df['type'] == 'JUNIOR']['id'].tolist()
        
        return {
            'senior_workers': senior_employees,
            'junior_workers': junior_employees
        }
    
    def get_employee_list_json(self):
        """
        取得JSON格式的技師清單
        
        Returns:
            str: JSON格式的技師清單
        """
        if not self.is_loaded or self.employee_df is None:
            raise RuntimeError("技師清單尚未載入，請先執行 load_employee_list_from_csv()")
        
        # 轉換為字典列表
        employee_list = []
        for _, row in self.employee_df.iterrows():
            employee_list.append({
                'id': row['id'],
                'type': row['type']
            })
        
        return json.dumps(employee_list, ensure_ascii=False, indent=2)
    
    def save_employee_list_json(self, output_file='employee_list.json'):
        """
        將技師清單儲存為JSON檔案
        
        Args:
            output_file (str): 輸出檔案路徑
        
        Returns:
            bool: 儲存是否成功
        """
        try:
            json_content = self.get_employee_list_json()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            print(f"✅ 技師清單JSON已儲存至: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 儲存技師清單JSON失敗: {str(e)}")
            return False
    
    def get_employee_stats(self):
        """
        取得技師統計資訊
        
        Returns:
            dict: 技師統計資訊
        """
        if not self.is_loaded or self.employee_df is None:
            raise RuntimeError("技師清單尚未載入，請先執行 load_employee_list_from_csv()")
        
        senior_count = len(self.employee_df[self.employee_df['type'] == 'SENIOR'])
        junior_count = len(self.employee_df[self.employee_df['type'] == 'JUNIOR'])
        total_count = len(self.employee_df)
        
        return {
            'total_employees': total_count,
            'senior_employees': senior_count,
            'junior_employees': junior_count,
            'senior_percentage': round((senior_count / total_count) * 100, 2) if total_count > 0 else 0,
            'junior_percentage': round((junior_count / total_count) * 100, 2) if total_count > 0 else 0
        }

def load_external_employee_list():
    """
    載入外部技師清單的便利函數
    
    Returns:
        tuple: (senior_workers_list, junior_workers_list)
    """
    if not USE_EXTERNAL_WORKER_LIST:
        # 使用配置檔中的預設技師數量，生成ID格式
        senior_workers = [f"senior.worker.{i+1}" for i in range(SENIOR_WORKERS)]
        junior_workers = [f"junior.worker.{i+1}" for i in range(JUNIOR_WORKERS)]
        return senior_workers, junior_workers
    
    try:
        manager = EmployeeManager()
        if manager.load_employee_list_from_csv():
            employee_dict = manager.get_employee_dict()
            return employee_dict['senior_workers'], employee_dict['junior_workers']
        else:
            raise Exception("無法載入技師清單")
    except Exception as e:
        print(f"❌ 載入外部技師清單失敗，使用預設配置: {e}")
        # 使用配置檔中的預設技師數量，生成ID格式
        senior_workers = [f"senior.worker.{i+1}" for i in range(SENIOR_WORKERS)]
        junior_workers = [f"junior.worker.{i+1}" for i in range(JUNIOR_WORKERS)]
        return senior_workers, junior_workers

def print_actual_employee_config():
    """
    印出實際技師配置的統一函數
    """
    try:
        senior_count, junior_count = get_actual_employee_counts()
        print(f"📊 實際技師配置: {senior_count}資深 + {junior_count}一般 = {senior_count + junior_count}人")
    except Exception as e:
        print(f"❌ 無法取得技師配置: {e}")

def get_actual_employee_counts():
    """
    獲取實際技師數量的統一函數
    
    Returns:
        tuple: (actual_senior_count, actual_junior_count)
    """
    try:
        senior_workers, junior_workers = load_external_employee_list()
        return len(senior_workers), len(junior_workers)
    except Exception as e:
        print(f"❌ 無法讀取技師清單，使用config預設值: {e}")
        # 延遲導入避免循環依賴
        import config_params
        return config_params.SENIOR_WORKERS, config_params.JUNIOR_WORKERS

def get_runtime_config():
    """
    獲取運行時配置，包括實際技師數量
    
    Returns:
        dict: 包含所有配置參數的字典
    """
    try:
        actual_senior_count, actual_junior_count = get_actual_employee_counts()
        
        return {
            'senior_workers': actual_senior_count,
            'junior_workers': actual_junior_count,
            'total_workers': actual_senior_count + actual_junior_count,
            'work_hours_per_day': config_params.WORK_HOURS_PER_DAY,
            'minimum_work_target': config_params.MINIMUM_WORK_TARGET,
            'senior_time': config_params.SENIOR_TIME,
            'junior_time': config_params.JUNIOR_TIME,
            'use_external_worker_list': config_params.USE_EXTERNAL_WORKER_LIST,
            'external_worker_list_file': config_params.EXTERNAL_WORKER_LIST_FILE
        }
    except Exception as e:
        print(f"❌ 取得運行時配置失敗: {e}")
        return {
            'senior_workers': config_params.SENIOR_WORKERS,
            'junior_workers': config_params.JUNIOR_WORKERS,
            'total_workers': config_params.SENIOR_WORKERS + config_params.JUNIOR_WORKERS,
            'work_hours_per_day': config_params.WORK_HOURS_PER_DAY,
            'minimum_work_target': config_params.MINIMUM_WORK_TARGET,
            'senior_time': config_params.SENIOR_TIME,
            'junior_time': config_params.JUNIOR_TIME,
            'use_external_worker_list': config_params.USE_EXTERNAL_WORKER_LIST,
            'external_worker_list_file': config_params.EXTERNAL_WORKER_LIST_FILE
        }

def main():
    """主函數 - 用於測試和示範"""
    print("=== 技師管理模組測試 ===")
    
    # 測試讀取功能
    manager = EmployeeManager()
    
    if manager.load_employee_list_from_csv():
        # 顯示JSON格式
        print(f"\n📄 技師清單JSON格式:")
        print(manager.get_employee_list_json())
        
        # 顯示統計資訊
        stats = manager.get_employee_stats()
        print(f"\n📊 技師統計:")
        print(f"   總技師數: {stats['total_employees']}")
        print(f"   資深技師: {stats['senior_employees']} ({stats['senior_percentage']}%)")
        print(f"   一般技師: {stats['junior_employees']} ({stats['junior_percentage']}%)")
        
        # 測試外部技師名單載入
        print(f"\n🔄 測試外部技師名單載入:")
        senior_list, junior_list = load_external_employee_list()
        print(f"   資深技師: {senior_list}")
        print(f"   一般技師: {junior_list}")
    else:
        print("❌ 技師清單載入失敗")

if __name__ == "__main__":
    main() 