#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遞增式人力需求計算器
===================

基於現有架構，逐步增加人力直到達成目標，不使用hard code的數值。
使用原本的strategy_manager架構，支持外部參數輸入。
"""

import pandas as pd
import sys
import os
from datetime import datetime

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_params import *
from strategy_manager import StrategyManager

class IncrementalWorkforceCalculator:
    """遞增式人力需求計算器"""
    
    def __init__(self, data_file=None, **base_params):
        """初始化計算器
        
        Args:
            data_file: 數據文件路徑
            **base_params: 基礎參數配置，如果不提供則使用config中的值
        """
        self.data_file = data_file
        
        # 設置基礎參數（如果外部沒有提供則使用config）
        self.base_senior_workers = base_params.get('senior_workers', SENIOR_WORKERS)
        self.base_junior_workers = base_params.get('junior_workers', JUNIOR_WORKERS)
        self.work_hours_per_day = base_params.get('work_hours_per_day', WORK_HOURS_PER_DAY)
        self.minimum_work_target = base_params.get('minimum_work_target', MINIMUM_WORK_TARGET)
        self.senior_time = base_params.get('senior_time', SENIOR_TIME)
        self.junior_time = base_params.get('junior_time', JUNIOR_TIME)
        
        # 載入數據
        if not self.data_file:
            from path_utils import get_data_file_path
            self.data_file = get_data_file_path('result.csv')
        
        self.df = pd.read_csv(self.data_file)
        
        # 計算成本權重（可配置）
        self.senior_cost_weight = base_params.get('senior_cost_weight', 1.5)
        self.junior_cost_weight = base_params.get('junior_cost_weight', 1.0)
    
    def evaluate_configuration(self, senior_workers, junior_workers, verbose=False):
        """評估指定人力配置的效果
        
        Args:
            senior_workers: 資深員工人數
            junior_workers: 一般員工人數  
            verbose: 是否輸出詳細信息
            
        Returns:
            dict: 包含完成工作數、是否達標、利用率等信息
        """
        manager = StrategyManager(
            senior_workers=senior_workers,
            junior_workers=junior_workers,
            work_hours_per_day=self.work_hours_per_day,
            minimum_work_target=self.minimum_work_target,
            senior_time=self.senior_time,
            junior_time=self.junior_time
        )
        
        manager.load_data(self.data_file)
        summary = manager.get_strategy_summary()
        
        # 計算成本
        total_cost = senior_workers * self.senior_cost_weight + junior_workers * self.junior_cost_weight
        base_cost = self.base_senior_workers * self.senior_cost_weight + self.base_junior_workers * self.junior_cost_weight
        cost_increase = total_cost - base_cost
        cost_increase_percentage = (cost_increase / base_cost) * 100 if base_cost > 0 else 0
        
        # 計算人力增加
        senior_increase = senior_workers - self.base_senior_workers
        junior_increase = junior_workers - self.base_junior_workers
        total_increase = senior_increase + junior_increase
        
        result = {
            'senior_workers': senior_workers,
            'junior_workers': junior_workers,
            'total_workers': senior_workers + junior_workers,
            'senior_increase': senior_increase,
            'junior_increase': junior_increase,
            'total_increase': total_increase,
            'total_completed': summary['total_completed'],
            'meets_target': summary['meets_minimum'],
            'target_gap': max(0, self.minimum_work_target - summary['total_completed']),
            'excess_completion': max(0, summary['total_completed'] - self.minimum_work_target),
            'overall_utilization': summary['overall_utilization'],
            'leftover_senior': summary['leftover_senior'],
            'leftover_junior': summary['leftover_junior'],
            'total_cost': total_cost,
            'cost_increase': cost_increase,
            'cost_increase_percentage': cost_increase_percentage,
            'efficiency': summary['total_completed'] / total_cost if total_cost > 0 else 0
        }
        
        if verbose:
            print(f"配置 {senior_workers}資深+{junior_workers}一般: 完成{result['total_completed']}件, "
                  f"{'✅達標' if result['meets_target'] else '❌未達標'}, "
                  f"成本+{cost_increase:.1f}")
        
        return result
    
    def find_minimum_workforce_addition(self, max_iterations=50, strategy='balanced'):
        """尋找達成目標的最小人力增加方案
        
        Args:
            max_iterations: 最大迭代次數
            strategy: 增加策略 ('senior_only', 'junior_only', 'balanced', 'cost_optimal')
            
        Returns:
            dict: 最優方案的詳細信息
        """
        print("="*80)
        print("🔄 遞增式人力需求計算分析")
        print("="*80)
        print(f"📅 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 目標: 達成 {self.minimum_work_target} 件最低工作目標")
        print(f"📊 策略: {strategy}")
        
        # 檢查當前配置
        print(f"\n📋 當前配置分析:")
        current_result = self.evaluate_configuration(self.base_senior_workers, self.base_junior_workers, verbose=True)
        
        if current_result['meets_target']:
            print(f"\n🎉 當前配置已達成目標！無需增加人力。")
            return current_result
        
        print(f"\n🔍 需要補足 {current_result['target_gap']} 件工作")
        print(f"🔧 開始遞增計算...")
        print("-" * 60)
        
        # 遞增搜索
        solutions = []
        iteration = 0
        
        if strategy == 'senior_only':
            # 只增加資深員工
            for add_senior in range(1, max_iterations + 1):
                iteration += 1
                result = self.evaluate_configuration(
                    self.base_senior_workers + add_senior, 
                    self.base_junior_workers,
                    verbose=True
                )
                solutions.append(result)
                
                if result['meets_target']:
                    print(f"\n✅ 找到解決方案！增加 {add_senior} 名資深員工")
                    break
                    
        elif strategy == 'junior_only':
            # 只增加一般員工
            for add_junior in range(1, max_iterations + 1):
                iteration += 1
                result = self.evaluate_configuration(
                    self.base_senior_workers,
                    self.base_junior_workers + add_junior,
                    verbose=True
                )
                solutions.append(result)
                
                if result['meets_target']:
                    print(f"\n✅ 找到解決方案！增加 {add_junior} 名一般員工")
                    break
                    
        elif strategy == 'balanced':
            # 平衡增加（同時考慮資深和一般員工）
            found_solution = False
            
            # 先嘗試小幅增加，逐步擴大範圍
            for total_add in range(1, max_iterations + 1):
                if found_solution:
                    break
                    
                # 對於每個總增加人數，嘗試不同的資深/一般組合
                for add_senior in range(0, total_add + 1):
                    add_junior = total_add - add_senior
                    iteration += 1
                    
                    result = self.evaluate_configuration(
                        self.base_senior_workers + add_senior,
                        self.base_junior_workers + add_junior,
                        verbose=True
                    )
                    solutions.append(result)
                    
                    if result['meets_target']:
                        print(f"\n✅ 找到解決方案！增加 {add_senior} 資深 + {add_junior} 一般員工")
                        found_solution = True
                        break
                        
        elif strategy == 'cost_optimal':
            # 成本最優化策略
            found_solution = False
            
            # 比較不同組合的成本效益
            for total_add in range(1, max_iterations + 1):
                if found_solution:
                    break
                    
                current_round_solutions = []
                
                # 對於每個總增加人數，嘗試不同的資深/一般組合
                for add_senior in range(0, total_add + 1):
                    add_junior = total_add - add_senior
                    iteration += 1
                    
                    result = self.evaluate_configuration(
                        self.base_senior_workers + add_senior,
                        self.base_junior_workers + add_junior,
                        verbose=True
                    )
                    
                    solutions.append(result)
                    if result['meets_target']:
                        current_round_solutions.append(result)
                
                # 如果這一輪有達標的方案，選擇成本最低的
                if current_round_solutions:
                    best_solution = min(current_round_solutions, key=lambda x: x['cost_increase'])
                    print(f"\n✅ 找到成本最優解決方案！")
                    print(f"   增加 {best_solution['senior_increase']} 資深 + {best_solution['junior_increase']} 一般員工")
                    print(f"   成本增加: {best_solution['cost_increase']:.1f}")
                    found_solution = True
        
        if not solutions or not any(s['meets_target'] for s in solutions):
            print(f"\n❌ 在 {max_iterations} 次迭代內未找到解決方案")
            print(f"建議：")
            print(f"   1. 增加最大迭代次數")
            print(f"   2. 檢查工作難度分佈是否合理")
            print(f"   3. 考慮調整工作時間配置")
            
            # 返回最佳嘗試結果
            if solutions:
                best_attempt = max(solutions, key=lambda x: x['total_completed'])
                return best_attempt
            else:
                return current_result
        
        # 找到所有達標方案
        feasible_solutions = [s for s in solutions if s['meets_target']]
        
        if not feasible_solutions:
            return current_result
        
        # 根據策略選擇最佳方案
        if strategy == 'cost_optimal':
            best_solution = min(feasible_solutions, key=lambda x: x['cost_increase'])
        else:
            # 默認選擇人力增加最少的方案
            best_solution = min(feasible_solutions, key=lambda x: x['total_increase'])
        
        # 輸出分析結果
        self._print_solution_analysis(current_result, best_solution, feasible_solutions)
        
        return best_solution
    
    def compare_all_strategies(self, max_iterations=20):
        """比較所有策略的結果
        
        Args:
            max_iterations: 每個策略的最大迭代次數
            
        Returns:
            dict: 包含所有策略結果的字典
        """
        print("="*80)
        print("📊 全策略比較分析")
        print("="*80)
        
        strategies = ['senior_only', 'junior_only', 'balanced', 'cost_optimal']
        results = {}
        
        for strategy in strategies:
            print(f"\n🔧 測試策略: {strategy}")
            print("-" * 40)
            
            result = self.find_minimum_workforce_addition(max_iterations, strategy)
            results[strategy] = result
        
        # 比較分析
        print(f"\n📊 策略比較結果:")
        print("="*80)
        
        print(f"{'策略':<15} {'人力增加':<12} {'完成工作':<8} {'成本增加':<10} {'效率':<8} {'推薦度':<8}")
        print("-" * 70)
        
        for strategy, result in results.items():
            if result['meets_target']:
                recommendation = "⭐" if result == min(
                    [r for r in results.values() if r['meets_target']], 
                    key=lambda x: x['cost_increase']
                ) else ""
                
                print(f"{strategy:<15} "
                      f"+{result['senior_increase']}資深+{result['junior_increase']}一般{'':<3} "
                      f"{result['total_completed']:<8} "
                      f"+{result['cost_increase']:<8.1f} "
                      f"{result['efficiency']:<8.2f} "
                      f"{recommendation:<8}")
            else:
                print(f"{strategy:<15} {'未達標':<12} {result['total_completed']:<8} {'N/A':<10} {'N/A':<8} {'❌':<8}")
        
        # 推薦最佳策略
        feasible_strategies = {k: v for k, v in results.items() if v['meets_target']}
        
        if feasible_strategies:
            best_strategy_name = min(feasible_strategies.keys(), 
                                   key=lambda x: feasible_strategies[x]['cost_increase'])
            best_strategy_result = feasible_strategies[best_strategy_name]
            
            print(f"\n🏆 推薦策略: {best_strategy_name}")
            print(f"   人力配置: {best_strategy_result['senior_workers']}資深 + {best_strategy_result['junior_workers']}一般")
            print(f"   增加人力: +{best_strategy_result['senior_increase']}資深 + {best_strategy_result['junior_increase']}一般")
            print(f"   完成工作: {best_strategy_result['total_completed']} 件")
            print(f"   成本增加: {best_strategy_result['cost_increase_percentage']:.1f}%")
            
            return best_strategy_result
        else:
            print(f"\n❌ 沒有策略能在指定迭代次數內達成目標")
            return None
    
    def _print_solution_analysis(self, current_result, best_solution, all_solutions):
        """輸出解決方案分析"""
        
        print(f"\n📊 解決方案分析:")
        print("="*60)
        
        print(f"當前配置: {self.base_senior_workers}資深 + {self.base_junior_workers}一般 = {self.base_senior_workers + self.base_junior_workers}人")
        print(f"   完成工作: {current_result['total_completed']} 件")
        print(f"   目標缺口: {current_result['target_gap']} 件")
        print(f"   利用率: {current_result['overall_utilization']*100:.1f}%")
        
        print(f"\n推薦配置: {best_solution['senior_workers']}資深 + {best_solution['junior_workers']}一般 = {best_solution['total_workers']}人")
        print(f"   完成工作: {best_solution['total_completed']} 件")
        print(f"   超額完成: {best_solution['excess_completion']} 件")
        print(f"   利用率: {best_solution['overall_utilization']*100:.1f}%")
        print(f"   人力增加: +{best_solution['senior_increase']}資深 + {best_solution['junior_increase']}一般 (+{best_solution['total_increase']}人)")
        print(f"   成本增加: {best_solution['cost_increase_percentage']:.1f}%")
        
        print(f"\n💡 實施建議:")
        print(f"   修改 config_params.py:")
        print(f"   ```python")
        print(f"   SENIOR_WORKERS = {best_solution['senior_workers']}  # 原 {self.base_senior_workers}")
        print(f"   JUNIOR_WORKERS = {best_solution['junior_workers']}  # 原 {self.base_junior_workers}")
        print(f"   ```")

def main():
    """主函數"""
    try:
        # 使用默認配置參數（如果需要可以傳入自定義參數）
        calculator = IncrementalWorkforceCalculator()
        
        # 比較所有策略
        best_solution = calculator.compare_all_strategies(max_iterations=15)
        
        if best_solution:
            print(f"\n" + "="*80)
            print(f"✅ 遞增式人力需求計算完成")
            print(f"📊 最佳方案: 增加 {best_solution['senior_increase']} 資深 + {best_solution['junior_increase']} 一般員工")
            print(f"🎯 預期效果: 完成 {best_solution['total_completed']} 件工作")
            print(f"💰 成本影響: 增加 {best_solution['cost_increase_percentage']:.1f}%")
            print(f"="*80)
        
    except Exception as e:
        print(f"❌ 計算過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 