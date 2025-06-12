import pandas as pd
import numpy as np
from collections import defaultdict
from config_params import *
import random
from employee_manager import load_external_employee_list
import json
import os

def assign_workers_to_tasks():
    """將工作分配給具體的員工並更新CSV"""
    
    # 讀取原始數據
    from path_utils import get_data_file_path
    df = pd.read_csv(get_data_file_path('result.csv'))
    
    print("🔍 使用統一策略管理器獲取最佳策略...")
    from strategy_manager import get_strategy_manager
    manager = get_strategy_manager()
    manager.load_data()
    best_assignment = manager.get_optimal_assignment()
    leftover_senior, leftover_junior = manager.get_leftover_time()
    
    # 轉換為我們需要的格式
    optimal_assignment = {}
    for difficulty, (senior_count, junior_count) in best_assignment.items():
        optimal_assignment[difficulty] = [senior_count, junior_count]
    
    print(f"📋 最佳分配方案:")
    for diff in sorted(optimal_assignment.keys()):
        senior_count, junior_count = optimal_assignment[diff]
        print(f"   難度 {diff}: 資深員工 {senior_count} 件, 一般員工 {junior_count} 件")
    
    print("=== 🎯 根據最佳策略分配工作給具體員工 ===")
    
    # 載入員工名單（支援外部輸入）
    senior_workers, junior_workers = load_external_employee_list()
    
    print(f"👥 員工名單:")
    print(f"   資深員工: {senior_workers}")
    print(f"   一般員工: {junior_workers}")
    
    # 按優先權和難度排序工作（與advanced_optimal_strategy一致）
    df_sorted = df.sort_values(['priority', 'difficulty']).reset_index(drop=True)
    
    # 追蹤每個員工的工作負載（分鐘）
    senior_workload = {worker: 0 for worker in senior_workers}
    junior_workload = {worker: 0 for worker in junior_workers}
    
    # 追蹤各難度的分配配額（來自最佳策略）
    remaining_quota = {}
    for difficulty, (senior_count, junior_count) in optimal_assignment.items():
        remaining_quota[difficulty] = {'senior': senior_count, 'junior': junior_count}
    
    # 新增分配欄位
    df_sorted['assigned_worker'] = 'UNASSIGNED'
    df_sorted['worker_type'] = 'UNASSIGNED'
    df_sorted['estimated_time'] = 0
    
    print(f"\n📋 開始按照最佳策略分配工作...")
    assigned_count = 0
    
    # 直接按照最佳策略的順序分配工作
    for idx, row in df_sorted.iterrows():
        difficulty = row['difficulty']
        
        # 檢查該難度的配額
        if difficulty not in remaining_quota:
            continue
            
        senior_quota = remaining_quota[difficulty]['senior']
        junior_quota = remaining_quota[difficulty]['junior']
        
        assigned = False
        
        # 優先按照策略分配：先資深員工配額，再一般員工配額
        if senior_quota > 0:
            # 找可用的資深員工
            available_senior = [w for w in senior_workers 
                              if senior_workload[w] + SENIOR_TIME[difficulty] <= WORK_HOURS_PER_DAY]
            if available_senior:
                assigned_worker = min(available_senior, key=lambda w: senior_workload[w])
                df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                df_sorted.loc[idx, 'worker_type'] = 'SENIOR'
                df_sorted.loc[idx, 'estimated_time'] = SENIOR_TIME[difficulty]
                senior_workload[assigned_worker] += SENIOR_TIME[difficulty]
                remaining_quota[difficulty]['senior'] -= 1
                assigned = True
                assigned_count += 1
        
        if not assigned and junior_quota > 0:
            # 找可用的一般員工
            available_junior = [w for w in junior_workers 
                               if junior_workload[w] + JUNIOR_TIME[difficulty] <= WORK_HOURS_PER_DAY]
            if available_junior:
                assigned_worker = min(available_junior, key=lambda w: junior_workload[w])
                df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                df_sorted.loc[idx, 'worker_type'] = 'JUNIOR'
                df_sorted.loc[idx, 'estimated_time'] = JUNIOR_TIME[difficulty]
                junior_workload[assigned_worker] += JUNIOR_TIME[difficulty]
                remaining_quota[difficulty]['junior'] -= 1
                assigned = True
                assigned_count += 1
        
        # 如果策略配額已用完，但還有剩餘時間，則繼續分配
        if not assigned:
            # 選擇效率更高的員工類型
            senior_time = SENIOR_TIME[difficulty]
            junior_time = JUNIOR_TIME[difficulty]
            
            if senior_time <= junior_time:
                # 資深員工更有效率，優先分配
                available_senior = [w for w in senior_workers 
                                  if senior_workload[w] + senior_time <= WORK_HOURS_PER_DAY]
                if available_senior:
                    assigned_worker = min(available_senior, key=lambda w: senior_workload[w])
                    df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                    df_sorted.loc[idx, 'worker_type'] = 'SENIOR'
                    df_sorted.loc[idx, 'estimated_time'] = senior_time
                    senior_workload[assigned_worker] += senior_time
                    assigned = True
                    assigned_count += 1
            
            if not assigned:
                # 分配給一般員工
                available_junior = [w for w in junior_workers 
                                   if junior_workload[w] + junior_time <= WORK_HOURS_PER_DAY]
                if available_junior:
                    assigned_worker = min(available_junior, key=lambda w: junior_workload[w])
                    df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                    df_sorted.loc[idx, 'worker_type'] = 'JUNIOR'
                    df_sorted.loc[idx, 'estimated_time'] = junior_time
                    junior_workload[assigned_worker] += junior_time
                    assigned = True
                    assigned_count += 1
    
    print(f"✅ 工作分配完成: {assigned_count} 件")
    
    # 生成統計報告
    total_assigned = len(df_sorted[df_sorted['assigned_worker'] != 'UNASSIGNED'])
    
    # 計算實際的剩餘時間
    actual_senior_used = sum(senior_workload.values())
    actual_junior_used = sum(junior_workload.values())
    actual_leftover_senior = SENIOR_WORKERS * WORK_HOURS_PER_DAY - actual_senior_used
    actual_leftover_junior = JUNIOR_WORKERS * WORK_HOURS_PER_DAY - actual_junior_used
    
    print(f"\n=== 📊 最終分配統計 ===")
    print(f"總工作數: {len(df_sorted)} 件")
    print(f"已分配工作: {total_assigned} 件")
    print(f"未分配工作: {len(df_sorted) - total_assigned} 件")
    print(f"分配完成率: {total_assigned/len(df_sorted)*100:.1f}%")
    print(f"資深員工時間利用率: {actual_senior_used/(SENIOR_WORKERS * WORK_HOURS_PER_DAY)*100:.1f}%")
    print(f"一般員工時間利用率: {actual_junior_used/(JUNIOR_WORKERS * WORK_HOURS_PER_DAY)*100:.1f}%")
    print(f"剩餘資深員工時間: {actual_leftover_senior} 分鐘")
    print(f"剩餘一般員工時間: {actual_leftover_junior} 分鐘")
    
    # 比較預期與實際的差異
    if abs(actual_leftover_senior - leftover_senior) > 5 or abs(actual_leftover_junior - leftover_junior) > 5:
        print(f"\n⚠️ 注意：實際剩餘時間與策略預期有差異")
        print(f"   策略預期剩餘：資深{leftover_senior}分鐘，一般{leftover_junior}分鐘")
        print(f"   實際剩餘：資深{actual_leftover_senior}分鐘，一般{actual_leftover_junior}分鐘")
    
    return df_sorted, senior_workload, junior_workload

