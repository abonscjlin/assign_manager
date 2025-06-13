#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD格式分析報告生成器
生成結構化的Markdown格式工作分配分析報告
"""

import os
import pandas as pd
from datetime import datetime
from config_params import MINIMUM_WORK_TARGET, SENIOR_TIME, JUNIOR_TIME
from employee_manager import get_actual_employee_counts

class MDReportGenerator:
    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.report_data = {}
        
    def collect_data(self):
        """收集所有相關數據"""
        # 讀取分配結果
        result_file = os.path.join(self.script_dir, "result/result_with_assignments.csv")
        if os.path.exists(result_file):
            self.report_data['df'] = pd.read_csv(result_file)
        
        # 執行人力需求分析
        try:
            from direct_calculation import direct_workforce_calculation
            import io
            import sys
            
            # 捕獲 direct_workforce_calculation 的輸出
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # 執行人力需求分析
            result = direct_workforce_calculation()
            
            # 恢復標準輸出
            sys.stdout = old_stdout
            
            # 獲取輸出內容
            analysis_output = captured_output.getvalue()
            
            if result and analysis_output:
                self.report_data['workforce_analysis'] = {
                    'output': analysis_output,
                    'result': result
                }
        except Exception as e:
            print(f"警告：無法執行人力需求分析：{e}")
            self.report_data['workforce_analysis'] = None
        
        # 收集基本統計
        if 'df' in self.report_data:
            df = self.report_data['df']
            self.report_data['stats'] = self._calculate_statistics(df)
    
    def _calculate_statistics(self, df):
        """計算關鍵統計數據"""
        total_tasks = len(df)
        assigned_tasks = len(df[df['assigned_worker'] != 'UNASSIGNED'])
        
        # 按員工類型統計
        senior_tasks = len(df[df['worker_type'] == 'SENIOR'])
        junior_tasks = len(df[df['worker_type'] == 'JUNIOR'])
        
        # 按難度統計
        difficulty_stats = df[df['assigned_worker'] != 'UNASSIGNED'].groupby('difficulty').agg({
            'measure_record_oid': 'count',
            'estimated_time': 'sum'
        }).round(1)
        
        # 按優先權統計
        priority_stats = df.groupby('priority').agg({
            'measure_record_oid': 'count'
        })
        assigned_priority_stats = df[df['assigned_worker'] != 'UNASSIGNED'].groupby('priority').agg({
            'measure_record_oid': 'count'
        })
        
        # 計算完成率
        priority_completion = {}
        for priority in priority_stats.index:
            total = priority_stats.loc[priority, 'measure_record_oid']
            assigned = assigned_priority_stats.loc[priority, 'measure_record_oid'] if priority in assigned_priority_stats.index else 0
            priority_completion[priority] = {
                'total': total,
                'assigned': assigned,
                'rate': (assigned / total * 100) if total > 0 else 0
            }
        
        # 按員工工作負載統計
        worker_stats = df[df['assigned_worker'] != 'UNASSIGNED'].groupby(['assigned_worker', 'worker_type']).agg({
            'measure_record_oid': 'count',
            'estimated_time': 'sum'
        }).round(1)
        
        return {
            'total_tasks': total_tasks,
            'assigned_tasks': assigned_tasks,
            'assignment_rate': (assigned_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'senior_tasks': senior_tasks,
            'junior_tasks': junior_tasks,
            'difficulty_stats': difficulty_stats,
            'priority_completion': priority_completion,
            'worker_stats': worker_stats,
            'target_met': assigned_tasks >= MINIMUM_WORK_TARGET,
            'target_gap': max(0, MINIMUM_WORK_TARGET - assigned_tasks)
        }
    
    def generate_report(self):
        """生成完整的MD格式報告"""
        self.collect_data()
        
        # 載入真實員工數量
        actual_senior_count, actual_junior_count = get_actual_employee_counts()
        
        # 生成報告標題
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        md = f"""# 工作分配管理系統 - 分析報告

