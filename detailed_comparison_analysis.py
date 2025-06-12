#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime
import os

def detailed_assignment_comparison():
    """詳細對比原始分配和AI優化分配的結果"""
    
    # 檔案路徑
    original_file = 'result/original_assignments_baseline.csv'
    optimized_file = 'result/ai_optimized_assignments_current.csv'
    
    if not os.path.exists(original_file):
        print(f"❌ 找不到原始分配文件: {original_file}")
        return
    
    if not os.path.exists(optimized_file):
        print(f"❌ 找不到AI優化分配文件: {optimized_file}")
        return
    
    # 讀取數據
    df_original = pd.read_csv(original_file)
    df_optimized = pd.read_csv(optimized_file)
    
    print("🔍 原始分配 vs AI優化分配 - 詳細對比分析")
    print("="*80)
    
    # 基本統計對比
    print("\n📊 基本統計對比")
    print("-"*50)
    
    # 原始數據統計
    orig_total = len(df_original)
    orig_assigned = len(df_original[df_original['assigned_worker'] != 'UNASSIGNED'])
    orig_rate = (orig_assigned / orig_total) * 100
    
    # AI優化數據統計  
    opt_total = len(df_optimized)
    opt_assigned = len(df_optimized[df_optimized['assigned_worker'] != 'UNASSIGNED'])
    opt_rate = (opt_assigned / opt_total) * 100
    
    print(f"{'項目':<20} {'原始分配':<15} {'AI優化分配':<15} {'改進':<15}")
    print("-"*65)
    print(f"{'總任務數':<20} {orig_total:<15} {opt_total:<15} {opt_total-orig_total:+}")
    print(f"{'已分配任務':<20} {orig_assigned:<15} {opt_assigned:<15} {opt_assigned-orig_assigned:+}")
    print(f"{'未分配任務':<20} {orig_total-orig_assigned:<15} {opt_total-opt_assigned:<15} {(opt_total-opt_assigned)-(orig_total-orig_assigned):+}")
    print(f"{'分配成功率':<20} {orig_rate:.1f}%{'':<9} {opt_rate:.1f}%{'':<9} {opt_rate-orig_rate:+.1f}%")
    
    # 員工類型分配對比
    print("\n👥 員工類型分配對比")
    print("-"*50)
    
    # 原始分配
    orig_assigned_df = df_original[df_original['assigned_worker'] != 'UNASSIGNED']
    orig_senior = len(orig_assigned_df[orig_assigned_df['worker_type'] == 'SENIOR'])
    orig_junior = len(orig_assigned_df[orig_assigned_df['worker_type'] == 'JUNIOR'])
    
    # AI優化分配
    opt_assigned_df = df_optimized[df_optimized['assigned_worker'] != 'UNASSIGNED']
    opt_senior = len(opt_assigned_df[opt_assigned_df['worker_type'] == 'SENIOR'])
    opt_junior = len(opt_assigned_df[opt_assigned_df['worker_type'] == 'JUNIOR'])
    
    print(f"{'類型':<15} {'原始分配':<15} {'AI優化分配':<15} {'改進':<15}")
    print("-"*60)
    print(f"{'資深員工':<15} {orig_senior:<15} {opt_senior:<15} {opt_senior-orig_senior:+}")
    print(f"{'一般員工':<15} {orig_junior:<15} {opt_junior:<15} {opt_junior-orig_junior:+}")
    
    # 難度分佈對比
    print("\n🎯 難度分佈對比")
    print("-"*50)
    
    print(f"{'難度':<8} {'原始分配':<12} {'AI優化分配':<12} {'改進':<10} {'原始資深':<10} {'AI資深':<10} {'原始一般':<10} {'AI一般':<10}")
    print("-"*80)
    
    for diff in sorted(df_original['difficulty'].unique()):
        # 原始分配統計
        orig_diff_total = len(orig_assigned_df[orig_assigned_df['difficulty'] == diff])
        orig_diff_senior = len(orig_assigned_df[(orig_assigned_df['difficulty'] == diff) & (orig_assigned_df['worker_type'] == 'SENIOR')])
        orig_diff_junior = len(orig_assigned_df[(orig_assigned_df['difficulty'] == diff) & (orig_assigned_df['worker_type'] == 'JUNIOR')])
        
        # AI優化分配統計
        opt_diff_total = len(opt_assigned_df[opt_assigned_df['difficulty'] == diff])
        opt_diff_senior = len(opt_assigned_df[(opt_assigned_df['difficulty'] == diff) & (opt_assigned_df['worker_type'] == 'SENIOR')])
        opt_diff_junior = len(opt_assigned_df[(opt_assigned_df['difficulty'] == diff) & (opt_assigned_df['worker_type'] == 'JUNIOR')])
        
        improvement = opt_diff_total - orig_diff_total
        
        print(f"難度{diff:<3} {orig_diff_total:<12} {opt_diff_total:<12} {improvement:+<10} {orig_diff_senior:<10} {opt_diff_senior:<10} {orig_diff_junior:<10} {opt_diff_junior:<10}")
    
    # 優先級處理對比
    print("\n⭐ 優先級處理對比")
    print("-"*50)
    
    vip_orig = len(df_original[df_original['is_vip'] == True])
    vip_orig_assigned = len(orig_assigned_df[orig_assigned_df['is_vip'] == True])
    vip_opt = len(df_optimized[df_optimized['is_vip'] == True])
    vip_opt_assigned = len(opt_assigned_df[opt_assigned_df['is_vip'] == True])
    
    top_orig = len(df_original[df_original['is_top_job'] == True])
    top_orig_assigned = len(orig_assigned_df[orig_assigned_df['is_top_job'] == True])
    top_opt = len(df_optimized[df_optimized['is_top_job'] == True])
    top_opt_assigned = len(opt_assigned_df[opt_assigned_df['is_top_job'] == True])
    
    simple_orig = len(df_original[df_original['is_simple_work'] == True])
    simple_orig_assigned = len(orig_assigned_df[orig_assigned_df['is_simple_work'] == True])
    simple_opt = len(df_optimized[df_optimized['is_simple_work'] == True])
    simple_opt_assigned = len(opt_assigned_df[opt_assigned_df['is_simple_work'] == True])
    
    print(f"{'類型':<15} {'原始':<20} {'AI優化':<20} {'改進':<15}")
    print("-"*70)
    print(f"{'VIP任務':<15} {vip_orig_assigned}/{vip_orig} ({vip_orig_assigned/vip_orig*100:.1f}%){'':<5} {vip_opt_assigned}/{vip_opt} ({vip_opt_assigned/vip_opt*100:.1f}%){'':<5} {vip_opt_assigned-vip_orig_assigned:+}")
    print(f"{'TOP任務':<15} {top_orig_assigned}/{top_orig} ({top_orig_assigned/top_orig*100:.1f}%){'':<5} {top_opt_assigned}/{top_opt} ({top_opt_assigned/top_opt*100:.1f}%){'':<5} {top_opt_assigned-top_orig_assigned:+}")
    print(f"{'簡單任務':<15} {simple_orig_assigned}/{simple_orig} ({simple_orig_assigned/simple_orig*100:.1f}%){'':<3} {simple_opt_assigned}/{simple_opt} ({simple_opt_assigned/simple_opt*100:.1f}%){'':<3} {simple_opt_assigned-simple_orig_assigned:+}")
    
    # 個別員工負載對比
    print("\n🔍 個別員工負載對比")
    print("-"*50)
    
    # 原始員工負載
    orig_worker_loads = orig_assigned_df['assigned_worker'].value_counts().sort_index()
    opt_worker_loads = opt_assigned_df['assigned_worker'].value_counts().sort_index()
    
    print("資深員工負載對比:")
    senior_workers = [w for w in orig_worker_loads.index if 'SENIOR' in w]
    for worker in sorted(senior_workers):
        orig_load = orig_worker_loads.get(worker, 0)
        opt_load = opt_worker_loads.get(worker, 0)
        improvement = opt_load - orig_load
        print(f"  {worker:<18}: {orig_load}件 → {opt_load}件 ({improvement:+})")
    
    print("\n一般員工負載對比:")
    junior_workers = [w for w in orig_worker_loads.index if 'JUNIOR' in w]
    for worker in sorted(junior_workers):
        orig_load = orig_worker_loads.get(worker, 0)
        opt_load = opt_worker_loads.get(worker, 0)
        improvement = opt_load - orig_load
        print(f"  {worker:<18}: {orig_load}件 → {opt_load}件 ({improvement:+})")
    
    # 新增的員工（如果有的話）
    new_workers = set(opt_worker_loads.index) - set(orig_worker_loads.index)
    if new_workers:
        print("\n新增員工:")
        for worker in sorted(new_workers):
            opt_load = opt_worker_loads.get(worker, 0)
            print(f"  {worker:<18}: 0件 → {opt_load}件 (新增)")
    
    # 詳細分配清單對比 - 前20項工作
    print("\n📋 詳細分配清單對比 (前20項工作)")
    print("-"*80)
    print(f"{'ID':<8} {'難度':<6} {'VIP':<5} {'TOP':<5} {'原始分配':<18} {'AI優化分配':<18} {'變化'}")
    print("-"*80)
    
    # 合併數據進行對比
    comparison_df = pd.merge(
        df_original[['measure_record_oid', 'difficulty', 'is_vip', 'is_top_job', 'assigned_worker', 'worker_type']].add_suffix('_orig'),
        df_optimized[['measure_record_oid', 'difficulty', 'is_vip', 'is_top_job', 'assigned_worker', 'worker_type']].add_suffix('_opt'),
        left_on='measure_record_oid_orig',
        right_on='measure_record_oid_opt',
        how='inner'
    )
    
    # 只顯示前20項變化
    changes = comparison_df[comparison_df['assigned_worker_orig'] != comparison_df['assigned_worker_opt']].head(20)
    
    for _, row in changes.iterrows():
        task_id = str(row['measure_record_oid_orig'])[:8]
        difficulty = row['difficulty_orig']
        is_vip = '✓' if row['is_vip_orig'] else '✗'
        is_top = '✓' if row['is_top_job_orig'] else '✗'
        orig_worker = row['assigned_worker_orig'] if row['assigned_worker_orig'] != 'UNASSIGNED' else '未分配'
        opt_worker = row['assigned_worker_opt'] if row['assigned_worker_opt'] != 'UNASSIGNED' else '未分配'
        
        if orig_worker != opt_worker:
            change_type = "重新分配" if orig_worker != '未分配' and opt_worker != '未分配' else \
                         "新增分配" if orig_worker == '未分配' else "取消分配"
        else:
            change_type = "無變化"
        
        print(f"{task_id:<8} {difficulty:<6} {is_vip:<5} {is_top:<5} {orig_worker:<18} {opt_worker:<18} {change_type}")
    
    # 生成詳細對比報告CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_report_file = f'result/detailed_comparison_report_{timestamp}.csv'
    
    # 準備詳細對比數據
    comparison_summary = []
    
    # 基本統計數據
    comparison_summary.append({
        '分析項目': '基本統計',
        '指標': '總任務數',
        '原始值': orig_total,
        '優化值': opt_total,
        '改進': opt_total - orig_total,
        '改進率': f"{((opt_total - orig_total) / orig_total * 100):.1f}%" if orig_total > 0 else "N/A"
    })
    
    comparison_summary.append({
        '分析項目': '基本統計',
        '指標': '已分配任務',
        '原始值': orig_assigned,
        '優化值': opt_assigned,
        '改進': opt_assigned - orig_assigned,
        '改進率': f"{((opt_assigned - orig_assigned) / orig_assigned * 100):.1f}%" if orig_assigned > 0 else "N/A"
    })
    
    comparison_summary.append({
        '分析項目': '基本統計',
        '指標': '分配成功率',
        '原始值': f"{orig_rate:.1f}%",
        '優化值': f"{opt_rate:.1f}%",
        '改進': f"{opt_rate - orig_rate:+.1f}%",
        '改進率': f"{((opt_rate - orig_rate) / orig_rate * 100):.1f}%" if orig_rate > 0 else "N/A"
    })
    
    # 保存對比報告
    comparison_df_export = pd.DataFrame(comparison_summary)
    comparison_df_export.to_csv(comparison_report_file, index=False, encoding='utf-8-sig')
    
    print(f"\n📄 詳細對比報告已保存至: {comparison_report_file}")
    
    # 生成完整的任務變化清單
    full_changes_file = f'result/task_changes_detail_{timestamp}.csv'
    
    # 找出所有變化的任務
    all_changes = comparison_df[comparison_df['assigned_worker_orig'] != comparison_df['assigned_worker_opt']]
    
    if len(all_changes) > 0:
        changes_export = all_changes[['measure_record_oid_orig', 'difficulty_orig', 'is_vip_orig', 'is_top_job_orig', 
                                     'assigned_worker_orig', 'worker_type_orig', 
                                     'assigned_worker_opt', 'worker_type_opt']].copy()
        
        changes_export.columns = ['任務ID', '難度', 'VIP', 'TOP任務', '原始分配員工', '原始員工類型', 'AI優化分配員工', 'AI優化員工類型']
        changes_export.to_csv(full_changes_file, index=False, encoding='utf-8-sig')
        
        print(f"📄 任務變化詳細清單已保存至: {full_changes_file}")
        print(f"📊 共有 {len(all_changes)} 項任務的分配發生變化")
    
    # 總結
    print(f"\n🎯 對比分析總結")
    print("-"*50)
    print(f"✅ AI優化成效:")
    print(f"   • 分配成功率提升: {opt_rate - orig_rate:+.1f}%")
    print(f"   • 新增分配任務: {opt_assigned - orig_assigned:+} 件")
    print(f"   • 減少未分配任務: {(orig_total-orig_assigned) - (opt_total-opt_assigned):+} 件")
    
    if len(all_changes) > 0:
        print(f"   • 共優化 {len(all_changes)} 項任務的分配")
    
    return {
        'original_stats': {'total': orig_total, 'assigned': orig_assigned, 'rate': orig_rate},
        'optimized_stats': {'total': opt_total, 'assigned': opt_assigned, 'rate': opt_rate},
        'improvements': {'assigned_diff': opt_assigned - orig_assigned, 'rate_diff': opt_rate - orig_rate},
        'changes_count': len(all_changes) if len(all_changes) > 0 else 0
    }

if __name__ == "__main__":
    results = detailed_assignment_comparison() 