#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作分配管理系統 - 主要管理腳本
==================================

整合所有工作調度和分配功能的主要管理程式。

功能包括：
1. 最佳策略分析
2. 工作分配給具體技師 (支援JSON格式技師輸入)
3. 生成詳細統計報告
4. 生成最終建議報告
5. 自動人力需求分析（當未達標時）

使用方法：
    python main_manager.py [選項]

選項：
    --analysis-only    只執行分析，不進行分配
    --assign-only      只執行分配，跳過分析
    --report-only      只生成報告
    --workforce-only   只執行人力需求分析
    --full             執行完整流程 (預設)
    --json-workers     使用JSON格式技師輸入 (需要--assigned-worker和--worker-type參數)
    --assigned-worker  JSON格式的技師分配 (配合--json-workers使用)
    --worker-type      JSON格式的技師類型 (配合--json-workers使用)
"""

import sys
import os
import argparse
from datetime import datetime
import pandas as pd
import json

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入所有模組
from config_params import *
import optimal_strategy_analysis
import final_recommendation_report
import update_assignment_results
import detailed_global_statistics
import traceback
import glob

# 導入人力需求計算模組
# from workforce_api import calculate_required_workforce, get_current_status  # 不再使用遞增式計算
from md_report_generator import generate_md_report
from direct_calculation import direct_workforce_calculation

# 導入技師管理模組
from employee_manager import print_actual_employee_config, get_actual_employee_counts
from update_assignment_results import assign_workers_with_json_input
from path_utils import get_data_file_path

class WorkAssignmentManager:
    """工作分配管理器"""
    
    def __init__(self, data_file="result.csv", use_json_workers=False, 
                 assigned_worker_json=None, worker_type_json=None):
        """初始化管理器"""
        # 智能路徑處理：確保相對路徑正確解析
        if not os.path.isabs(data_file):
            # 獲取腳本所在目錄
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # 構建數據文件的絕對路徑
            self.data_file = os.path.join(script_dir, data_file)
        else:
            self.data_file = data_file
            
        self.start_time = datetime.now()
        self.use_json_workers = use_json_workers
        self.assigned_worker_json = assigned_worker_json
        self.worker_type_json = worker_type_json
        
        # 檢查資料檔案是否存在
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"找不到資料檔案: {self.data_file}")
        
        print(f"📂 工作目錄: {os.getcwd()}")
        print(f"📂 腳本目錄: {os.path.dirname(os.path.abspath(__file__))}")
        print(f"📂 數據文件: {self.data_file}")
        
        print("🎯 工作分配管理系統啟動")
        print("=" * 50)
        print(f"📅 執行時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 資料檔案: {self.data_file}")
        # 載入實際技師數量顯示
        print_actual_employee_config()
        print(f"🎯 最低目標: {MINIMUM_WORK_TARGET} 件工作")
        
        if self.use_json_workers:
            print(f"🔧 使用模式: JSON格式技師輸入")
            if self.assigned_worker_json:
                print(f"   assigned_worker參數: {len(self.assigned_worker_json)} 字符")
            if self.worker_type_json:
                print(f"   worker_type參數: {len(self.worker_type_json)} 字符")
        else:
            print(f"🔧 使用模式: 標準技師配置")
        
        print("=" * 50)
    

    def run_optimization(self):
        """執行最佳策略分析"""
        print("\n🔍 第1步: 執行最佳策略分析...")
        
        try:
            # 執行最佳策略分析
            optimal_strategy_analysis.main()
            print("✅ 最佳策略分析完成")
        except Exception as e:
            print(f"❌ 最佳策略分析失敗: {e}")
            return False
        
        return True
    
    def run_assignment(self):
        """執行工作分配"""
        if self.use_json_workers:
            print("\n👥 第2步: 使用JSON格式執行工作分配...")
            return self.run_json_assignment()
        else:
            print("\n👥 第2步: 執行工作分配給具體技師...")
            
            try:
                # 執行工作分配（使用統一策略管理器）
                update_assignment_results.main()
                print("✅ 工作分配完成")
            except Exception as e:
                print(f"❌ 工作分配失敗: {e}")
                return False
            
            return True
    
    def run_json_assignment(self):
        """使用JSON格式執行工作分配"""
        try:
            # 執行JSON格式的工作分配
            result_df, senior_workload, junior_workload, assignment_json = assign_workers_with_json_input(
                self.assigned_worker_json, self.worker_type_json
            )
            
            # 保存分配結果到原來的CSV文件
            output_file = get_data_file_path('result.csv')
            result_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"📄 分配結果已保存到: {output_file}")
            
            print("✅ JSON格式工作分配完成")
            return True
            
        except Exception as e:
            print(f"❌ JSON格式工作分配失敗: {e}")
            traceback.print_exc()
            return False
    
    def generate_reports(self):
        """生成報告"""
        print("\n📋 第3步: 生成詳細報告...")
        
        try:
            # 生成詳細統計報告
            detailed_global_statistics.main()
            print("✅ 詳細統計報告生成完成")
            
            # 生成最終建議報告
            final_recommendation_report.main()
            print("✅ 最終建議報告生成完成")
            
        except Exception as e:
            print(f"❌ 報告生成失敗: {e}")
            return False
        
        return True
    
    def analyze_workforce_requirements(self):
        """分析人力需求（當未達標時）"""
        print("\n🔧 第4步: 分析人力需求...")
        
        try:
            print("🎯 執行直接人力需求計算分析...")
            result = direct_workforce_calculation()
            return True
        except Exception as e:
            print(f"❌ 人力需求分析失敗: {e}")
            traceback.print_exc()
            return False
    
    def generate_md_report(self):
        """生成MD格式綜合分析報告"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            md_file_path = generate_md_report(script_dir)
            return md_file_path
        except Exception as e:
            raise Exception(f"MD報告生成失敗: {e}")
    
    def run_full_workflow(self):
        """執行完整的工作分配流程"""
        success_count = 0
        total_steps = 5  # 增加MD報告生成步驟
        
        print("🚀 開始執行完整工作分配流程...\n")
        
        # 第1步：最佳策略分析
        print("🔍 第1步: 執行最佳策略分析...")
        try:
            result = self.run_optimization()
            if result:
                success_count += 1
                print("✅ 最佳策略分析完成\n")
            else:
                print("❌ 最佳策略分析失敗\n")
        except Exception as e:
            print(f"❌ 最佳策略分析失敗: {e}\n")
        
        # 第2步：具體工作分配
        print("👥 第2步: 執行工作分配給具體技師...")
        try:
            result = self.run_assignment()
            if result:
                success_count += 1
                print("✅ 工作分配完成\n")
            else:
                print("❌ 工作分配失敗\n")
        except Exception as e:
            print(f"❌ 工作分配失敗: {e}\n")
        
        # 第3步：生成詳細報告
        print("📋 第3步: 生成詳細報告...")
        try:
            result = self.generate_reports()
            if result:
                success_count += 1
                print("✅ 詳細統計報告生成完成\n")
            else:
                print("❌ 報告生成失敗\n")
        except Exception as e:
            print(f"❌ 報告生成失敗: {e}\n")
        
        # 第4步：人力需求分析
        print("🔧 第4步: 分析人力需求...")
        try:
            result = self.analyze_workforce_requirements()
            if result:
                success_count += 1
                print("✅ 人力需求分析完成\n")
            else:
                print("❌ 人力需求分析失敗\n")
        except Exception as e:
            print(f"❌ 人力需求分析失敗: {e}\n")
        
        # 第5步：生成MD格式綜合報告
        print("📄 第5步: 生成MD格式綜合分析報告...")
        try:
            md_file = self.generate_md_report()
            success_count += 1
            print(f"✅ MD格式報告已生成: {os.path.basename(md_file)}\n")
        except Exception as e:
            print(f"❌ MD報告生成失敗: {e}\n")
        
        # 顯示執行摘要
        self.show_summary(success_count, total_steps)
    
    def show_summary(self, success_count, total_steps):
        """顯示執行摘要"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 執行摘要")
        print("=" * 60)
        print(f"⏱️ 執行時間: {duration.total_seconds():.1f} 秒")
        print(f"✅ 完成步驟: {success_count}/{total_steps}")
        
        if success_count == total_steps:
            print("🎉 所有步驟執行成功！")
            
            # 顯示生成的檔案
            print(f"\n📁 生成的檔案:")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_files = [
                "result/result_with_assignments.csv",
                "result/assignment_summary.txt",
                "result/detailed_statistics_report.txt",
                "result/workforce_requirements_analysis.txt"
            ]
            
            # 檢查固定文件
            for filename in output_files:
                full_path = os.path.join(script_dir, filename)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   📄 {filename} ({file_size:,} bytes)")
                else:
                    print(f"   ⚠️ {filename} (未生成)")
            
            # 檢查MD報告文件（動態文件名）
            result_dir = os.path.join(script_dir, "result")
            if os.path.exists(result_dir):
                import glob
                md_files = glob.glob(os.path.join(result_dir, "工作分配分析報告_*.md"))
                if md_files:
                    # 獲取最新的MD報告
                    latest_md = max(md_files, key=os.path.getctime)
                    file_size = os.path.getsize(latest_md)
                    filename = os.path.basename(latest_md)
                    print(f"   📄 result/{filename} ({file_size:,} bytes)")
                else:
                    print(f"   ⚠️ MD格式分析報告 (未生成)")
            
            # 顯示關鍵統計
            try:
                result_file = os.path.join(script_dir, "result/result_with_assignments.csv")
                if os.path.exists(result_file):
                    df = pd.read_csv(result_file)
                    total_tasks = len(df)
                    assigned_tasks = len(df[df['assigned_worker'] != 'UNASSIGNED'])
                    assignment_rate = (assigned_tasks / total_tasks) * 100
                    
                    print(f"\n🎯 關鍵結果:")
                    print(f"   總工作數量: {total_tasks:,} 件")
                    print(f"   已分配工作: {assigned_tasks:,} 件")
                    print(f"   分配成功率: {assignment_rate:.1f}%")
                    
                    # 檢查是否達標
                    target_met = assigned_tasks >= MINIMUM_WORK_TARGET
                    print(f"   目標達成: {'✅ 是' if target_met else '❌ 否'}")
                    
                    if not target_met:
                        gap = MINIMUM_WORK_TARGET - assigned_tasks
                        print(f"   目標缺口: {gap} 件")
                        
                        # 直接顯示人力需求分析內容
                        workforce_analysis_file = os.path.join(script_dir, "result/workforce_requirements_analysis.txt")
                        if os.path.exists(workforce_analysis_file):
                            print(f"\n" + "=" * 60)
                            print("🔧 人力需求分析結果")
                            print("=" * 60)
                            
                            try:
                                with open(workforce_analysis_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # 只顯示關鍵部分，跳過標題
                                    lines = content.split('\n')
                                    in_content = False
                                    for line in lines:
                                        if line.startswith('當前配置分析:'):
                                            in_content = True
                                        if in_content:
                                            # 美化輸出格式
                                            if line.startswith('-----'):
                                                continue
                                            elif line.startswith('當前配置分析:'):
                                                print("📊 當前配置分析:")
                                            elif line.startswith('推薦配置:'):
                                                print("\n💡 推薦配置:")
                                            elif line.startswith('實施建議:'):
                                                print("\n🛠️ 實施建議:")
                                            elif line.startswith('效益分析:'):
                                                print("\n📈 效益分析:")
                                            elif line.strip() and not line.startswith('='):
                                                print(f"   {line}")
                                
                                print("=" * 60)
                                
                            except Exception as e:
                                print(f"   ⚠️ 讀取人力需求分析報告失敗: {e}")
                                print(f"   📋 詳細分析請查看: result/workforce_requirements_analysis.txt")
                        else:
                            print(f"   📋 詳細人力需求分析請查看: result/workforce_requirements_analysis.txt")
                    
            except Exception as e:
                print(f"   ⚠️ 無法讀取結果統計: {e}")
        else:
            print("❌ 部分步驟執行失敗，請檢查錯誤訊息")
        
        print("=" * 60)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="工作分配管理系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
    python main_manager.py                # 執行完整流程
    python main_manager.py --analysis-only   # 只執行最佳策略分析
    python main_manager.py --assign-only     # 只執行工作分配
    python main_manager.py --report-only     # 只生成報告
    python main_manager.py --workforce-only  # 只執行人力需求分析
    python main_manager.py --json-workers --assigned-worker '{"worker1": "John", "worker2": "Jane"}' --worker-type '{"worker1": "Senior", "worker2": "Junior"}'
        """
    )
    
    parser.add_argument(
        '--analysis-only',
        action='store_true',
        help='只執行最佳策略分析步驟'
    )
    
    parser.add_argument(
        '--assign-only',
        action='store_true',
        help='只執行分配步驟'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='只生成報告'
    )
    
    parser.add_argument(
        '--workforce-only',
        action='store_true',
        help='只執行人力需求分析'
    )
    
    parser.add_argument(
        '--data-file',
        default='result.csv',
        help='指定資料檔案路徑 (預設: result.csv)'
    )
    
    parser.add_argument(
        '--json-workers',
        action='store_true',
        help='使用JSON格式技師輸入'
    )
    
    parser.add_argument(
        '--assigned-worker',
        help='JSON格式的技師分配'
    )
    
    parser.add_argument(
        '--worker-type',
        help='JSON格式的技師類型'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化管理器
        manager = WorkAssignmentManager(
            args.data_file,
            args.json_workers,
            args.assigned_worker,
            args.worker_type
        )
        
        # 根據參數執行相應功能
        if args.analysis_only:
            # 只執行最佳策略分析
            success = manager.run_optimization()
        elif args.assign_only:
            success = manager.run_assignment()
        elif args.report_only:
            success = manager.generate_reports()
        elif args.workforce_only:
            success = manager.analyze_workforce_requirements()
        else:
            # 預設執行完整流程
            success = manager.run_full_workflow()
        
        # 設置退出代碼
        sys.exit(0 if success else 1)
        
    except FileNotFoundError as e:
        print(f"❌ 檔案錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 