**報告生成時間：** {timestamp}  
**系統版本：** v2.0 - 智能工作分配系統  
**分析範圍：** 完整工作流程分析報告  

---

## 執行概覽

### 系統配置
- **資深員工數量：** {actual_senior_count} 人
- **一般員工數量：** {actual_junior_count} 人
- **最低工作目標：** {MINIMUM_WORK_TARGET} 件
- **每人日工時：** 8 小時 (480 分鐘)

### 工作時間配置

#### 資深員工完成時間 (分鐘)
| 難度等級 | 完成時間 | 難度等級 | 完成時間 | 難度等級 | 完成時間 |
|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|"""

        # 添加資深員工時間配置表格
        senior_time_items = list(SENIOR_TIME.items())
        for i in range(0, len(senior_time_items), 3):
            row_items = senior_time_items[i:i+3]
            row = ""
            for diff, time in row_items:
                row += f"| 難度 {diff} | {time} 分鐘 "
            # 補齊空格
            while len(row_items) < 3:
                row += "| - | - "
                row_items.append(None)
            row += "|"
            md += f"""
{row}"""

        md += f"""

#### 一般員工完成時間 (分鐘)
| 難度等級 | 完成時間 | 難度等級 | 完成時間 | 難度等級 | 完成時間 |
|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|"""

        # 添加一般員工時間配置表格
        junior_time_items = list(JUNIOR_TIME.items())
        for i in range(0, len(junior_time_items), 3):
            row_items = junior_time_items[i:i+3]
            row = ""
            for diff, time in row_items:
                row += f"| 難度 {diff} | {time} 分鐘 "
            # 補齊空格
            while len(row_items) < 3:
                row += "| - | - "
                row_items.append(None)
            row += "|"
            md += f"""
{row}"""

        md += f"""

#### 時間配置說明
- **難度定義：** 1為最簡單（{SENIOR_TIME[1]}分鐘），{max(SENIOR_TIME.keys())}為最難（{SENIOR_TIME[max(SENIOR_TIME.keys())]}分鐘）
- **效率比例：** 一般員工完成時間為資深員工的1.5倍
- **低難度工作：** 難度6-9（適合一般員工優先處理）
- **高難度工作：** 難度1-5（需要資深員工處理）

### 關鍵績效指標 (KPI)

| 指標 | 數值 | 狀態 |
|------|------|------|"""

        # 添加統計數據
        if 'stats' in self.report_data:
            stats = self.report_data['stats']
            target_status = "未達標" if not stats.get('target_met', False) else "達標"
            target_icon = "❌" if not stats.get('target_met', False) else "✅"
            
            md += f"""
| 總工作數量 | {stats.get('total_tasks', 0)} 件 | - |
| 已分配工作 | {stats.get('assigned_tasks', 0)} 件 | - |
| 分配成功率 | {stats.get('assignment_rate', 0):.1f}% | {"需改善" if stats.get('assignment_rate', 0) < 80 else "良好"} |
| 目標達成狀況 | {stats.get('assigned_tasks', 0)}/{MINIMUM_WORK_TARGET} 件 | {target_status} |
| 目標缺口 | {stats.get('target_gap', 0)} 件 | {"需補強" if stats.get('target_gap', 0) > 0 else "達標"} |"""

        md += """

---

## 工作分配分析

### 員工類型分配統計

| 員工類型 | 分配數量 | 占比 |
|---------|--------:|-----:|"""

        # 添加員工分配統計
        if 'df' in self.report_data:
            df = self.report_data['df']
            assigned_df = df[df['assigned_worker'] != 'UNASSIGNED']
            
            senior_count = len(assigned_df[assigned_df['worker_type'] == 'SENIOR'])
            junior_count = len(assigned_df[assigned_df['worker_type'] == 'JUNIOR'])
            total_assigned = senior_count + junior_count
            
            if total_assigned > 0:
                senior_pct = (senior_count / total_assigned) * 100
                junior_pct = (junior_count / total_assigned) * 100
                
                md += f"""
