#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接人力需求計算器
=================

基於工作量和時間直接計算需要增加多少人力才能達到300件目標。
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_params import *

def calculate_required_time_for_gap(gap_count, df):
    """計算處理缺口工作所需的時間"""
    
    # 分析未完成工作的難度分佈
    # 按照優先權和難度排序，模擬未分配的工作
    df_sorted = df.sort_values(['priority', 'difficulty'])
    
    # 獲取當前最佳分配
    from strategy_manager import get_strategy_manager
    manager = get_strategy_manager()
    manager.load_data()
    optimal_assignment = manager.get_optimal_assignment()
    total_assigned = sum(sum(counts) for counts in optimal_assignment.values())
    
    # 估算未分配工作的分佈（假設按比例分配）
    unassigned_work = df_sorted.iloc[total_assigned:total_assigned + gap_count]
    
    # 計算處理這些工作需要的時間
    senior_time_needed = 0
    junior_time_needed = 0
    
    difficulty_distribution = {}
    
    for _, row in unassigned_work.iterrows():
        diff = row['difficulty']
        if diff not in difficulty_distribution:
            difficulty_distribution[diff] = 0
        difficulty_distribution[diff] += 1
        
        senior_time_needed += SENIOR_TIME[diff]
        junior_time_needed += JUNIOR_TIME[diff]
    
    return senior_time_needed, junior_time_needed, difficulty_distribution

