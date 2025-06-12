#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人力需求計算API接口
==================

提供簡單的函數接口，讓外部可以輕鬆調用遞增式人力計算功能。
支持外部參數輸入，如果沒有輸入則使用config中的默認值。
"""

import sys
import os
from typing import Dict, Optional, Tuple, Any

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_params import *
from incremental_workforce_calculator import IncrementalWorkforceCalculator

def calculate_required_workforce(
    target: Optional[int] = None,
    current_senior: Optional[int] = None,
    current_junior: Optional[int] = None,
    work_hours_per_day: Optional[int] = None,
    senior_cost_weight: float = 1.5,
    junior_cost_weight: float = 1.0,
    strategy: str = 'cost_optimal',
    max_iterations: int = 20,
    data_file: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """計算達成目標所需的人力配置
    
    Args:
        target: 目標工作完成數，如果為None則使用config中的MINIMUM_WORK_TARGET
        current_senior: 當前資深員工人數，如果為None則使用config中的SENIOR_WORKERS
        current_junior: 當前一般員工人數，如果為None則使用config中的JUNIOR_WORKERS
        work_hours_per_day: 每人每日工時，如果為None則使用config中的WORK_HOURS_PER_DAY
        senior_cost_weight: 資深員工成本權重
        junior_cost_weight: 一般員工成本權重
        strategy: 計算策略 ('senior_only', 'junior_only', 'balanced', 'cost_optimal')
        max_iterations: 最大迭代次數
        data_file: 數據文件路徑，如果為None則自動尋找
        verbose: 是否輸出詳細信息
        
    Returns:
        dict: 包含計算結果的字典
    """
    
    # 準備參數
    params = {}
    if current_senior is not None:
        params['senior_workers'] = current_senior
    if current_junior is not None:
        params['junior_workers'] = current_junior
    if work_hours_per_day is not None:
        params['work_hours_per_day'] = work_hours_per_day
    if target is not None:
        params['minimum_work_target'] = target
    
    params['senior_cost_weight'] = senior_cost_weight
    params['junior_cost_weight'] = junior_cost_weight
    
    # 創建計算器
    calculator = IncrementalWorkforceCalculator(data_file=data_file, **params)
    
    # 執行計算
    if not verbose:
        # 重定向輸出以減少噪音
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = calculator.find_minimum_workforce_addition(max_iterations, strategy)
    else:
        result = calculator.find_minimum_workforce_addition(max_iterations, strategy)
    
    # 整理結果
    if result:
        return {
            'success': True,
            'meets_target': result['meets_target'],
            'current_configuration': {
                'senior_workers': calculator.base_senior_workers,
                'junior_workers': calculator.base_junior_workers,
                'total_workers': calculator.base_senior_workers + calculator.base_junior_workers,
                'completed_work': result['total_completed'] - result['excess_completion'] if result['meets_target'] else result['total_completed']
            },
            'recommended_configuration': {
                'senior_workers': result['senior_workers'],
                'junior_workers': result['junior_workers'],
                'total_workers': result['total_workers'],
                'completed_work': result['total_completed']
            },
            'workforce_changes': {
                'senior_increase': result['senior_increase'],
                'junior_increase': result['junior_increase'],
                'total_increase': result['total_increase']
            },
            'performance': {
                'target_gap': result['target_gap'],
                'excess_completion': result['excess_completion'],
                'overall_utilization': result['overall_utilization'],
                'leftover_senior': result['leftover_senior'],
                'leftover_junior': result['leftover_junior']
            },
            'cost_analysis': {
                'cost_increase': result['cost_increase'],
                'cost_increase_percentage': result['cost_increase_percentage'],
                'efficiency': result['efficiency']
            },
            'implementation': {
                'config_changes': {
                    'SENIOR_WORKERS': result['senior_workers'],
                    'JUNIOR_WORKERS': result['junior_workers']
                },
                'strategy_used': strategy
            }
        }
    else:
        return {
            'success': False,
            'error': '無法在指定迭代次數內找到解決方案',
            'current_configuration': {
                'senior_workers': calculator.base_senior_workers,
                'junior_workers': calculator.base_junior_workers,
                'total_workers': calculator.base_senior_workers + calculator.base_junior_workers
            }
        }

def compare_strategies(
    target: Optional[int] = None,
    current_senior: Optional[int] = None,
    current_junior: Optional[int] = None,
    work_hours_per_day: Optional[int] = None,
    senior_cost_weight: float = 1.5,
    junior_cost_weight: float = 1.0,
    max_iterations: int = 15,
    data_file: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """比較所有策略的結果
    
    Args:
        target: 目標工作完成數，如果為None則使用config中的MINIMUM_WORK_TARGET
        current_senior: 當前資深員工人數，如果為None則使用config中的SENIOR_WORKERS
        current_junior: 當前一般員工人數，如果為None則使用config中的JUNIOR_WORKERS
        work_hours_per_day: 每人每日工時，如果為None則使用config中的WORK_HOURS_PER_DAY
        senior_cost_weight: 資深員工成本權重
        junior_cost_weight: 一般員工成本權重
        max_iterations: 最大迭代次數
        data_file: 數據文件路徑，如果為None則自動尋找
        verbose: 是否輸出詳細信息
        
    Returns:
        dict: 包含所有策略比較結果的字典
    """
    
    # 準備參數
    params = {}
    if current_senior is not None:
        params['senior_workers'] = current_senior
    if current_junior is not None:
        params['junior_workers'] = current_junior
    if work_hours_per_day is not None:
        params['work_hours_per_day'] = work_hours_per_day
    if target is not None:
        params['minimum_work_target'] = target
    
    params['senior_cost_weight'] = senior_cost_weight
    params['junior_cost_weight'] = junior_cost_weight
    
    # 創建計算器
    calculator = IncrementalWorkforceCalculator(data_file=data_file, **params)
    
    # 執行比較
    if not verbose:
        # 重定向輸出以減少噪音
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            best_result = calculator.compare_all_strategies(max_iterations)
    else:
        best_result = calculator.compare_all_strategies(max_iterations)
    
    # 重新計算所有策略（為了獲取完整結果）
    strategies = ['senior_only', 'junior_only', 'balanced', 'cost_optimal']
    strategy_results = {}
    
    for strategy in strategies:
        result = calculate_required_workforce(
            target=target,
            current_senior=current_senior,
            current_junior=current_junior,
            work_hours_per_day=work_hours_per_day,
            senior_cost_weight=senior_cost_weight,
            junior_cost_weight=junior_cost_weight,
            strategy=strategy,
            max_iterations=max_iterations,
            data_file=data_file,
            verbose=False
        )
        strategy_results[strategy] = result
    
    # 找出最佳策略
    feasible_strategies = {k: v for k, v in strategy_results.items() 
                          if v['success'] and v['meets_target']}
    
    best_strategy = None
    if feasible_strategies:
        best_strategy_name = min(feasible_strategies.keys(),
                               key=lambda x: feasible_strategies[x]['cost_analysis']['cost_increase'])
        best_strategy = {
            'name': best_strategy_name,
            'result': feasible_strategies[best_strategy_name]
        }
    
    return {
        'success': len(feasible_strategies) > 0,
        'strategies': strategy_results,
        'best_strategy': best_strategy,
        'summary': {
            'feasible_count': len(feasible_strategies),
            'total_strategies': len(strategies)
        }
    }

def get_current_status(
    data_file: Optional[str] = None,
    senior_workers: Optional[int] = None,
    junior_workers: Optional[int] = None,
    work_hours_per_day: Optional[int] = None,
    target: Optional[int] = None
) -> Dict[str, Any]:
    """獲取當前配置的狀態
    
    Args:
        data_file: 數據文件路徑，如果為None則自動尋找
        senior_workers: 資深員工人數，如果為None則使用config值
        junior_workers: 一般員工人數，如果為None則使用config值
        work_hours_per_day: 每人每日工時，如果為None則使用config值
        target: 目標工作完成數，如果為None則使用config值
        
    Returns:
        dict: 包含當前狀態的字典
    """
    
    # 準備參數
    params = {}
    if senior_workers is not None:
        params['senior_workers'] = senior_workers
    if junior_workers is not None:
        params['junior_workers'] = junior_workers
    if work_hours_per_day is not None:
        params['work_hours_per_day'] = work_hours_per_day
    if target is not None:
        params['minimum_work_target'] = target
    
    # 創建計算器
    calculator = IncrementalWorkforceCalculator(data_file=data_file, **params)
    
    # 評估當前配置
    result = calculator.evaluate_configuration(
        calculator.base_senior_workers,
        calculator.base_junior_workers,
        verbose=False
    )
    
    return {
        'configuration': {
            'senior_workers': calculator.base_senior_workers,
            'junior_workers': calculator.base_junior_workers,
            'total_workers': calculator.base_senior_workers + calculator.base_junior_workers,
            'work_hours_per_day': calculator.work_hours_per_day,
            'target': calculator.minimum_work_target
        },
        'performance': {
            'completed_work': result['total_completed'],
            'meets_target': result['meets_target'],
            'target_gap': result['target_gap'],
            'overall_utilization': result['overall_utilization'],
            'leftover_senior': result['leftover_senior'],
            'leftover_junior': result['leftover_junior']
        },
        'data_info': {
            'total_work_items': len(calculator.df),
            'data_file': calculator.data_file
        }
    }

# 示例使用
def example_usage():
    """示例如何使用API"""
    
    print("="*60)
    print("人力需求計算API使用示例")
    print("="*60)
    
    # 1. 獲取當前狀態
    print("\n1. 獲取當前狀態:")
    current = get_current_status()
    print(f"   當前配置: {current['configuration']['senior_workers']}資深 + {current['configuration']['junior_workers']}一般")
    print(f"   完成工作: {current['performance']['completed_work']} 件")
    print(f"   是否達標: {'✅' if current['performance']['meets_target'] else '❌'}")
    print(f"   缺口: {current['performance']['target_gap']} 件")
    
    # 2. 計算所需人力（使用默認策略）
    print("\n2. 計算所需人力:")
    result = calculate_required_workforce(strategy='cost_optimal', verbose=False)
    if result['success']:
        print(f"   推薦配置: {result['recommended_configuration']['senior_workers']}資深 + {result['recommended_configuration']['junior_workers']}一般")
        print(f"   需要增加: +{result['workforce_changes']['senior_increase']}資深 + {result['workforce_changes']['junior_increase']}一般")
        print(f"   成本增加: {result['cost_analysis']['cost_increase_percentage']:.1f}%")
    
    # 3. 比較所有策略
    print("\n3. 比較所有策略:")
    comparison = compare_strategies(verbose=False)
    if comparison['success']:
        print(f"   最佳策略: {comparison['best_strategy']['name']}")
        best = comparison['best_strategy']['result']
        print(f"   推薦配置: {best['recommended_configuration']['senior_workers']}資深 + {best['recommended_configuration']['junior_workers']}一般")
        print(f"   成本增加: {best['cost_analysis']['cost_increase_percentage']:.1f}%")
    
    # 4. 使用自定義參數
    print("\n4. 使用自定義參數 (目標350件):")
    custom_result = calculate_required_workforce(target=350, strategy='balanced', verbose=False)
    if custom_result['success']:
        print(f"   推薦配置: {custom_result['recommended_configuration']['senior_workers']}資深 + {custom_result['recommended_configuration']['junior_workers']}一般")
        print(f"   需要增加: +{custom_result['workforce_changes']['senior_increase']}資深 + {custom_result['workforce_changes']['junior_increase']}一般")
        print(f"   成本增加: {custom_result['cost_analysis']['cost_increase_percentage']:.1f}%")

if __name__ == "__main__":
    example_usage() 