| 資深員工 | {senior_count} 件 | {senior_pct:.1f}% |
| 一般員工 | {junior_count} 件 | {junior_pct:.1f}% |
| **總計** | **{total_assigned} 件** | **100.0%** |"""

        md += """

### 難度分佈分析

| 難度等級 | 工作數量 | 預估總時間 | 平均時間/件 |
|:--------:|--------:|----------:|----------:|"""

        # 添加難度分析
        if 'df' in self.report_data:
            df = self.report_data['df']
            assigned_df = df[df['assigned_worker'] != 'UNASSIGNED']
            
            difficulty_stats = assigned_df.groupby('difficulty').agg({
                'measure_record_oid': 'count',
                'estimated_time': 'sum'
            }).round(1)
            
            for difficulty in sorted(difficulty_stats.index):
                count = difficulty_stats.loc[difficulty, 'measure_record_oid']
                total_time = difficulty_stats.loc[difficulty, 'estimated_time']
                avg_time = total_time / count if count > 0 else 0
                md += f"""
| 難度 {difficulty} | {count} 件 | {total_time:.0f} 分鐘 | {avg_time:.1f} 分鐘 |"""

        md += """

### 優先權完成分析

| 優先權 | 總數量 | 已完成 | 完成率 | 狀態 |
|:------:|-------:|-------:|-------:|:----:|"""

        # 添加優先權分析
        if 'df' in self.report_data:
            df = self.report_data['df']
            
            priority_stats = df.groupby('priority').agg({
                'measure_record_oid': 'count'
            })
            assigned_priority_stats = df[df['assigned_worker'] != 'UNASSIGNED'].groupby('priority').agg({
                'measure_record_oid': 'count'
            })
            
            for priority in sorted(priority_stats.index):
                total = priority_stats.loc[priority, 'measure_record_oid']
                assigned = assigned_priority_stats.loc[priority, 'measure_record_oid'] if priority in assigned_priority_stats.index else 0
                completion_rate = (assigned / total * 100) if total > 0 else 0
                status = "完成" if completion_rate == 100 else "需關注" if completion_rate < 50 else "進行中"
                
                md += f"""
| 優先權 {priority} | {total} 件 | {assigned} 件 | {completion_rate:.1f}% | {status} |"""

        md += """

---

## 員工工作負載分析

### 資深員工工作分配

| 員工編號 | 工作數量 | 工作時間 | 利用率 |
|----------|--------:|--------:|-------:|"""

        # 添加資深員工分析
        if 'df' in self.report_data:
            df = self.report_data['df']
            senior_df = df[df['worker_type'] == 'SENIOR']
            
            if not senior_df.empty:
                senior_workload = senior_df.groupby('assigned_worker').agg({
                    'measure_record_oid': 'count',
                    'estimated_time': 'sum'
                }).round(1)
                
                for worker in sorted(senior_workload.index):
                    if worker != 'UNASSIGNED':
                        count = senior_workload.loc[worker, 'measure_record_oid']
                        time = senior_workload.loc[worker, 'estimated_time']
                        utilization = (time / 480 * 100) if time > 0 else 0
                        md += f"""
| {worker} | {count} 件 | {time:.0f} 分鐘 | {utilization:.1f}% |"""

        md += """

### 一般員工工作分配

| 員工編號 | 工作數量 | 工作時間 | 利用率 |
|----------|--------:|--------:|-------:|"""

        # 添加一般員工分析
        if 'df' in self.report_data:
            df = self.report_data['df']
            junior_df = df[df['worker_type'] == 'JUNIOR']
            
            if not junior_df.empty:
                junior_workload = junior_df.groupby('assigned_worker').agg({
                    'measure_record_oid': 'count',
                    'estimated_time': 'sum'
                }).round(1)
                
                for worker in sorted(junior_workload.index):
                    if worker != 'UNASSIGNED':
                        count = junior_workload.loc[worker, 'measure_record_oid']
                        time = junior_workload.loc[worker, 'estimated_time']
                        utilization = (time / 480 * 100) if time > 0 else 0
                        md += f"""
