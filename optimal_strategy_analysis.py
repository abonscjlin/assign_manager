import pandas as pd
import numpy as np
from collections import defaultdict
from config_params import *

def advanced_optimal_strategy(df, senior_workers=None, junior_workers=None, 
                            work_hours_per_day=None, minimum_work_target=None,
                            senior_time=None, junior_time=None, verbose=True):
    """進階最佳化策略：考慮多種因素的動態分配
    
    Args:
        df: 工作數據DataFrame
        senior_workers: 資深技師人數，如果為None則使用config值
        junior_workers: 一般技師人數，如果為None則使用config值
        work_hours_per_day: 每人每日工時，如果為None則使用config值
        minimum_work_target: 最低工作目標，如果為None則使用config值
        senior_time: 資深技師時間配置，如果為None則使用config值
        junior_time: 一般技師時間配置，如果為None則使用config值
        verbose: 是否輸出詳細信息
    
    Returns:
        tuple: (assignment, remaining_senior_time, remaining_junior_time)
    """
    
    # 使用外部參數或默認config值
    _senior_workers = senior_workers if senior_workers is not None else SENIOR_WORKERS
    _junior_workers = junior_workers if junior_workers is not None else JUNIOR_WORKERS
    _work_hours_per_day = work_hours_per_day if work_hours_per_day is not None else WORK_HOURS_PER_DAY
    _minimum_work_target = minimum_work_target if minimum_work_target is not None else MINIMUM_WORK_TARGET
    _senior_time = senior_time if senior_time is not None else SENIOR_TIME
    _junior_time = junior_time if junior_time is not None else JUNIOR_TIME
    
    assignment = defaultdict(lambda: [0, 0])  # [senior_count, junior_count]
    
    # 按優先權和難度綜合排序
    # 優先權1必須最先完成，其次考慮難度
    df_sorted = df.sort_values(['priority', 'difficulty'])
    
    remaining_senior_time = _senior_workers * _work_hours_per_day
    remaining_junior_time = _junior_workers * _work_hours_per_day
    
    completed_count = 0
    priority_1_completed = 0
    
    # 第一階段：確保所有優先權1的工作完成
    priority_1_work = df[df['priority'] == 1].sort_values('difficulty')
    
    for _, row in priority_1_work.iterrows():
        diff = row['difficulty']
        senior_time = _senior_time[diff]
        junior_time = _junior_time[diff]
        
        # 優先權1的工作優先給資深技師（除非資深技師時間不足）
        if remaining_senior_time >= senior_time:
            assignment[diff][0] += 1
            remaining_senior_time -= senior_time
        elif remaining_junior_time >= junior_time:
            assignment[diff][1] += 1
            remaining_junior_time -= junior_time
        else:
            if verbose:
                print(f"⚠️ 警告：無法完成優先權1的難度{diff}工作")
            continue
        
        priority_1_completed += 1
        completed_count += 1
    
    if verbose:
        print(f"✅ 優先權1工作完成: {priority_1_completed}/{len(priority_1_work)} 件")
    
    # 第二階段：高效分配其他工作，確保達到最低目標要求
    other_work = df[df['priority'] != 1].sort_values(['priority', 'difficulty'])
    
    for _, row in other_work.iterrows():
        if completed_count >= _minimum_work_target:
            # 已達到最低要求，開始按照效率優化
            break
            
        diff = row['difficulty']
        senior_time = _senior_time[diff]
        junior_time = _junior_time[diff]
        
        # 選擇最高效的分配方式
        if remaining_senior_time >= senior_time and remaining_junior_time >= junior_time:
            # 兩種選擇都可行，選擇更經濟的方案
            senior_efficiency = 1 / senior_time  # 每分鐘完成件數
            junior_efficiency = 1 / junior_time
            
            if senior_efficiency >= junior_efficiency:
                assignment[diff][0] += 1
                remaining_senior_time -= senior_time
            else:
                assignment[diff][1] += 1
                remaining_junior_time -= junior_time
        elif remaining_senior_time >= senior_time:
            assignment[diff][0] += 1
            remaining_senior_time -= senior_time
        elif remaining_junior_time >= junior_time:
            assignment[diff][1] += 1
            remaining_junior_time -= junior_time
        else:
            continue
        
        completed_count += 1
    
    # 第三階段：用剩餘時間完成更多工作，優先選擇最簡單的
    if completed_count < len(df):
        remaining_work = df.iloc[completed_count:].sort_values('difficulty', ascending=True)  # 從簡單到難（1->7）
        
        for _, row in remaining_work.iterrows():
            diff = row['difficulty']
            senior_time = _senior_time[diff]
            junior_time = _junior_time[diff]
            
            # 剩餘時間優先給一般技師處理簡單工作
            if remaining_junior_time >= junior_time:
                assignment[diff][1] += 1
                remaining_junior_time -= junior_time
                completed_count += 1
            elif remaining_senior_time >= senior_time:
                assignment[diff][0] += 1
                remaining_senior_time -= senior_time
                completed_count += 1
    
    return dict(assignment), remaining_senior_time, remaining_junior_time

