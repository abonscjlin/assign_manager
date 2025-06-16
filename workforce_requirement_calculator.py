#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人力需求計算器
=================

分析當前工作分配情況，計算要達到300件目標需要增加多少人力。
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_params import *
from employee_manager import get_actual_employee_counts

def simulate_workforce_scenario(senior_workers, junior_workers, df):
    """模擬指定人力配置下的工作完成情況"""
    from optimal_strategy_analysis import advanced_optimal_strategy
    
    # 暫時修改全局變量進行模擬
    original_senior = SENIOR_WORKERS
    original_junior = JUNIOR_WORKERS
    
    # 替換配置
    import config_params
    config_params.SENIOR_WORKERS = senior_workers
    config_params.JUNIOR_WORKERS = junior_workers
    
    # 同時也要更新 optimal_strategy_analysis 模塊中的變量
    import optimal_strategy_analysis
    optimal_strategy_analysis.SENIOR_WORKERS = senior_workers
    optimal_strategy_analysis.JUNIOR_WORKERS = junior_workers
    optimal_strategy_analysis.WORK_HOURS_PER_DAY = WORK_HOURS_PER_DAY
    
    try:
        # 執行策略計算
        assignment, leftover_senior, leftover_junior = advanced_optimal_strategy(df)
        total_completed = sum(sum(counts) for counts in assignment.values())
        
        # 計算時間使用情況
        senior_time_used = senior_workers * WORK_HOURS_PER_DAY - leftover_senior
        junior_time_used = junior_workers * WORK_HOURS_PER_DAY - leftover_junior
        overall_utilization = (senior_time_used + junior_time_used) / ((senior_workers + junior_workers) * WORK_HOURS_PER_DAY)
        
        # 添加調試信息（僅在前幾次調用時顯示）
        debug_info = {
            'total_completed': total_completed,
            'senior_utilization': senior_time_used / (senior_workers * WORK_HOURS_PER_DAY) * 100,
            'junior_utilization': junior_time_used / (junior_workers * WORK_HOURS_PER_DAY) * 100,
            'overall_utilization': overall_utilization * 100,
            'leftover_senior': leftover_senior,
            'leftover_junior': leftover_junior,
            'meets_target': total_completed >= MINIMUM_WORK_TARGET,
            'assignment': assignment,
            'senior_time_used': senior_time_used,
            'junior_time_used': junior_time_used
        }
        
        return debug_info
    finally:
        # 恢復原始配置
        config_params.SENIOR_WORKERS = original_senior
        config_params.JUNIOR_WORKERS = original_junior
        optimal_strategy_analysis.SENIOR_WORKERS = original_senior
        optimal_strategy_analysis.JUNIOR_WORKERS = original_junior