def direct_workforce_calculation():
    """直接計算人力需求"""
    
    print("="*80)
    print("📊 直接人力需求計算分析")
    print("="*80)
    print(f"📅 計算時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 讀取數據
    from path_utils import get_data_file_path
    df = pd.read_csv(get_data_file_path('result.csv'))
    
    # 獲取當前最佳配置結果
    from strategy_manager import get_strategy_manager
    manager = get_strategy_manager()
    manager.load_data()
    optimal_assignment = manager.get_optimal_assignment()
    leftover_senior, leftover_junior = manager.get_leftover_time()
    
    # 計算當前狀況
    total_assigned = sum(sum(counts) for counts in optimal_assignment.values())
    current_gap = max(0, MINIMUM_WORK_TARGET - total_assigned)
    
    print(f"\n📋 當前狀況分析:")
    print(f"   總工作數量: {len(df)} 件")
    print(f"   當前分配完成: {total_assigned} 件")
    print(f"   目標要求: {MINIMUM_WORK_TARGET} 件")
    print(f"   需要補足: {current_gap} 件")
    print(f"   當前人力: {SENIOR_WORKERS}資深 + {JUNIOR_WORKERS}一般 = {SENIOR_WORKERS+JUNIOR_WORKERS}人")
    print(f"   剩餘時間: 資深{leftover_senior}分鐘, 一般{leftover_junior}分鐘")
    
    if current_gap == 0:
        print("\n🎉 當前配置已能達成目標！")
        return
    
    # 計算處理缺口所需時間
    senior_time_needed, junior_time_needed, difficulty_dist = calculate_required_time_for_gap(current_gap, df)
    
    print(f"\n⏱️ 處理{current_gap}件缺口工作的時間需求:")
    print(f"   如全由資深員工處理: {senior_time_needed} 分鐘")
    print(f"   如全由一般員工處理: {junior_time_needed} 分鐘")
    
    print(f"\n📊 缺口工作難度分佈:")
    for diff in sorted(difficulty_dist.keys()):
        count = difficulty_dist[diff]
        senior_time = count * SENIOR_TIME[diff]
        junior_time = count * JUNIOR_TIME[diff]
        print(f"   難度 {diff}: {count} 件 (資深需{senior_time}分鐘, 一般需{junior_time}分鐘)")
    
    # 計算不同人力增加方案
    print(f"\n🔧 人力增加方案計算:")
    print("="*60)
    
    # 方案計算
    solutions = []
    
    # 方案一：只增加資深員工
    print(f"\n💡 方案一：只增加資深員工")
    
    # 考慮現有剩餘時間
    effective_senior_time_needed = max(0, senior_time_needed - leftover_senior)
    additional_senior_needed = effective_senior_time_needed / WORK_HOURS_PER_DAY
    senior_workers_to_add = int(np.ceil(additional_senior_needed))
    
    if senior_workers_to_add == 0:
        print(f"   ✅ 當前剩餘時間足夠，無需增加資深員工")
        solutions.append({
            'type': '不增加資深員工',
            'senior_add': 0,
            'junior_add': 0,
            'cost_factor': 0,
            'description': '利用現有剩餘時間'
        })
    else:
        print(f"   需要額外時間: {effective_senior_time_needed} 分鐘")
        print(f"   ✅ 建議增加: {senior_workers_to_add} 名資深員工")
        solutions.append({
            'type': '只增加資深員工',
            'senior_add': senior_workers_to_add,
            'junior_add': 0,
            'cost_factor': senior_workers_to_add * 1.5,  # 假設資深員工成本1.5倍
            'description': f'增加{senior_workers_to_add}名資深員工'
        })
    
    # 方案二：只增加一般員工
    print(f"\n💡 方案二：只增加一般員工")
    
    effective_junior_time_needed = max(0, junior_time_needed - leftover_junior)
    additional_junior_needed = effective_junior_time_needed / WORK_HOURS_PER_DAY
    junior_workers_to_add = int(np.ceil(additional_junior_needed))
    
    if junior_workers_to_add == 0:
        print(f"   ✅ 當前剩餘時間足夠，無需增加一般員工")
        solutions.append({
            'type': '不增加一般員工',
            'senior_add': 0,
            'junior_add': 0,
            'cost_factor': 0,
            'description': '利用現有剩餘時間'
        })
    else:
        print(f"   需要額外時間: {effective_junior_time_needed} 分鐘")
        print(f"   ✅ 建議增加: {junior_workers_to_add} 名一般員工")
        solutions.append({
            'type': '只增加一般員工',
            'senior_add': 0,
            'junior_add': junior_workers_to_add,
            'cost_factor': junior_workers_to_add * 1.0,
            'description': f'增加{junior_workers_to_add}名一般員工'
        })
    
    # 方案三：混合增加（效率最優）
    print(f"\n💡 方案三：混合增加（效率最優化）")
    
    # 使用剩餘時間先處理一部分
    remaining_senior_capacity = leftover_senior
    remaining_junior_capacity = leftover_junior
    
    # 計算利用剩餘時間可以完成多少工作
    work_by_leftover = 0
    remaining_gap = current_gap
    
    # 按難度優先級分配剩餘時間（簡單工作給一般員工，複雜工作給資深員工）
    for diff in sorted(difficulty_dist.keys(), reverse=True):  # 從高難度開始
        count = difficulty_dist[diff]
        senior_time_per_task = SENIOR_TIME[diff]
        junior_time_per_task = JUNIOR_TIME[diff]
        
        if diff <= 3:  # 高難度工作優先給資深員工
            tasks_possible_by_senior = min(count, remaining_senior_capacity // senior_time_per_task)
            work_by_leftover += tasks_possible_by_senior
            remaining_senior_capacity -= tasks_possible_by_senior * senior_time_per_task
            remaining_gap -= tasks_possible_by_senior
            
            remaining_count = count - tasks_possible_by_senior
            if remaining_count > 0:
                tasks_possible_by_junior = min(remaining_count, remaining_junior_capacity // junior_time_per_task)
                work_by_leftover += tasks_possible_by_junior
                remaining_junior_capacity -= tasks_possible_by_junior * junior_time_per_task
                remaining_gap -= tasks_possible_by_junior
        else:  # 低難度工作優先給一般員工
            tasks_possible_by_junior = min(count, remaining_junior_capacity // junior_time_per_task)
            work_by_leftover += tasks_possible_by_junior
            remaining_junior_capacity -= tasks_possible_by_junior * junior_time_per_task
            remaining_gap -= tasks_possible_by_junior
            
            remaining_count = count - tasks_possible_by_junior
            if remaining_count > 0:
                tasks_possible_by_senior = min(remaining_count, remaining_senior_capacity // senior_time_per_task)
                work_by_leftover += tasks_possible_by_senior
                remaining_senior_capacity -= tasks_possible_by_senior * senior_time_per_task
                remaining_gap -= tasks_possible_by_senior
    
    print(f"   利用剩餘時間可完成: {work_by_leftover} 件")
    print(f"   仍需處理: {remaining_gap} 件")
    
    if remaining_gap <= 0:
        print(f"   ✅ 現有人力配置足夠達成目標！")
        solutions.append({
            'type': '現有配置足夠',
            'senior_add': 0,
            'junior_add': 0,
            'cost_factor': 0,
            'description': '現有人力已足夠'
        })
    else:
        # 計算處理剩餘缺口的最優人力組合
        # 假設剩餘工作平均分配
        avg_senior_time = np.mean([SENIOR_TIME[d] for d in range(1, 8)])
        avg_junior_time = np.mean([JUNIOR_TIME[d] for d in range(1, 8)])
        
        # 嘗試不同的混合方案
        best_mix = None
        min_cost = float('inf')
        
        for senior_add in range(0, 6):
            for junior_add in range(0, 11):
                if senior_add == 0 and junior_add == 0:
                    continue
                
                additional_capacity = senior_add * WORK_HOURS_PER_DAY + junior_add * WORK_HOURS_PER_DAY
                # 估算可以完成的工作（使用加權平均時間）
                weighted_avg_time = (avg_senior_time + avg_junior_time) / 2
                estimated_completion = additional_capacity / weighted_avg_time
                
                if estimated_completion >= remaining_gap:
                    cost = senior_add * 1.5 + junior_add * 1.0
                    if cost < min_cost:
                        min_cost = cost
                        best_mix = (senior_add, junior_add)
        
        if best_mix:
            senior_add, junior_add = best_mix
            print(f"   ✅ 建議增加: {senior_add} 名資深員工 + {junior_add} 名一般員工")
            solutions.append({
                'type': '混合增加',
                'senior_add': senior_add,
                'junior_add': junior_add,
                'cost_factor': senior_add * 1.5 + junior_add * 1.0,
                'description': f'增加{senior_add}資深+{junior_add}一般員工'
            })
        else:
            print(f"   ⚠️ 無法找到合適的混合方案，建議使用單一類型增加")
    
    # 方案總結和推薦
    print(f"\n🏆 方案總結和推薦:")
    print("="*60)
    
    # 篩選有效方案
    valid_solutions = [s for s in solutions if s['senior_add'] > 0 or s['junior_add'] > 0 or s['cost_factor'] == 0]
    
    if not valid_solutions:
        print("❌ 未找到有效的解決方案")
        return
    
    # 按成本排序
    valid_solutions.sort(key=lambda x: x['cost_factor'])
    
    print(f"\n📊 方案對比（按成本排序）:")
    print("-" * 70)
    print(f"{'方案類型':<15} {'增加資深':<8} {'增加一般':<8} {'成本係數':<8} {'描述':<20}")
    print("-" * 70)
    
    for i, solution in enumerate(valid_solutions[:5]):  # 只顯示前5個方案
        marker = "⭐" if i == 0 else "  "
        print(f"{marker} {solution['type']:<15} {solution['senior_add']:<8} {solution['junior_add']:<8} {solution['cost_factor']:<8.1f} {solution['description']:<20}")
    
    # 推薦方案
    recommended = valid_solutions[0]
    
    print(f"\n🎯 **推薦方案：{recommended['type']}**")
    print(f"")
    print(f"   📈 **具體調整：**")
    print(f"   - 資深員工：{SENIOR_WORKERS} → {SENIOR_WORKERS + recommended['senior_add']} 人 (+{recommended['senior_add']}人)")
    print(f"   - 一般員工：{JUNIOR_WORKERS} → {JUNIOR_WORKERS + recommended['junior_add']} 人 (+{recommended['junior_add']}人)")
    print(f"   - 總人力：{SENIOR_WORKERS + JUNIOR_WORKERS} → {SENIOR_WORKERS + JUNIOR_WORKERS + recommended['senior_add'] + recommended['junior_add']} 人")
    
    if recommended['senior_add'] > 0 or recommended['junior_add'] > 0:
        total_increase = recommended['senior_add'] + recommended['junior_add']
        increase_percentage = (total_increase / (SENIOR_WORKERS + JUNIOR_WORKERS)) * 100
        print(f"   - 人力增加幅度：{increase_percentage:.1f}%")
        
        print(f"\n   💼 **預期效果：**")
        print(f"   - 可達成300件最低目標")
        print(f"   - 成本增加相對最小")
        print(f"   - 資源配置合理")
        
        print(f"\n   🔧 **config_params.py 修改建議：**")
        print(f"   ```python")
        print(f"   SENIOR_WORKERS = {SENIOR_WORKERS + recommended['senior_add']}  # 原 {SENIOR_WORKERS}")
        print(f"   JUNIOR_WORKERS = {JUNIOR_WORKERS + recommended['junior_add']}  # 原 {JUNIOR_WORKERS}")
        print(f"   ```")
    else:
        print(f"\n   ✅ **結論：現有人力配置已足夠達成目標！**")
    
    return recommended

def main():
    """主函數"""
    try:
        result = direct_workforce_calculation()
        
        if result:
            print(f"\n" + "="*80)
            print(f"✅ 人力需求計算完成")
            print(f"📊 推薦方案：{result['description']}")
            if result['cost_factor'] > 0:
                print(f"💰 預估成本影響：增加 {result['cost_factor']:.1f} 個成本單位")
            print(f"="*80)
        
    except Exception as e:
        print(f"❌ 計算過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 