def generate_global_statistics(df, senior_workload, junior_workload):
    """生成全局統計數據"""
    
    print(f"\n" + "="*60)
    print(f"📈 全局統計數據報告")
    print(f"="*60)
    
    # 基本統計
    total_tasks = len(df)
    assigned_tasks = len(df[df['assigned_worker'] != 'UNASSIGNED'])
    unassigned_tasks = total_tasks - assigned_tasks
    
    print(f"\n🎯 **工作分配概況**")
    print(f"   總工作數量: {total_tasks:,} 件")
    print(f"   已分配工作: {assigned_tasks:,} 件")
    print(f"   未分配工作: {unassigned_tasks:,} 件")
    print(f"   分配成功率: {assigned_tasks/total_tasks*100:.1f}%")
    
    # 按員工類型統計
    senior_assigned = len(df[df['worker_type'] == 'SENIOR'])
    junior_assigned = len(df[df['worker_type'] == 'JUNIOR'])
    
    print(f"\n👥 **員工類型分配**")
    print(f"   資深員工負責: {senior_assigned:,} 件 ({senior_assigned/assigned_tasks*100:.1f}%)")
    print(f"   一般員工負責: {junior_assigned:,} 件 ({junior_assigned/assigned_tasks*100:.1f}%)")
    
    # 工作負載統計
    print(f"\n⏱️ **工作負載分析**")
    print(f"   資深員工工作負載:")
    for worker, workload in senior_workload.items():
        utilization = workload / WORK_HOURS_PER_DAY * 100
        print(f"     {worker}: {workload:3d}分鐘 ({utilization:5.1f}%)")
    
    avg_senior_workload = np.mean(list(senior_workload.values()))
    avg_senior_utilization = avg_senior_workload / WORK_HOURS_PER_DAY * 100
    
    print(f"   資深員工平均負載: {avg_senior_workload:.1f}分鐘 ({avg_senior_utilization:.1f}%)")
    
    print(f"\n   一般員工工作負載:")
    for worker, workload in junior_workload.items():
        utilization = workload / WORK_HOURS_PER_DAY * 100
        print(f"     {worker}: {workload:3d}分鐘 ({utilization:5.1f}%)")
    
    avg_junior_workload = np.mean(list(junior_workload.values()))
    avg_junior_utilization = avg_junior_workload / WORK_HOURS_PER_DAY * 100
    
    print(f"   一般員工平均負載: {avg_junior_workload:.1f}分鐘 ({avg_junior_utilization:.1f}%)")
    
    # 按難度統計
    print(f"\n🎯 **難度分佈統計**")
    assigned_df = df[df['assigned_worker'] != 'UNASSIGNED']
    
    for difficulty in sorted(assigned_df['difficulty'].unique()):
        diff_tasks = assigned_df[assigned_df['difficulty'] == difficulty]
        senior_count = len(diff_tasks[diff_tasks['worker_type'] == 'SENIOR'])
        junior_count = len(diff_tasks[diff_tasks['worker_type'] == 'JUNIOR'])
        total_count = len(diff_tasks)
        
        print(f"   難度 {difficulty}: {total_count:3d}件 (資深:{senior_count:2d}, 一般:{junior_count:2d})")
    
    # 按優先權統計
    print(f"\n🚨 **優先權完成統計**")
    for priority in sorted(assigned_df['priority'].unique()):
        priority_tasks = df[df['priority'] == priority]
        assigned_priority = assigned_df[assigned_df['priority'] == priority]
        completion_rate = len(assigned_priority) / len(priority_tasks) * 100
        
        print(f"   優先權 {priority}: {len(assigned_priority):3d}/{len(priority_tasks):3d}件 ({completion_rate:5.1f}%)")
    
    # 時間統計
    total_estimated_time = assigned_df['estimated_time'].sum()
    total_available_time = (SENIOR_WORKERS + JUNIOR_WORKERS) * WORK_HOURS_PER_DAY
    overall_utilization = total_estimated_time / total_available_time * 100
    
    print(f"\n⚡ **整體效率分析**")
    print(f"   總預估工時: {total_estimated_time:,} 分鐘")
    print(f"   總可用工時: {total_available_time:,} 分鐘")
    print(f"   整體利用率: {overall_utilization:.1f}%")
    print(f"   剩餘工時: {total_available_time - total_estimated_time:,} 分鐘")
    
    # 目標達成情況
    print(f"\n🎯 **目標達成情況**")
    meets_target = assigned_tasks >= MINIMUM_WORK_TARGET
    print(f"   最低目標: {MINIMUM_WORK_TARGET} 件")
    print(f"   實際完成: {assigned_tasks} 件")
    print(f"   目標達成: {'✅ 是' if meets_target else '❌ 否'}")
    
    if meets_target:
        excess = assigned_tasks - MINIMUM_WORK_TARGET
        print(f"   超額完成: {excess} 件 ({excess/MINIMUM_WORK_TARGET*100:.1f}%)")
    else:
        shortage = MINIMUM_WORK_TARGET - assigned_tasks
        print(f"   缺少完成: {shortage} 件")
    
    return {
        'total_tasks': total_tasks,
        'assigned_tasks': assigned_tasks,
        'unassigned_tasks': unassigned_tasks,
        'assignment_rate': assigned_tasks/total_tasks*100,
        'senior_assigned': senior_assigned,
        'junior_assigned': junior_assigned,
        'avg_senior_utilization': avg_senior_utilization,
        'avg_junior_utilization': avg_junior_utilization,
        'overall_utilization': overall_utilization,
        'meets_target': meets_target,
        'senior_workload': senior_workload,
        'junior_workload': junior_workload
    }