| {worker} | {count} 件 | {time:.0f} 分鐘 | {utilization:.1f}% |"""

        md += """

---

## 人力需求分析"""

        # 添加人力需求分析
        if 'workforce_analysis' in self.report_data and self.report_data['workforce_analysis']:
            analysis_data = self.report_data['workforce_analysis']
            
            if 'result' in analysis_data and analysis_data['result']:
                result = analysis_data['result']
                
                # 計算調整後的預期完成工作數量
                current_completed = self.report_data.get('stats', {}).get('assigned_tasks', 0)
                target_gap = self.report_data.get('stats', {}).get('target_gap', 0)
                expected_completed = current_completed + target_gap
                
                # 如果有額外的人力增加，可能會超過最低目標
                additional_capacity_estimate = 0
                if result.get('senior_add', 0) > 0:
                    # 資深員工每天可處理約16件工作（480分鐘/30分鐘平均）
                    additional_capacity_estimate += result.get('senior_add', 0) * 16
                if result.get('junior_add', 0) > 0:
                    # 一般員工每天可處理約12件工作（480分鐘/40分鐘平均）
                    additional_capacity_estimate += result.get('junior_add', 0) * 12
                
                # 保守估計，只計算達成目標所需的工作量
                final_expected = min(expected_completed, MINIMUM_WORK_TARGET + additional_capacity_estimate // 2)
                
                md += f"""

### 當前狀況分析
- **當前配置：** {actual_senior_count}資深 + {actual_junior_count}一般 = {actual_senior_count + actual_junior_count}人
- **已完成工作：** {current_completed} 件
- **目標要求：** {MINIMUM_WORK_TARGET} 件
- **缺口：** {target_gap} 件

### 推薦解決方案
- **方案類型：** {result.get('type', '未知')}
- **具體調整：**
  - 資深員工：{actual_senior_count} → {actual_senior_count + result.get('senior_add', 0)} 人 (+{result.get('senior_add', 0)}人)
  - 一般員工：{actual_junior_count} → {actual_junior_count + result.get('junior_add', 0)} 人 (+{result.get('junior_add', 0)}人)
- **預期效果：** {result.get('description', '無描述')}
- **預期完成工作：** {final_expected} 件（{'✅ ' if final_expected >= MINIMUM_WORK_TARGET else '⚠️ '}{'達成目標' if final_expected >= MINIMUM_WORK_TARGET else '仍未達標'}）
- **成本影響：** {result.get('cost_factor', 0):.1f} 個成本單位

### 實施建議
"""
                
                if result.get('senior_add', 0) > 0 or result.get('junior_add', 0) > 0:
                    total_increase = result.get('senior_add', 0) + result.get('junior_add', 0)
                    increase_percentage = (total_increase / (actual_senior_count + actual_junior_count)) * 100
                    
                    md += f"""- **人力增加幅度：** {increase_percentage:.1f}%
- **配置文件修改：**
  ```
  SENIOR_WORKERS = {actual_senior_count + result.get('senior_add', 0)}  # 原 {actual_senior_count}
  JUNIOR_WORKERS = {actual_junior_count + result.get('junior_add', 0)}  # 原 {actual_junior_count}
  ```
- **預期達成目標：** 300件最低工作要求
- **資源配置：** 成本增加相對最小，資源配置合理"""
                else:
                    md += f"""- **結論：** 現有人力配置已足夠達成目標
- **建議：** 優化工作分配策略，提升整體效率"""
        else:
            md += f"""

### 人力需求分析
- **狀態：** 分析數據不可用
- **建議：** 請檢查系統配置或重新執行分析"""

        return md

def generate_md_report(script_dir):
    """生成MD格式報告的主函數"""
    generator = MDReportGenerator(script_dir)
    
    # 生成報告內容
    md_content = generator.generate_report()
    
    # 保存MD文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"工作分配分析報告_{timestamp}.md"
    filepath = os.path.join(script_dir, "result", filename)
    
    # 確保result目錄存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filepath 