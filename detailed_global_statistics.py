#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細全局統計模組
=================

生成工作分配的詳細統計報告，包括：
- 工作分配概況
- 員工工作負載分析
- 難度分佈統計
- 優先權完成分析
- 整體效率分析
- 目標達成評估
- 性能評估與建議
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_params import *
from employee_manager import get_actual_employee_counts, load_external_employee_list
from path_utils import get_result_file_path

def get_display_width(text):
    """計算字符串的實際顯示寬度"""
    text = str(text)
    width = 0
    for char in text:
        # 簡化判斷：ASCII字符為1，非ASCII字符為2
        if ord(char) < 128:
            width += 1
        else:
            width += 2
    return width

def format_cell(text, width, align='left'):
    """格式化單元格內容，確保固定寬度"""
    text = str(text)
    current_width = get_display_width(text)
    
    # 如果超長，截斷處理
    if current_width > width:
        truncated = ""
        temp_width = 0
        for char in text:
            char_width = 1 if ord(char) < 128 else 2
            if temp_width + char_width <= width:
                truncated += char
                temp_width += char_width
            else:
                break
        text = truncated
        current_width = temp_width
    
    # 計算需要的空格數
    spaces_needed = width - current_width
    
    if align == 'center':
        left_spaces = spaces_needed // 2
        right_spaces = spaces_needed - left_spaces
        return ' ' * left_spaces + text + ' ' * right_spaces
    elif align == 'right':
        return ' ' * spaces_needed + text
    else:  # left
        return text + ' ' * spaces_needed

