"""
統一策略管理器 - 避免重複分配邏輯
================================================

這個模組提供統一的分配策略接口，確保所有其他模組都使用相同的最佳策略。

功能：
1. 統一策略計算入口
2. 結果緩存和重用
3. 參數化配置支持
4. 支持外部參數輸入
"""

import pandas as pd
from config_params import *
from optimal_strategy_analysis import advanced_optimal_strategy

class StrategyManager:
    """統一策略管理器 - 確保所有模組使用相同的最佳策略"""
    
    def __init__(self, data_file=None, **kwargs):
        """初始化策略管理器
        
        Args:
            data_file: 數據文件路徑
            **kwargs: 外部參數覆蓋，包括：
                - senior_workers: 資深員工人數
                - junior_workers: 一般員工人數  
                - work_hours_per_day: 每人每日工時
                - minimum_work_target: 最低工作目標
                - senior_time: 資深員工時間配置
                - junior_time: 一般員工時間配置
        """
        self.data_file = data_file
        self._df = None
        self._optimal_assignment = None
        self._leftover_senior = None
        self._leftover_junior = None
        self._computed = False
        
        # 設置參數（優先使用外部參數，否則使用config）
        self.senior_workers = kwargs.get('senior_workers', SENIOR_WORKERS)
        self.junior_workers = kwargs.get('junior_workers', JUNIOR_WORKERS) 
        self.work_hours_per_day = kwargs.get('work_hours_per_day', WORK_HOURS_PER_DAY)
        self.minimum_work_target = kwargs.get('minimum_work_target', MINIMUM_WORK_TARGET)
        self.senior_time = kwargs.get('senior_time', SENIOR_TIME)
        self.junior_time = kwargs.get('junior_time', JUNIOR_TIME)
    
    def update_parameters(self, **kwargs):
        """更新參數並重置計算狀態
        
        Args:
            **kwargs: 要更新的參數
        """
        if 'senior_workers' in kwargs:
            self.senior_workers = kwargs['senior_workers']
        if 'junior_workers' in kwargs:
            self.junior_workers = kwargs['junior_workers']
        if 'work_hours_per_day' in kwargs:
            self.work_hours_per_day = kwargs['work_hours_per_day']
        if 'minimum_work_target' in kwargs:
            self.minimum_work_target = kwargs['minimum_work_target']
        if 'senior_time' in kwargs:
            self.senior_time = kwargs['senior_time']
        if 'junior_time' in kwargs:
            self.junior_time = kwargs['junior_time']
            
        self._computed = False  # 重新計算
    
    def get_current_parameters(self):
        """獲取當前參數配置"""
        return {
            'senior_workers': self.senior_workers,
            'junior_workers': self.junior_workers,
            'work_hours_per_day': self.work_hours_per_day,
            'minimum_work_target': self.minimum_work_target,
            'senior_time': self.senior_time,
            'junior_time': self.junior_time
        }
    
    def load_data(self, data_file=None):
        """載入數據"""
        if data_file:
            self.data_file = data_file
        
        if not self.data_file:
            from path_utils import get_data_file_path
            self.data_file = get_data_file_path('result.csv')
        
        self._df = pd.read_csv(self.data_file)
        self._computed = False  # 重新計算
        return self._df
    
    def compute_optimal_strategy(self, force_recompute=False):
        """計算最佳策略（支持緩存和自定義參數）"""
        if self._computed and not force_recompute:
            return self._optimal_assignment, self._leftover_senior, self._leftover_junior
        
        if self._df is None:
            self.load_data()
        
        # 使用當前實例的參數進行計算
        self._optimal_assignment, self._leftover_senior, self._leftover_junior = advanced_optimal_strategy(
            self._df,
            senior_workers=self.senior_workers,
            junior_workers=self.junior_workers,
            work_hours_per_day=self.work_hours_per_day,
            minimum_work_target=self.minimum_work_target,
            senior_time=self.senior_time,
            junior_time=self.junior_time
        )
        self._computed = True
        
        return self._optimal_assignment, self._leftover_senior, self._leftover_junior
    
    def get_optimal_assignment(self):
        """獲取最佳分配方案"""
        if not self._computed:
            self.compute_optimal_strategy()
        return self._optimal_assignment
    
    def get_leftover_time(self):
        """獲取剩餘時間"""
        if not self._computed:
            self.compute_optimal_strategy()
        return self._leftover_senior, self._leftover_junior
    
    def get_strategy_summary(self):
        """獲取策略摘要"""
        if not self._computed:
            self.compute_optimal_strategy()
        
        total_completed = sum(sum(counts) for counts in self._optimal_assignment.values())
        total_senior_assigned = sum(counts[0] for counts in self._optimal_assignment.values())
        total_junior_assigned = sum(counts[1] for counts in self._optimal_assignment.values())
        
        senior_time_used = self.senior_workers * self.work_hours_per_day - self._leftover_senior
        junior_time_used = self.junior_workers * self.work_hours_per_day - self._leftover_junior
        
        return {
            'total_completed': total_completed,
            'total_senior_assigned': total_senior_assigned,
            'total_junior_assigned': total_junior_assigned,
            'senior_utilization': senior_time_used / (self.senior_workers * self.work_hours_per_day),
            'junior_utilization': junior_time_used / (self.junior_workers * self.work_hours_per_day),
            'overall_utilization': (senior_time_used + junior_time_used) / ((self.senior_workers + self.junior_workers) * self.work_hours_per_day),
            'completion_rate': total_completed / len(self._df) if self._df is not None else 0,
            'meets_minimum': total_completed >= self.minimum_work_target,
            'leftover_senior': self._leftover_senior,
            'leftover_junior': self._leftover_junior,
            'parameters': self.get_current_parameters()
        }
    
    def get_data(self):
        """獲取數據"""
        if self._df is None:
            self.load_data()
        return self._df

# 全局單例實例
_strategy_manager = None

def get_strategy_manager(**kwargs):
    """獲取全局策略管理器實例
    
    Args:
        **kwargs: 外部參數，如果提供則創建新實例
    """
    global _strategy_manager
    if _strategy_manager is None or kwargs:
        if kwargs:
            # 如果有外部參數，創建新實例
            return StrategyManager(**kwargs)
        else:
            # 否則使用全局實例
            _strategy_manager = StrategyManager()
    return _strategy_manager

def get_optimal_assignment(**kwargs):
    """快速獲取最佳分配方案"""
    return get_strategy_manager(**kwargs).get_optimal_assignment()

def get_strategy_summary(**kwargs):
    """快速獲取策略摘要"""
    return get_strategy_manager(**kwargs).get_strategy_summary()

def get_leftover_time(**kwargs):
    """快速獲取剩餘時間"""
    return get_strategy_manager(**kwargs).get_leftover_time() 