def main():
    """主函數"""
    # 讀取CSV數據
    from path_utils import get_data_file_path
    df = pd.read_csv(get_data_file_path('result.csv'))
    
    # 執行進階最佳策略
    print("=== 🎯 進階最佳化策略分析 ===")
    print(f"當前參數設定：目標 {MINIMUM_WORK_TARGET} 件/天，資深技師 {SENIOR_WORKERS} 人，一般技師 {JUNIOR_WORKERS} 人")
    optimal_assignment, leftover_senior, leftover_junior = advanced_optimal_strategy(df)

    # 使用config中的參數值（供後續計算使用）
    _senior_workers = SENIOR_WORKERS
    _junior_workers = JUNIOR_WORKERS
    _work_hours_per_day = WORK_HOURS_PER_DAY
    _minimum_work_target = MINIMUM_WORK_TARGET
    _senior_time = SENIOR_TIME
    _junior_time = JUNIOR_TIME

    # 計算結果
    total_completed = sum(sum(counts) for counts in optimal_assignment.values())
    total_senior_assigned = sum(counts[0] for counts in optimal_assignment.values())
    total_junior_assigned = sum(counts[1] for counts in optimal_assignment.values())

    senior_time_used = _senior_workers * _work_hours_per_day - leftover_senior
    junior_time_used = _junior_workers * _work_hours_per_day - leftover_junior

    print(f"\n=== 📊 最佳策略執行結果 ===")
    print(f"完成工作總數: {total_completed} 件")
    print(f"資深技師分配: {total_senior_assigned} 件")
    print(f"一般技師分配: {total_junior_assigned} 件")
    print(f"資深技師時間利用率: {senior_time_used/(_senior_workers * _work_hours_per_day)*100:.1f}%")
    print(f"一般技師時間利用率: {junior_time_used/(_junior_workers * _work_hours_per_day)*100:.1f}%")
    print(f"剩餘資深技師時間: {leftover_senior} 分鐘")
    print(f"剩餘一般技師時間: {leftover_junior} 分鐘")

    if total_completed >= _minimum_work_target:
        print(f"✅ 成功達到每日最少{_minimum_work_target}件要求")
    else:
        print(f"❌ 未達到最少{_minimum_work_target}件要求，缺少 {_minimum_work_target - total_completed} 件")

    # 詳細分配表
    print(f"\n=== 📋 最佳策略詳細工作分配 ===")
    print("難度 | 資深技師 | 一般技師 | 小計 | 資深用時 | 一般用時")
    print("-" * 55)
    total_senior_time = 0
    total_junior_time = 0

    for diff in sorted(optimal_assignment.keys()):
        senior_count, junior_count = optimal_assignment[diff]
        subtotal = senior_count + junior_count
        senior_time_for_diff = senior_count * _senior_time[diff]
        junior_time_for_diff = junior_count * _junior_time[diff]
        total_senior_time += senior_time_for_diff
        total_junior_time += junior_time_for_diff
        
        print(f"  {diff}  |    {senior_count:3d}    |    {junior_count:3d}    | {subtotal:3d}  |  {senior_time_for_diff:4d}分  |  {junior_time_for_diff:4d}分")

    print("-" * 55)
    print(f"合計 |   {total_senior_assigned:4d}   |   {total_junior_assigned:4d}   | {total_completed:3d}  | {total_senior_time:5d}分 | {total_junior_time:5d}分")

    # 優先權完成情況分析
    print(f"\n=== 🎯 各優先權完成情況 ===")
    priority_completion = {}
    
    # 建立臨時分配副本來追蹤可用容量，不修改原始分配
    temp_assignment = {diff: [counts[0], counts[1]] for diff, counts in optimal_assignment.items()}
    
    for priority in sorted(df['priority'].unique()):
        priority_work = df[df['priority'] == priority]
        total_priority_work = len(priority_work)
        
        completed_priority_work = 0
        for _, row in priority_work.iterrows():
            diff = row['difficulty']
            if diff in temp_assignment:
                senior_assigned, junior_assigned = temp_assignment[diff]
                if senior_assigned + junior_assigned > 0:
                    completed_priority_work += 1
                    # 從臨時副本減少計數（不影響原始分配數據）
                    if senior_assigned > 0:
                        temp_assignment[diff][0] -= 1
                    elif junior_assigned > 0:
                        temp_assignment[diff][1] -= 1
        
        completion_rate = completed_priority_work / total_priority_work * 100
        priority_completion[priority] = completion_rate
        print(f"優先權 {priority}: {completed_priority_work}/{total_priority_work} 件 ({completion_rate:.1f}%)")

    # 實施建議
    print(f"\n=== 💡 實施建議 ===")
    print("1. **詳細人員配置與工作分配**:")
    
    # 計算資深技師的實際工作分布
    senior_high_diff = sum(optimal_assignment.get(diff, [0, 0])[0] for diff in HIGH_DIFFICULTY_LEVELS)
    senior_mid_low_diff = sum(optimal_assignment.get(diff, [0, 0])[0] for diff in MEDIUM_DIFFICULTY_LEVELS + LOW_DIFFICULTY_LEVELS)
    
    print(f"   📋 資深技師 ({_senior_workers}人) 工作分配:")
    print(f"     • 高難度工作 (6-7級): {senior_high_diff}件 ({senior_high_diff/total_senior_assigned*100:.1f}%)")
    for diff in HIGH_DIFFICULTY_LEVELS:
        if diff in optimal_assignment and optimal_assignment[diff][0] > 0:
            time_per_diff = optimal_assignment[diff][0] * _senior_time[diff]
            print(f"       - 難度{diff}: {optimal_assignment[diff][0]}件 (預計{time_per_diff}分鐘)")
    
    if senior_mid_low_diff > 0:
        print(f"     • 中低難度工作 (1-5級): {senior_mid_low_diff}件 ({senior_mid_low_diff/total_senior_assigned*100:.1f}%)")
        for diff in MEDIUM_DIFFICULTY_LEVELS + LOW_DIFFICULTY_LEVELS:
            if diff in optimal_assignment and optimal_assignment[diff][0] > 0:
                time_per_diff = optimal_assignment[diff][0] * _senior_time[diff]
                print(f"       - 難度{diff}: {optimal_assignment[diff][0]}件 (預計{time_per_diff}分鐘)")

    print(f"\n   👥 一般技師 ({_junior_workers}人) 工作分配:")
    for diff in sorted(optimal_assignment.keys()):
        if optimal_assignment[diff][1] > 0:
            time_per_diff = optimal_assignment[diff][1] * _junior_time[diff]
            avg_per_worker = optimal_assignment[diff][1] / _junior_workers
            print(f"     • 難度{diff}: {optimal_assignment[diff][1]}件 (預計{time_per_diff}分鐘, 平均{avg_per_worker:.1f}件/人)")

    print("\n2. **分階段實施時程建議**:")
    print("   🕐 **上午時段 (09:00-12:00):**")
    print("     • 資深技師：優先處理所有優先權1工作")
    print("     • 一般技師：開始處理優先權2-3的中等難度工作")
    print("     • 預期完成：優先權1工作100%，優先權2工作50%")
    
    print("\n   🕑 **下午時段 (13:00-17:00):**")
    print("     • 資深技師：專攻高難度工作(6-7級)，協助處理優先權4工作")
    print("     • 一般技師：大量處理優先權4工作，開始優先權5工作")
    print("     • 預期完成：達到300件基本目標")
    
    print("\n   🕕 **加班時段 (如需要):**")
    print("     • 處理剩餘的優先權5-6工作")
    print(f"     • 利用剩餘{leftover_junior}分鐘處理低優先權工作")

    print("\n3. **智能效率優化策略**:")
    utilization_rate = (senior_time_used + junior_time_used) / ((_senior_workers + _junior_workers) * _work_hours_per_day)
    
    if utilization_rate > 0.98:
        print("   ⚠️  **高負荷警告 (99%+利用率):**")
        print("     • 建議增加15分鐘緩衝時間應對突發狀況")
        print("     • 考慮將部分優先權6工作安排到次日")
        print("     • 設立緊急支援機制")
    
    if leftover_junior > 15:
        print(f"   ⏰ **剩餘時間優化 ({leftover_junior}分鐘):**")
        possible_extra = leftover_junior // max(_junior_time.values())
        print(f"     • 可額外完成約{possible_extra}件簡單工作")
        print("     • 安排技師技能提升培訓")
        print("     • 準備次日工作預處理")
    
    # 效率提升建議
    print("\n   📈 **效率提升措施:**")
    if senior_mid_low_diff > 20:
        print(f"     • 資深技師處理了{senior_mid_low_diff}件中低難度工作，建議:")
        print("       - 培訓一般技師提升技能，承接部分中等難度工作")
        print("       - 建立工作轉移機制，釋放資深技師處理高難度工作")
    
    print("     • 建立工作配對制：1名資深技師指導2名一般技師")
    print("     • 實施工作標準化，減少重複溝通成本")
    print("     • 建立工作完成檢核表，確保品質")

    # 風險分析與應對策略
    print(f"\n=== ⚠️ 風險分析與應對策略 ===")
    high_difficulty_work = len(df[df['difficulty'].isin(HIGH_DIFFICULTY_LEVELS)])
    senior_high_diff_capacity = sum(optimal_assignment.get(diff, [0, 0])[0] for diff in HIGH_DIFFICULTY_LEVELS)
    uncompleted = len(df) - total_completed
    
    print("📋 **風險等級評估：**")
    
    # 高難度工作風險
    if high_difficulty_work > senior_high_diff_capacity:
        shortage = high_difficulty_work - senior_high_diff_capacity
        print(f"🔴 **高風險：高難度工作產能不足**")
        print(f"   • 高難度工作需求：{high_difficulty_work}件")
        print(f"   • 資深技師處理能力：{senior_high_diff_capacity}件")
        print(f"   • 缺口：{shortage}件")
        print(f"   💡 **應對措施：**")
        print(f"     - 緊急培訓2-3名一般技師處理難度5工作")
        print(f"     - 建立資深技師輪班制，延長工作時間")
        print(f"     - 考慮外包部分高難度工作")
    
    # 未完成工作風險
    if uncompleted > 0:
        uncompleted_rate = uncompleted / len(df) * 100
        if uncompleted_rate > 10:
            risk_level = "🔴 高風險"
        elif uncompleted_rate > 5:
            risk_level = "🟡 中風險"
        else:
            risk_level = "🟢 低風險"
            
        print(f"{risk_level}：**未完成工作 ({uncompleted}件, {uncompleted_rate:.1f}%)**")
        print(f"   💡 **應對措施：**")
        print(f"     - 建立次日優先處理機制")
        print(f"     - 設定工作延遲通知系統")
        if uncompleted > 20:
            print(f"     - 考慮增加臨時人力或延長工作時間")
    
    # 資源利用率風險
    utilization_rate = (senior_time_used + junior_time_used) / ((_senior_workers + _junior_workers) * _work_hours_per_day)
    if utilization_rate > 0.98:
        print(f"🟡 **中風險：資源利用率過高 ({utilization_rate*100:.1f}%)**")
        print(f"   • 缺乏應對突發狀況的緩衝時間")
        print(f"   💡 **應對措施：**")
        print(f"     - 預留10-15分鐘緊急時間")
        print(f"     - 建立工作優先級動態調整機制")
        print(f"     - 準備備用人力支援方案")
    
    # 優先權完成風險 (調整合理的風險閾值)
    priority_5_rate = priority_completion.get(5, 0)
    priority_6_rate = priority_completion.get(6, 0)
    
    # 優先權5：70%以下才算風險，因為它是較低優先級工作
    if priority_5_rate < 70:
        print(f"🟡 **中風險：優先權5完成率偏低 ({priority_5_rate:.1f}%)**")
        print(f"   💡 **應對措施：**")
        print(f"     - 調整午休後工作重點到優先權5")
        print(f"     - 安排資深技師重點支援")
    elif priority_5_rate >= 70:
        print(f"🟢 **良好：優先權5完成率 ({priority_5_rate:.1f}%) - 表現良好**")
        print(f"   💡 **優化建議：**")
        print(f"     - 維持當前分配策略")
        print(f"     - 可考慮利用剩餘時間提高完成率")
    
    # 優先權6：50%以下才算需要關注
    if priority_6_rate < 50:
        print(f"🟡 **中風險：優先權6完成率偏低 ({priority_6_rate:.1f}%)**")
        print(f"   💡 **應對措施：**")
        print(f"     - 安排到次日優先處理")
        print(f"     - 考慮延長工作時間處理")
    else:
        print(f"🟢 **可接受：優先權6完成率 ({priority_6_rate:.1f}%) - 符合預期**")
        print(f"   💡 **優化建議：**")
        print(f"     - 利用剩餘時間儘量多完成")
        print(f"     - 安排到次日優先處理")
    
    print(f"\n🛡️ **整體風險控制策略：**")
    print(f"   • 建立每日工作進度檢視點 (10:00, 14:00, 16:00)")
    print(f"   • 設立工作延遲預警機制 (超過預期時間20%)")
    print(f"   • 準備彈性調配方案 (人員互援、工作重新分配)")
    print(f"   • 建立品質檢核機制，確保在時間壓力下維持工作品質")

    print("\n=== 🎯 關鍵績效指標 (KPI) ===")
    print(f"📊 工作完成率: {total_completed/len(df)*100:.1f}%")
    print(f"📊 人力利用率: {(senior_time_used + junior_time_used)/((_senior_workers + _junior_workers) * _work_hours_per_day)*100:.1f}%")
    print(f"📊 最低要求達成: {'✅ 是' if total_completed >= _minimum_work_target else '❌ 否'}")
    print(f"📊 優先權1完成率: {priority_completion.get(1, 0):.1f}%")

    print(f"\n🔧 **調整參數建議**:")
    print(f"   - 若需提高完成率，可考慮增加人力或調整 _minimum_work_target")
    print(f"   - 當前設定可在 config_params.py 中修改")
    
    return optimal_assignment, leftover_senior, leftover_junior

if __name__ == "__main__":
    main() 