def assign_workers_with_json_input(assigned_worker_json: str = None, worker_type_json: str = None):
    """使用JSON格式輸入分配工作給員工
    
    Args:
        assigned_worker_json: JSON格式的員工分配信息
            格式範例: '{"senior_workers": ["陈明华", "李建国"], "junior_workers": ["黄小敏", "周文杰"]}'
        worker_type_json: JSON格式的員工類型信息
            格式範例: '{"陈明华": "SENIOR", "李建国": "SENIOR", "黄小敏": "JUNIOR", "周文杰": "JUNIOR"}'
    
    Returns:
        DataFrame: 包含分配結果的數據框
    """
    print("=== 🎯 使用JSON輸入分配工作給員工 ===")
    
    # 讀取原始數據
    from path_utils import get_data_file_path
    df = pd.read_csv(get_data_file_path('result.csv'))
    
    # 解析JSON輸入
    if assigned_worker_json:
        try:
            assigned_worker_data = json.loads(assigned_worker_json)
            senior_workers = assigned_worker_data.get('senior_workers', [])
            junior_workers = assigned_worker_data.get('junior_workers', [])
            print(f"✅ 使用JSON輸入的員工名單:")
            print(f"   資深員工: {senior_workers}")
            print(f"   一般員工: {junior_workers}")
            # 更新實際員工數量
            actual_senior_count = len(senior_workers)
            actual_junior_count = len(junior_workers)
            print(f"📊 實際員工數量: 資深{actual_senior_count}人, 一般{actual_junior_count}人 (不依賴config設定)")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失敗: {e}")
            print("🔄 回退使用預設員工名單")
            senior_workers, junior_workers = load_external_employee_list()
            actual_senior_count = len(senior_workers)
            actual_junior_count = len(junior_workers)
    else:
        print("📋 使用預設員工名單")
        senior_workers, junior_workers = load_external_employee_list()
        actual_senior_count = len(senior_workers)
        actual_junior_count = len(junior_workers)
    
    # 解析員工類型JSON (可選)
    worker_type_mapping = {}
    if worker_type_json:
        try:
            worker_type_mapping = json.loads(worker_type_json)
            print(f"✅ 使用JSON輸入的員工類型映射:")
            for worker, wtype in worker_type_mapping.items():
                print(f"   {worker}: {wtype}")
        except json.JSONDecodeError as e:
            print(f"❌ 員工類型JSON解析失敗: {e}")
    
    # 獲取最佳策略 - 使用實際員工數量重新計算
    print("🔍 使用統一策略管理器獲取最佳策略...")
    from strategy_manager import get_strategy_manager
    manager = get_strategy_manager()
    manager.load_data()
    
    # 如果員工數量與config不同，給出提示
    if actual_senior_count != SENIOR_WORKERS or actual_junior_count != JUNIOR_WORKERS:
        print(f"⚠️ 實際員工數量與config不符，將基於實際人數進行分配...")
        print(f"   config設定: 資深{SENIOR_WORKERS}人/一般{JUNIOR_WORKERS}人")
        print(f"   實際人數: 資深{actual_senior_count}人/一般{actual_junior_count}人")
    
    best_assignment = manager.get_optimal_assignment()
    
    # 轉換為我們需要的格式
    optimal_assignment = {}
    for difficulty, (senior_count, junior_count) in best_assignment.items():
        optimal_assignment[difficulty] = [senior_count, junior_count]
    
    print(f"📋 最佳分配方案 (基於{actual_senior_count}資深+{actual_junior_count}一般員工):")
    for diff in sorted(optimal_assignment.keys()):
        senior_count, junior_count = optimal_assignment[diff]
        print(f"   難度 {diff}: 資深員工 {senior_count} 件, 一般員工 {junior_count} 件")
    
    # 按優先權和難度排序工作
    df_sorted = df.sort_values(['priority', 'difficulty']).reset_index(drop=True)
    
    # 追蹤每個員工的工作負載（分鐘） - 使用實際員工名單
    senior_workload = {worker: 0 for worker in senior_workers}
    junior_workload = {worker: 0 for worker in junior_workers}
    
    # 計算總可用工時 (使用實際員工數量)
    total_senior_hours = actual_senior_count * WORK_HOURS_PER_DAY
    total_junior_hours = actual_junior_count * WORK_HOURS_PER_DAY
    print(f"📊 總可用工時: 資深員工{total_senior_hours}分鐘, 一般員工{total_junior_hours}分鐘")
    
    # 追蹤各難度的分配配額
    remaining_quota = {}
    for difficulty, (senior_count, junior_count) in optimal_assignment.items():
        remaining_quota[difficulty] = {'senior': senior_count, 'junior': junior_count}
    
    # 新增分配欄位
    df_sorted['assigned_worker'] = 'UNASSIGNED'
    df_sorted['worker_type'] = 'UNASSIGNED'
    df_sorted['estimated_time'] = 0
    
    print(f"\n📋 開始按照最佳策略分配工作...")
    assigned_count = 0
    
    # 執行工作分配邏輯
    for idx, row in df_sorted.iterrows():
        difficulty = row['difficulty']
        
        if difficulty not in remaining_quota:
            continue
            
        senior_quota = remaining_quota[difficulty]['senior']
        junior_quota = remaining_quota[difficulty]['junior']
        
        assigned = False
        
        # 優先按照策略分配：先資深員工配額，再一般員工配額
        if senior_quota > 0:
            available_senior = [w for w in senior_workers 
                              if senior_workload[w] + SENIOR_TIME[difficulty] <= WORK_HOURS_PER_DAY]
            if available_senior:
                assigned_worker = min(available_senior, key=lambda w: senior_workload[w])
                df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                df_sorted.loc[idx, 'worker_type'] = 'SENIOR'
                df_sorted.loc[idx, 'estimated_time'] = SENIOR_TIME[difficulty]
                senior_workload[assigned_worker] += SENIOR_TIME[difficulty]
                remaining_quota[difficulty]['senior'] -= 1
                assigned = True
                assigned_count += 1
        
        if not assigned and junior_quota > 0:
            available_junior = [w for w in junior_workers 
                               if junior_workload[w] + JUNIOR_TIME[difficulty] <= WORK_HOURS_PER_DAY]
            if available_junior:
                assigned_worker = min(available_junior, key=lambda w: junior_workload[w])
                df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                df_sorted.loc[idx, 'worker_type'] = 'JUNIOR'
                df_sorted.loc[idx, 'estimated_time'] = JUNIOR_TIME[difficulty]
                junior_workload[assigned_worker] += JUNIOR_TIME[difficulty]
                remaining_quota[difficulty]['junior'] -= 1
                assigned = True
                assigned_count += 1
        
        # 如果策略配額已用完，但還有剩餘時間，則繼續分配
        if not assigned:
            senior_time = SENIOR_TIME[difficulty]
            junior_time = JUNIOR_TIME[difficulty]
            
            if senior_time <= junior_time:
                available_senior = [w for w in senior_workers 
                                  if senior_workload[w] + senior_time <= WORK_HOURS_PER_DAY]
                if available_senior:
                    assigned_worker = min(available_senior, key=lambda w: senior_workload[w])
                    df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                    df_sorted.loc[idx, 'worker_type'] = 'SENIOR'
                    df_sorted.loc[idx, 'estimated_time'] = senior_time
                    senior_workload[assigned_worker] += senior_time
                    assigned = True
                    assigned_count += 1
            
            if not assigned:
                available_junior = [w for w in junior_workers 
                                   if junior_workload[w] + junior_time <= WORK_HOURS_PER_DAY]
                if available_junior:
                    assigned_worker = min(available_junior, key=lambda w: junior_workload[w])
                    df_sorted.loc[idx, 'assigned_worker'] = assigned_worker
                    df_sorted.loc[idx, 'worker_type'] = 'JUNIOR'
                    df_sorted.loc[idx, 'estimated_time'] = junior_time
                    junior_workload[assigned_worker] += junior_time
                    assigned = True
                    assigned_count += 1
    
    print(f"✅ 工作分配完成: {assigned_count} 件")
    
    # 生成分配結果的JSON格式
    assignment_result_json = {
        "assignment_summary": {
            "total_tasks": len(df_sorted),
            "assigned_tasks": assigned_count,
            "assignment_rate": f"{assigned_count/len(df_sorted)*100:.1f}%"
        },
        "worker_assignments": {}
    }
    
    # 整理每個員工的分配結果
    for worker in senior_workers + junior_workers:
        worker_tasks = df_sorted[df_sorted['assigned_worker'] == worker]
        if not worker_tasks.empty:
            assignment_result_json["worker_assignments"][worker] = {
                "worker_type": "SENIOR" if worker in senior_workers else "JUNIOR",
                "total_tasks": len(worker_tasks),
                "total_time": worker_tasks['estimated_time'].sum(),
                "workload_percentage": f"{(worker_tasks['estimated_time'].sum() / WORK_HOURS_PER_DAY * 100):.1f}%",
                "tasks": worker_tasks[['priority', 'difficulty', 'estimated_time']].to_dict('records')
            }
    
    # 保存JSON結果
    result_json_path = "result/assignment_results.json"
    os.makedirs(os.path.dirname(result_json_path), exist_ok=True)
    with open(result_json_path, 'w', encoding='utf-8') as f:
        json.dump(assignment_result_json, f, ensure_ascii=False, indent=2)
    
    print(f"📄 分配結果JSON已保存: {result_json_path}")
    
    return df_sorted, senior_workload, junior_workload, assignment_result_json

