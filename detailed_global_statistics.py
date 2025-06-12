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

def generate_report_content(df, assigned_df, total_tasks, assigned_tasks, unassigned_tasks, assignment_rate):
    """生成完整的報告內容（字符串格式）"""
    
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
    for i in range(1, SENIOR_WORKERS + 1):
        worker_name = f"SENIOR_WORKER_{i}"
        worker_tasks = assigned_df[assigned_df['assigned_worker'] == worker_name]
        workload = worker_tasks['estimated_time'].sum()
        utilization = (workload / WORK_HOURS_PER_DAY) * 100
        task_count = len(worker_tasks)
        senior_workloads[worker_name] = workload
        
        report_lines.append(f"| {worker_name} | {workload}分鐘 | {utilization:.1f}% | {task_count}件 |")
    
    avg_senior_workload = np.mean(list(senior_workloads.values()))
    avg_senior_utilization = (avg_senior_workload / WORK_HOURS_PER_DAY) * 100
    report_lines.append(f"| **平均** | **{avg_senior_workload:.0f}分鐘** | **{avg_senior_utilization:.1f}%** | **{senior_tasks/SENIOR_WORKERS:.1f}件** |")
    
    # === 一般員工工作負載 ===
    report_lines.append("\n⚡ 【一般員工工作負載】")
    report_lines.append("| 員工編號 | 工作時間 | 利用率 | 工作數 |")
    report_lines.append("|----------|--------:|-------:|-------:|")
    
    junior_workloads = {}
    for i in range(1, JUNIOR_WORKERS + 1):
        worker_name = f"JUNIOR_WORKER_{i}"
        worker_tasks = assigned_df[assigned_df['assigned_worker'] == worker_name]
        workload = worker_tasks['estimated_time'].sum()
        utilization = (workload / WORK_HOURS_PER_DAY) * 100
        task_count = len(worker_tasks)
        junior_workloads[worker_name] = workload
        
        report_lines.append(f"| {worker_name} | {workload}分鐘 | {utilization:.1f}% | {task_count}件 |")
    
    avg_junior_workload = np.mean(list(junior_workloads.values()))
    avg_junior_utilization = (avg_junior_workload / WORK_HOURS_PER_DAY) * 100
    report_lines.append(f"| **平均** | **{avg_junior_workload:.0f}分鐘** | **{avg_junior_utilization:.1f}%** | **{junior_tasks/JUNIOR_WORKERS:.1f}件** |")
    
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
    
    # === 整體效率分析 ===
    total_estimated_time = assigned_df['estimated_time'].sum()
    total_available_time = (SENIOR_WORKERS + JUNIOR_WORKERS) * WORK_HOURS_PER_DAY
    overall_utilization = (total_estimated_time / total_available_time) * 100
    remaining_time = total_available_time - total_estimated_time
    
    report_lines.append("\n⚡ 【整體效率分析】")
    report_lines.append("| 效率指標 | 數值 | 說明 |")
    report_lines.append("|----------|-----:|------|")
    report_lines.append(f"| 總預估工時 | {total_estimated_time:,} 分鐘 | 所有已分配工作的預估時間 |")
    report_lines.append(f"| 總可用工時 | {total_available_time:,} 分鐘 | 15名員工 × 8小時 |")
    report_lines.append(f"| 整體利用率 | {overall_utilization:.1f}% | 工時使用效率 |")
    report_lines.append(f"| 剩餘工時 | {remaining_time:,} 分鐘 | 未使用的工作時間 |")
    report_lines.append(f"| 剩餘工時(小時) | {remaining_time/60:.1f} 小時 | 約 {remaining_time/60:.1f} 小時的餘裕 |")
    
    # === 目標達成分析 ===
    meets_target = assigned_tasks >= MINIMUM_WORK_TARGET
    target_completion = (assigned_tasks / MINIMUM_WORK_TARGET) * 100
    
    report_lines.append("\n🎯 【目標達成分析】")
    report_lines.append("| 目標項目 | 數值 | 狀態 |")
    report_lines.append("|----------|-----:|:----:|")
    report_lines.append(f"| 最低完成目標 | {MINIMUM_WORK_TARGET:,} 件 | 設定的最低要求 |")
    report_lines.append(f"| 實際完成數量 | {assigned_tasks:,} 件 | 實際分配完成的工作 |")
    report_lines.append(f"| 目標完成率 | {target_completion:.1f}% | {'✅ 超額達成' if meets_target else '❌ 未達標準'} |")
    
    if meets_target:
        excess = assigned_tasks - MINIMUM_WORK_TARGET
        excess_rate = (excess / MINIMUM_WORK_TARGET) * 100
        report_lines.append(f"| 超額完成數量 | {excess:,} 件 | 超出目標的工作數量 |")
        report_lines.append(f"| 超額完成率 | {excess_rate:.1f}% | 相對於目標的超額比例 |")
    else:
        shortage = MINIMUM_WORK_TARGET - assigned_tasks
        shortage_rate = (shortage / MINIMUM_WORK_TARGET) * 100
        report_lines.append(f"| 缺少完成數量 | {shortage:,} 件 | 未達到目標的工作數量 |")
        report_lines.append(f"| 缺口率 | {shortage_rate:.1f}% | 相對於目標的缺口比例 |")
    
    # === 性能評估 ===
    report_lines.append("\n📈 【性能評估與建議】")
    
    # 計算各種指標
    high_priority_completion = priority_stats[1]['completion_rate']
    resource_utilization = overall_utilization
    workload_balance = 100 - (np.std(list(senior_workloads.values()) + list(junior_workloads.values())) / np.mean(list(senior_workloads.values()) + list(junior_workloads.values())) * 100)
    
    report_lines.append("✅ 優點:")
    if high_priority_completion == 100:
        report_lines.append("   • 優先權1工作100%完成 - 關鍵任務得到妥善處理")
    if meets_target:
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
    
    if remaining_time < 60:  # 少於1小時
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
        'meets_target': meets_target,
        'target_completion_rate': target_completion,
        'overall_utilization': overall_utilization,
        'senior_utilization': avg_senior_utilization,
        'junior_utilization': avg_junior_utilization,
        'difficulty_stats': difficulty_stats,
        'priority_stats': priority_stats,
        'senior_workloads': senior_workloads,
        'junior_workloads': junior_workloads
    }
    
    return summary_data, report_lines

def generate_detailed_statistics():
    """生成詳細統計分析"""
    
    # 讀取分配結果
    from path_utils import get_result_file_path
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
    summary_data, report_lines = generate_report_content(df, assigned_df, total_tasks, assigned_tasks, unassigned_tasks, assignment_rate)
    
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
    from path_utils import get_result_file_path
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