def generate_report_content(df, assigned_df, total_tasks, assigned_tasks, unassigned_tasks, assignment_rate, work_data=None, employee_data=None):
    """生成完整的報告內容（字符串格式）
    
    Args:
        df: 原始工作數據
        assigned_df: 已分配工作數據
        total_tasks: 總工作數
        assigned_tasks: 已分配工作數
        unassigned_tasks: 未分配工作數
        assignment_rate: 分配成功率
        work_data: 外部工作數據（可選）
        employee_data: 外部員工數據（可選）
    """
    
    # 使用策略管理器獲取統一的統計信息
    from strategy_manager import get_strategy_manager
    strategy_manager = get_strategy_manager(work_data=work_data, employee_data=employee_data)
    strategy_summary = strategy_manager.get_strategy_summary()
    
    # 使用 StrategyManager 的統一員工名單提取邏輯
    senior_workers, junior_workers = strategy_manager.get_employee_lists()
    
    report_lines = []
    
    report_lines.append("="*80)
    report_lines.append("📊 詳細統計分析報告")
    report_lines.append("="*80)
    report_lines.append(f"📅 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # === 基本概況 ===
    report_lines.append("\n📋 【工作分配概況】")
    report_lines.append("| 項目 | 數量 | 比例 |")
    report_lines.append("|------|-----:|-----:|")
    report_lines.append(f"| 總工作數量 | {total_tasks} 件 | 100.0% |")
    report_lines.append(f"| 已分配工作 | {assigned_tasks} 件 | {assignment_rate:.1f}% |")
    report_lines.append(f"| 未分配工作 | {unassigned_tasks} 件 | {(unassigned_tasks/total_tasks)*100:.1f}% |")
    
    # === 員工類型分配統計 ===
    senior_tasks = len(assigned_df[assigned_df['worker_type'] == 'SENIOR'])
    junior_tasks = len(assigned_df[assigned_df['worker_type'] == 'JUNIOR'])
    
    report_lines.append("\n👥 【員工類型分配】")
    report_lines.append("| 員工類型 | 分配數量 | 占比 |")
    report_lines.append("|---------|--------:|-----:|")
    report_lines.append(f"| 資深員工 | {senior_tasks} 件 | {(senior_tasks/assigned_tasks)*100:.1f}% |")
    report_lines.append(f"| 一般員工 | {junior_tasks} 件 | {(junior_tasks/assigned_tasks)*100:.1f}% |")
    
    # === 資深員工工作負載 ===
    report_lines.append("\n⚡ 【資深員工工作負載】")
    report_lines.append("| 員工編號 | 工作時間 | 利用率 | 工作數 |")
    report_lines.append("|----------|--------:|-------:|-------:|")
    
    senior_workloads = {}
    for worker_name in senior_workers:
        worker_tasks = assigned_df[assigned_df['assigned_worker'] == worker_name]
        workload = worker_tasks['estimated_time'].sum()
        utilization = (workload / WORK_HOURS_PER_DAY) * 100
        task_count = len(worker_tasks)
        senior_workloads[worker_name] = workload
        
        report_lines.append(f"| {worker_name} | {workload}分鐘 | {utilization:.1f}% | {task_count}件 |")
    
    avg_senior_workload = np.mean(list(senior_workloads.values())) if senior_workloads else 0
    avg_senior_utilization = (avg_senior_workload / WORK_HOURS_PER_DAY) * 100
    senior_count = len(senior_workers)
    report_lines.append(f"| **平均** | **{avg_senior_workload:.0f}分鐘** | **{avg_senior_utilization:.1f}%** | **{senior_tasks/senior_count:.1f}件** |")
    
    # === 一般員工工作負載 ===
    report_lines.append("\n⚡ 【一般員工工作負載】")
    report_lines.append("| 員工編號 | 工作時間 | 利用率 | 工作數 |")
    report_lines.append("|----------|--------:|-------:|-------:|")
    
    junior_workloads = {}
    for worker_name in junior_workers:
        worker_tasks = assigned_df[assigned_df['assigned_worker'] == worker_name]
        workload = worker_tasks['estimated_time'].sum()
        utilization = (workload / WORK_HOURS_PER_DAY) * 100
        task_count = len(worker_tasks)
        junior_workloads[worker_name] = workload
        
        report_lines.append(f"| {worker_name} | {workload}分鐘 | {utilization:.1f}% | {task_count}件 |")
    
    avg_junior_workload = np.mean(list(junior_workloads.values())) if junior_workloads else 0
    avg_junior_utilization = (avg_junior_workload / WORK_HOURS_PER_DAY) * 100
    junior_count = len(junior_workers)
    report_lines.append(f"| **平均** | **{avg_junior_workload:.0f}分鐘** | **{avg_junior_utilization:.1f}%** | **{junior_tasks/junior_count:.1f}件** |")
    
    # === 難度分佈分析 ===
    report_lines.append("\n🎯 【難度分佈統計】")
    report_lines.append("| 難度 | 總數量 | 資深員工 | 一般員工 | 資深占比 |")
    report_lines.append("|:----:|-------:|---------:|---------:|---------:|")
    
    difficulty_stats = {}
    for difficulty in sorted(assigned_df['difficulty'].unique()):
        diff_tasks = assigned_df[assigned_df['difficulty'] == difficulty]
        senior_count = len(diff_tasks[diff_tasks['worker_type'] == 'SENIOR'])
        junior_count = len(diff_tasks[diff_tasks['worker_type'] == 'JUNIOR'])
        total_count = len(diff_tasks)
        senior_ratio = (senior_count / total_count) * 100 if total_count > 0 else 0
        
        difficulty_stats[difficulty] = {
            'total': total_count,
            'senior': senior_count,
            'junior': junior_count,
            'senior_ratio': senior_ratio
        }
        
        report_lines.append(f"| 難度 {difficulty} | {total_count} 件 | {senior_count} 件 | {junior_count} 件 | {senior_ratio:.1f}% |")
    
    # === 優先權完成分析 ===
    report_lines.append("\n🚨 【優先權完成統計】")
    report_lines.append("| 優先權 | 總數量 | 已完成 | 完成率 | 完成狀態 |")
    report_lines.append("|:------:|-------:|-------:|-------:|:--------:|")
    
    priority_stats = {}
    for priority in sorted(df['priority'].unique()):
        priority_tasks = df[df['priority'] == priority]
        assigned_priority = assigned_df[assigned_df['priority'] == priority]
        total_priority = len(priority_tasks)
        completed_priority = len(assigned_priority)
        completion_rate = (completed_priority / total_priority) * 100
        
        status = "✅ 完成" if completion_rate == 100 else "⚠️ 部分完成" if completion_rate >= 80 else "❌ 未達標"
        
        priority_stats[priority] = {
            'total': total_priority,
            'completed': completed_priority,
            'completion_rate': completion_rate
        }
        
        report_lines.append(f"| 優先權{priority} | {total_priority} 件 | {completed_priority} 件 | {completion_rate:.1f}% | {status} |")
    
    # === 整體效率分析 === 使用策略管理器統一計算
    report_lines.append("\n⚡ 【整體效率分析】")
    report_lines.append("| 效率指標 | 數值 | 說明 |")
    report_lines.append("|----------|-----:|------|")
    report_lines.append(f"| 資深員工利用率 | {strategy_summary['senior_utilization']*100:.1f}% | 資深員工工時使用效率 |")
    report_lines.append(f"| 一般員工利用率 | {strategy_summary['junior_utilization']*100:.1f}% | 一般員工工時使用效率 |")
    report_lines.append(f"| 整體利用率 | {strategy_summary['overall_utilization']*100:.1f}% | 整體工時使用效率 |")
    report_lines.append(f"| 剩餘資深員工時間 | {strategy_summary['leftover_senior']:,} 分鐘 | 資深員工剩餘工作時間 |")
    report_lines.append(f"| 剩餘一般員工時間 | {strategy_summary['leftover_junior']:,} 分鐘 | 一般員工剩餘工作時間 |")
    total_remaining = strategy_summary['leftover_senior'] + strategy_summary['leftover_junior']
    report_lines.append(f"| 總剩餘工時 | {total_remaining:,} 分鐘 | 約 {total_remaining/60:.1f} 小時的餘裕 |")
    
    # === 目標達成分析 === 使用策略管理器統一計算
    target_completion = (assigned_tasks / strategy_summary['parameters']['minimum_work_target']) * 100
    
    report_lines.append("\n🎯 【目標達成分析】")
    report_lines.append("| 目標項目 | 數值 | 狀態 |")
    report_lines.append("|----------|-----:|:----:|")
    report_lines.append(f"| 最低完成目標 | {strategy_summary['parameters']['minimum_work_target']:,} 件 | 設定的最低要求 |")
    report_lines.append(f"| 實際完成數量 | {assigned_tasks:,} 件 | 實際分配完成的工作 |")
    report_lines.append(f"| 目標完成率 | {target_completion:.1f}% | {'✅ 超額達成' if strategy_summary['meets_minimum'] else '❌ 未達標準'} |")
    
    if strategy_summary['meets_minimum']:
        excess = assigned_tasks - strategy_summary['parameters']['minimum_work_target']
        excess_rate = (excess / strategy_summary['parameters']['minimum_work_target']) * 100
        report_lines.append(f"| 超額完成數量 | {excess:,} 件 | 超出目標的工作數量 |")
        report_lines.append(f"| 超額完成率 | {excess_rate:.1f}% | 相對於目標的超額比例 |")
    else:
        shortage = strategy_summary['parameters']['minimum_work_target'] - assigned_tasks
        shortage_rate = (shortage / strategy_summary['parameters']['minimum_work_target']) * 100
        report_lines.append(f"| 缺少完成數量 | {shortage:,} 件 | 未達到目標的工作數量 |")
        report_lines.append(f"| 缺口率 | {shortage_rate:.1f}% | 相對於目標的缺口比例 |")
    
    # === 性能評估 ===
    report_lines.append("\n📈 【性能評估與建議】")
    
    # 計算各種指標
    high_priority_completion = priority_stats[1]['completion_rate'] if 1 in priority_stats else 0
    resource_utilization = strategy_summary['overall_utilization'] * 100
    workload_balance = 100 - (np.std(list(senior_workloads.values()) + list(junior_workloads.values())) / np.mean(list(senior_workloads.values()) + list(junior_workloads.values())) * 100) if (senior_workloads or junior_workloads) else 100
    
    report_lines.append("✅ 優點:")
    if high_priority_completion == 100:
        report_lines.append("   • 優先權1工作100%完成 - 關鍵任務得到妥善處理")
    if strategy_summary['meets_minimum']:
        report_lines.append(f"   • 超額完成工作目標 - 達成{target_completion:.1f}%的目標完成率")
    if resource_utilization >= 95:
        report_lines.append(f"   • 資源利用率極高 - {resource_utilization:.1f}%的工時使用效率")
    if workload_balance >= 80:
        report_lines.append("   • 工作負載分配均衡 - 員工工作量分配合理")
    
    report_lines.append("\n⚠️ 改進建議:")
    if unassigned_tasks > 0:
        report_lines.append(f"   • 仍有{unassigned_tasks}件工作未分配，建議考慮:")
        report_lines.append("     - 增加工作時間或員工數量")
        report_lines.append("     - 調整工作難度評估")
        report_lines.append("     - 優化分配算法")
    
    if total_remaining < 60:  # 少於1小時
        report_lines.append("   • 工作安排非常緊湊，建議預留更多緩衝時間")
    
    low_completion_priorities = [p for p, stats in priority_stats.items() if stats['completion_rate'] < 80]
    if low_completion_priorities:
        report_lines.append(f"   • 優先權{low_completion_priorities}的完成率較低，需要重點關注")
    
    # 返回統計數據和報告內容
    summary_data = {
        'generated_time': datetime.now(),
        'total_tasks': total_tasks,
        'assigned_tasks': assigned_tasks,
        'assignment_rate': assignment_rate,
        'meets_target': strategy_summary['meets_minimum'],
        'target_completion_rate': target_completion,
        'overall_utilization': strategy_summary['overall_utilization'] * 100,
        'senior_utilization': strategy_summary['senior_utilization'] * 100,
        'junior_utilization': strategy_summary['junior_utilization'] * 100,
        'leftover_senior': strategy_summary['leftover_senior'],
        'leftover_junior': strategy_summary['leftover_junior'],
        'difficulty_stats': difficulty_stats,
        'priority_stats': priority_stats,
        'senior_workloads': senior_workloads,
        'junior_workloads': junior_workloads,
        'strategy_summary': strategy_summary  # 添加完整的策略摘要
    }
    
    return summary_data, report_lines

def generate_detailed_statistics(work_data=None, employee_data=None, result_file=None):
    """生成詳細統計分析
    
    Args:
        work_data: 工作數據 DataFrame，如果為 None 則讀取本地 CSV
        employee_data: 員工數據，如果為 None 則讀取本地 CSV
        result_file: 結果文件路徑，如果為 None 則使用默認路徑
    """
    
    # 讀取分配結果
    if work_data is not None:
        # 使用外部數據
        df = work_data
    else:
        # 讀取本地文件
        if result_file is None:
            result_file = get_result_file_path('result_with_assignments.csv')
        
        if not os.path.exists(result_file):
            print(f"❌ 找不到分配結果檔案: {result_file}")
            return None, None
        
        df = pd.read_csv(result_file)
    
    # 基本統計
    total_tasks = len(df)
    assigned_df = df[df['assigned_worker'] != 'UNASSIGNED']
    assigned_tasks = len(assigned_df)
    unassigned_tasks = total_tasks - assigned_tasks
    assignment_rate = (assigned_tasks / total_tasks) * 100
    
    # 生成報告內容
    summary_data, report_lines = generate_report_content(
        df, assigned_df, total_tasks, assigned_tasks, unassigned_tasks, assignment_rate,
        work_data=work_data, employee_data=employee_data
    )
    
    # 輸出到控制台
    for line in report_lines:
        print(line)
    
    return summary_data, report_lines

def main():
    """主函數"""
    # 執行統計分析
    print("生成詳細統計報告...")
    stats, report_lines = generate_detailed_statistics()
    
    if stats is None:
        print("❌ 統計分析失敗")
        return None

    # 保存完整的詳細報告到文件
    report_file = get_result_file_path('detailed_statistics_report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        # 寫入完整的報告內容
        for line in report_lines:
            f.write(line + '\n')

    print(f"\n{'='*80}")
    print(f"📋 詳細統計報告已保存至: {report_file}")
    print(f"📊 包含完整的工作分配分析和性能評估")
    print(f"{'='*80}") 
    
    return stats

if __name__ == "__main__":
    main() 