def main():
    """主函數"""
    # 執行分配
    print("開始執行工作分配...")
    updated_df, senior_workload, junior_workload = assign_workers_to_tasks()

    # 生成統計數據
    stats = generate_global_statistics(updated_df, senior_workload, junior_workload)

    # 儲存更新後的CSV
    from path_utils import get_result_file_path
    output_filename = get_result_file_path('result_with_assignments.csv')
    updated_df.to_csv(output_filename, index=False)

    print(f"\n" + "="*60)
    print(f"✅ 分配結果已儲存至: {output_filename}")
    print(f"📊 包含以下新欄位:")
    print(f"   - assigned_worker: 分配的具體員工")
    print(f"   - worker_type: 員工類型 (SENIOR/JUNIOR)")
    print(f"   - estimated_time: 預估完成時間(分鐘)")
    print("="*60)

    # 儲存統計摘要
    summary_filename = get_result_file_path('assignment_summary.txt')
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("工作分配統計摘要\n")
        f.write("="*50 + "\n")
        f.write(f"生成時間: {pd.Timestamp.now()}\n\n")
        
        f.write(f"基本統計:\n")
        f.write(f"  總工作數量: {stats['total_tasks']} 件\n")
        f.write(f"  已分配工作: {stats['assigned_tasks']} 件\n")
        f.write(f"  分配成功率: {stats['assignment_rate']:.1f}%\n")
        f.write(f"  目標達成: {'是' if stats['meets_target'] else '否'}\n\n")
        
        f.write(f"員工利用率:\n")
        f.write(f"  資深員工平均: {stats['avg_senior_utilization']:.1f}%\n")
        f.write(f"  一般員工平均: {stats['avg_junior_utilization']:.1f}%\n")
        f.write(f"  整體利用率: {stats['overall_utilization']:.1f}%\n")

    print(f"📋 統計摘要已儲存至: {summary_filename}")
    
    return updated_df, stats

if __name__ == "__main__":
    main() 