def analyze_workload_gap(df):
    """分析未完成工作的詳細情況"""
    print("\n🔍 分析未完成工作的詳細情況...")
    
    # 使用當前配置執行策略
    from strategy_manager import get_strategy_manager
    manager = get_strategy_manager()
    manager.load_data()
    optimal_assignment = manager.get_optimal_assignment()
    
    # 計算已分配的工作數量
    total_assigned = sum(sum(counts) for counts in optimal_assignment.values())
    unassigned_count = len(df) - total_assigned
    
    print(f"📊 當前分配情況:")
    print(f"   總工作數量: {len(df)} 件")
    print(f"   已分配工作: {total_assigned} 件")
    print(f"   未分配工作: {unassigned_count} 件")
    print(f"   分配成功率: {total_assigned/len(df)*100:.1f}%")
    
    # 分析未分配工作的原因
    gap_to_target = max(0, MINIMUM_WORK_TARGET - total_assigned)
    if gap_to_target > 0:
        print(f"\n🎯 達成300件目標還需要: {gap_to_target} 件")
    else:
        print(f"\n✅ 已超額達成目標: 完成 {total_assigned} 件 (目標300件)")
        return 0, {}
    
    # 分析未分配工作的難度分佈（模擬）
    # 假設未分配的工作主要是按優先權6和較高難度的工作
    df_sorted = df.sort_values(['priority', 'difficulty'])
    
    # 模擬未分配工作的分佈
    unassigned_work_profile = {}
    remaining_gap = gap_to_target
    
    # 分析各難度的平均時間需求
    print(f"\n⏱️ 各難度工作時間需求:")
    for diff in range(1, 8):
        senior_time = SENIOR_TIME[diff]
        junior_time = JUNIOR_TIME[diff]
        print(f"   難度 {diff}: 資深技師 {senior_time}分鐘, 一般技師 {junior_time}分鐘")
        
        # 估算該難度未分配的工作數量
        estimated_count = min(remaining_gap, max(1, unassigned_count // 7))
        if estimated_count > 0:
            unassigned_work_profile[diff] = estimated_count
            remaining_gap -= estimated_count
    
    print(f"\n📋 估算未分配工作分佈:")
    total_estimated_time_senior = 0
    total_estimated_time_junior = 0
    
    for diff, count in unassigned_work_profile.items():
        senior_time = count * SENIOR_TIME[diff]
        junior_time = count * JUNIOR_TIME[diff]
        total_estimated_time_senior += senior_time
        total_estimated_time_junior += junior_time
        print(f"   難度 {diff}: {count} 件 (資深技師需{senior_time}分鐘, 一般技師需{junior_time}分鐘)")
    
    print(f"\n💼 處理缺口所需總時間:")
    print(f"   如全由資深技師處理: {total_estimated_time_senior} 分鐘")
    print(f"   如全由一般技師處理: {total_estimated_time_junior} 分鐘")
    
    return gap_to_target, unassigned_work_profile

def calculate_workforce_requirements(df):
    """計算人力需求的主要函數"""
    print("="*80)
    print("🧮 人力需求計算分析系統")
    print("="*80)
    print(f"📅 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 載入實際技師數量
    actual_senior_count, actual_junior_count = get_actual_employee_counts()
    
    # 分析當前配置
    print(f"\n📋 當前人力配置:")
    print(f"   資深技師: {actual_senior_count} 人")
    print(f"   一般技師: {actual_junior_count} 人")
    print(f"   總人力: {actual_senior_count + actual_junior_count} 人")
    print(f"   每人日工時: {WORK_HOURS_PER_DAY} 分鐘 ({WORK_HOURS_PER_DAY//60} 小時)")
    print(f"   總可用工時: {(actual_senior_count + actual_junior_count) * WORK_HOURS_PER_DAY} 分鐘")
    print(f"   最低目標: {MINIMUM_WORK_TARGET} 件")
    
    # 分析工作缺口
    gap_to_target, unassigned_profile = analyze_workload_gap(df)
    
    if gap_to_target == 0:
        print("\n🎉 當前人力配置已能滿足目標要求！")
        return
    
    print(f"\n🔧 計算人力增加方案...")
    print("="*60)
    
    # 擴大測試範圍
    scenarios = []
    
    # 方案一：只增加一般技師（擴大範圍）
    print(f"\n💡 方案一：只增加一般技師")
    for additional_junior in range(1, 11):  # 增加到10人
        new_junior = actual_junior_count + additional_junior
        result = simulate_workforce_scenario(actual_senior_count, new_junior, df)
        
        cost_increase = (additional_junior / (actual_senior_count + actual_junior_count)) * 100
        
        scenarios.append({
            'name': f'增加{additional_junior}名一般技師',
            'senior': actual_senior_count,
            'junior': new_junior,
            'additional_cost': cost_increase,
            'completed': result['total_completed'],
            'meets_target': result['meets_target'],
            'utilization': result['overall_utilization']
        })
        
        status = "✅ 達標" if result['meets_target'] else "❌ 未達標"
        print(f"   +{additional_junior}人 → 完成{result['total_completed']}件 | 利用率{result['overall_utilization']:.1f}% | {status}")
        
        # 一旦達標就輸出詳細信息
        if result['meets_target'] and additional_junior <= 3:
            print(f"      💡 首次達標方案：增加{additional_junior}名一般技師")
    
    # 方案二：只增加資深技師（擴大範圍）
    print(f"\n💡 方案二：只增加資深技師")
    for additional_senior in range(1, 8):  # 增加到7人
        new_senior = actual_senior_count + additional_senior
        result = simulate_workforce_scenario(new_senior, actual_junior_count, df)
        
        cost_increase = (additional_senior * 1.5 / (actual_senior_count + actual_junior_count)) * 100
        
        scenarios.append({
            'name': f'增加{additional_senior}名資深技師',
            'senior': new_senior,
            'junior': actual_junior_count,
            'additional_cost': cost_increase,
            'completed': result['total_completed'],
            'meets_target': result['meets_target'],
            'utilization': result['overall_utilization']
        })
        
        status = "✅ 達標" if result['meets_target'] else "❌ 未達標"
        print(f"   +{additional_senior}人 → 完成{result['total_completed']}件 | 利用率{result['overall_utilization']:.1f}% | {status}")
        
        # 一旦達標就輸出詳細信息
        if result['meets_target'] and additional_senior <= 3:
            print(f"      💡 首次達標方案：增加{additional_senior}名資深技師")
    
    # 方案三：混合增加（擴大範圍）
    print(f"\n💡 方案三：混合增加")
    mixed_scenarios = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
        (2, 1), (2, 2), (2, 3), (2, 4),
        (3, 1), (3, 2), (3, 3),
        (4, 1), (4, 2),
        (5, 1)
    ]
    
    for add_senior, add_junior in mixed_scenarios:
        new_senior = actual_senior_count + add_senior
        new_junior = actual_junior_count + add_junior
        result = simulate_workforce_scenario(new_senior, new_junior, df)
        
        cost_increase = ((add_senior * 1.5 + add_junior) / (actual_senior_count + actual_junior_count)) * 100
        
        scenarios.append({
            'name': f'增加{add_senior}資深+{add_junior}一般',
            'senior': new_senior,
            'junior': new_junior,
            'additional_cost': cost_increase,
            'completed': result['total_completed'],
            'meets_target': result['meets_target'],
            'utilization': result['overall_utilization']
        })
        
        status = "✅ 達標" if result['meets_target'] else "❌ 未達標"
        print(f"   +{add_senior}資深+{add_junior}一般 → 完成{result['total_completed']}件 | 利用率{result['overall_utilization']:.1f}% | {status}")
        
        # 一旦達標就輸出詳細信息
        if result['meets_target'] and (add_senior + add_junior) <= 4:
            print(f"      💡 首次達標方案：增加{add_senior}資深+{add_junior}一般技師")
    
    # 找出達標的最優方案
    feasible_scenarios = [s for s in scenarios if s['meets_target']]
    
    if not feasible_scenarios:
        print("\n❌ 嚴重警告：即使大幅增加人力也無法達到目標！")
        print("   可能的原因：")
        print("   1. 工作難度分佈不合理，高難度工作過多")
        print("   2. 優先權設定問題，導致分配策略無效")
        print("   3. 時間預估不準確")
        print("   建議檢查數據質量和算法邏輯")
        
        # 分析最高完成數
        best_scenario = max(scenarios, key=lambda x: x['completed'])
        print(f"\n   最佳測試方案：{best_scenario['name']}")
        print(f"   最高完成數：{best_scenario['completed']} 件")
        print(f"   仍缺少：{MINIMUM_WORK_TARGET - best_scenario['completed']} 件")
        return
    
    # 按成本排序找最經濟方案
    most_economical = min(feasible_scenarios, key=lambda x: x['additional_cost'])
    # 按完成件數排序找最高效方案
    most_effective = max(feasible_scenarios, key=lambda x: x['completed'])
    # 找平衡方案（成本效益比最佳）
    for scenario in feasible_scenarios:
        scenario['efficiency'] = scenario['completed'] / (1 + scenario['additional_cost'] / 100)
    most_balanced = max(feasible_scenarios, key=lambda x: x['efficiency'])
    
    print(f"\n🏆 推薦方案分析:")
    print("="*60)
    
    print(f"\n💰 最經濟方案: {most_economical['name']}")
    print(f"   人力配置: 資深{most_economical['senior']}人 + 一般{most_economical['junior']}人")
    print(f"   預期完成: {most_economical['completed']} 件")
    print(f"   成本增加: {most_economical['additional_cost']:.1f}%")
    print(f"   利用率: {most_economical['utilization']:.1f}%")
    
    print(f"\n🚀 最高效方案: {most_effective['name']}")
    print(f"   人力配置: 資深{most_effective['senior']}人 + 一般{most_effective['junior']}人")
    print(f"   預期完成: {most_effective['completed']} 件")
    print(f"   成本增加: {most_effective['additional_cost']:.1f}%")
    print(f"   利用率: {most_effective['utilization']:.1f}%")
    
    print(f"\n⚖️ 最平衡方案: {most_balanced['name']}")
    print(f"   人力配置: 資深{most_balanced['senior']}人 + 一般{most_balanced['junior']}人")
    print(f"   預期完成: {most_balanced['completed']} 件")
    print(f"   成本增加: {most_balanced['additional_cost']:.1f}%")
    print(f"   利用率: {most_balanced['utilization']:.1f}%")
    print(f"   效益比: {most_balanced['efficiency']:.2f}")
    
    # 詳細對比表格（只顯示前10個達標方案）
    print(f"\n📊 達標方案對比（按成本排序）:")
    print("-" * 80)
    print(f"{'方案名稱':<20} {'完成件數':<8} {'成本增加':<8} {'利用率':<8} {'推薦度':<10}")
    print("-" * 80)
    
    top_scenarios = sorted(feasible_scenarios, key=lambda x: x['additional_cost'])[:10]
    for scenario in top_scenarios:
        recommendation = ""
        if scenario == most_economical:
            recommendation += "💰"
        if scenario == most_effective:
            recommendation += "🚀"
        if scenario == most_balanced:
            recommendation += "⭐"
            
        print(f"{scenario['name']:<20} {scenario['completed']:<8} {scenario['additional_cost']:<7.1f}% {scenario['utilization']:<7.1f}% {recommendation:<10}")
    
    # 實施建議
    print(f"\n📋 實施建議:")
    print("="*60)
    
    # 根據記憶，用戶明確要求不降低目標，只能增加人力
    print(f"🎯 **基於您的要求（不降低300件最低目標），推薦採用最平衡方案：**")
    print(f"")
    print(f"   📈 **具體調整：**")
    print(f"   - 資深技師：{actual_senior_count} → {most_balanced['senior']} 人 (+{most_balanced['senior']-actual_senior_count}人)")
    print(f"   - 一般技師：{actual_junior_count} → {most_balanced['junior']} 人 (+{most_balanced['junior']-actual_junior_count}人)")
    print(f"   - 總人力：{actual_senior_count + actual_junior_count} → {most_balanced['senior'] + most_balanced['junior']} 人")
    print(f"   - 人力增加幅度：{((most_balanced['senior'] + most_balanced['junior']) - (actual_senior_count + actual_junior_count))/(actual_senior_count + actual_junior_count)*100:.1f}%")
    print(f"")
    print(f"   💼 **預期效果：**")
    print(f"   - 工作完成量：{most_balanced['completed']} 件 (超額 {most_balanced['completed']-MINIMUM_WORK_TARGET} 件)")
    print(f"   - 目標達成率：{(most_balanced['completed']/MINIMUM_WORK_TARGET)*100:.1f}%")
    print(f"   - 人力利用率：{most_balanced['utilization']:.1f}%")
    print(f"   - 成本增加：{most_balanced['additional_cost']:.1f}%")
    
    print(f"\n   🔧 **config_params.py 修改建議：**")
    print(f"   ```python")
    print(f"   SENIOR_WORKERS = {most_balanced['senior']}  # 原 {actual_senior_count}")
    print(f"   JUNIOR_WORKERS = {most_balanced['junior']}  # 原 {actual_junior_count}")
    print(f"   ```")
    
    # 添加分階段實施建議
    print(f"\n   📅 **分階段實施建議：**")
    
    total_increase = (most_balanced['senior'] - actual_senior_count) + (most_balanced['junior'] - actual_junior_count)
    if total_increase <= 3:
        print(f"   階段一：一次性增加所有人力（總共+{total_increase}人）")
    else:
        senior_increase = most_balanced['senior'] - actual_senior_count  
        junior_increase = most_balanced['junior'] - actual_junior_count
        
        print(f"   階段一：優先增加{min(2, senior_increase)}名資深技師和{min(3, junior_increase)}名一般技師")
        if senior_increase > 2 or junior_increase > 3:
            remaining_senior = max(0, senior_increase - 2)
            remaining_junior = max(0, junior_increase - 3)
            if remaining_senior > 0 or remaining_junior > 0:
                print(f"   階段二：再增加{remaining_senior}名資深技師和{remaining_junior}名一般技師")
    
    return most_balanced

def main():
    """主函數"""
    try:
        # 讀取數據
        from path_utils import get_data_file_path
        df = pd.read_csv(get_data_file_path('result.csv'))
        
        # 執行計算
        recommended_solution = calculate_workforce_requirements(df)
        
        if recommended_solution:
            print(f"\n" + "="*80)
            print(f"✅ 人力需求計算完成")
            print(f"📊 建議方案：{recommended_solution['name']}")
            print(f"🎯 預期效果：完成 {recommended_solution['completed']} 件工作")
            print(f"💰 成本影響：增加 {recommended_solution['additional_cost']:.1f}%")
            print(f"="*80)
        
    except FileNotFoundError as e:
        print(f"❌ 找不到數據文件：{e}")
        print("請確保 result.csv 文件存在")
    except Exception as e:
        print(f"❌ 計算過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 