#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作分配管理系統 - API Server
============================

提供外部呼叫的RESTful API接口，支援：
1. 工作清單和技師清單的外部輸入
2. 自動工作分配計算
3. 結果輸出（包含原始資料 + 分配結果）

同時保留原本的CSV讀取功能供本地測試使用。
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback

# 添加父目錄到Python路徑（回到專案根目錄）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 導入系統模組
from config_params import *
from strategy_manager import StrategyManager, get_strategy_manager
from employee_manager import EmployeeManager
from path_utils import get_data_file_path
from update_assignment_results import assign_workers_to_tasks

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立Flask應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求

def create_date_result_directory():
    """創建按日期分組的結果目錄並返回時間戳"""
    now = datetime.now()
    today = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    date_result_dir = os.path.join(script_dir, "result", today)
    os.makedirs(date_result_dir, exist_ok=True)
    return date_result_dir, timestamp

def generate_reports_for_api(work_data, employee_data, result_df, senior_workloads, junior_workloads, date_result_dir, timestamp):
    """生成完整的分析報告（重用main_manager邏輯）"""
    try:
        # 導入所需模組
        import detailed_global_statistics
        import final_recommendation_report  
        import direct_calculation
        from md_report_generator import generate_md_report
        
        # 切換工作目錄以使用現有的報告生成邏輯
        original_cwd = os.getcwd()
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(script_dir)
        
        try:
            # 首先保存結果到項目根目錄，讓其他模組可以讀取
            temp_result_file = os.path.join(script_dir, 'result', 'result_with_assignments.csv')
            os.makedirs(os.path.dirname(temp_result_file), exist_ok=True)
            result_df.to_csv(temp_result_file, index=False, encoding='utf-8')
            
            # 1. 生成詳細統計報告（直接調用main函數）
            detailed_global_statistics.main(timestamp)
            
            # 移動生成的文件到日期目錄
            source_detailed_file = os.path.join(script_dir, 'result', f'detailed_statistics_report_{timestamp}.txt')
            if os.path.exists(source_detailed_file):
                dest_detailed_file = os.path.join(date_result_dir, f'detailed_statistics_report_{timestamp}.txt')
                import shutil
                shutil.move(source_detailed_file, dest_detailed_file)
                logger.info(f"詳細統計報告已保存到: {dest_detailed_file}")
            
            # 2. 生成人力需求分析（直接調用函數並指定時間戳）
            direct_calculation.direct_workforce_calculation(timestamp)
            
            # 移動生成的文件到日期目錄
            source_workforce_file = os.path.join(script_dir, 'result', f'workforce_requirements_analysis_{timestamp}.txt')
            if os.path.exists(source_workforce_file):
                dest_workforce_file = os.path.join(date_result_dir, f'workforce_requirements_analysis_{timestamp}.txt')
                import shutil
                shutil.move(source_workforce_file, dest_workforce_file)
                logger.info(f"人力需求分析報告已保存到: {dest_workforce_file}")
            
            # 3. 生成MD格式報告
            md_file_path = generate_md_report(script_dir)
            if md_file_path:
                # 移動MD報告到日期目錄，使用統一時間戳重命名
                import shutil
                dest_md_file = os.path.join(date_result_dir, f"工作分配分析報告_{timestamp}.md")
                shutil.move(md_file_path, dest_md_file)
                logger.info(f"MD格式報告已保存到: {dest_md_file}")
            
            # 清理臨時文件
            if os.path.exists(temp_result_file):
                os.remove(temp_result_file)
            
        finally:
            os.chdir(original_cwd)
        
        return True
        
    except Exception as e:
        logger.error(f"報告生成失敗: {str(e)}")
        logger.error(traceback.format_exc())
        return False

class WorkAssignmentAPI:
    """工作分配API處理器"""
    
    def __init__(self):
        """初始化API處理器"""
        self.required_work_fields = [
            'measure_record_oid', 'upload_end_time', 'promise_time', 'task_status',
            'task_status_name', 'institution_id', 'data_effective_rate', 'num_af',
            'num_pvc', 'num_sveb', 'delay_days', 'is_vip', 'is_top_job',
            'is_simple_work', 'priority', 'actual_record_days', 'source_file',
            'difficulty', 'x_value'
        ]
        
        self.required_employee_fields = ['id', 'type']
        
        self.output_fields = ['assigned_worker', 'worker_type', 'estimated_time']
    
    def validate_work_data(self, work_data):
        """驗證工作清單資料格式（支持簡化格式）"""
        if not isinstance(work_data, list) or len(work_data) == 0:
            return False, "Work list must be a non-empty array"
        
        for i, work in enumerate(work_data):
            if not isinstance(work, dict):
                return False, f"Work item {i+1} must be an object"
            
            # 檢查核心必要欄位（簡化驗證）
            core_fields = ['measure_record_oid', 'priority', 'difficulty']
            missing_fields = []
            for field in core_fields:
                if field not in work:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Work item {i+1} is missing core fields: {', '.join(missing_fields)}"
            
            # 驗證資料型別
            try:
                # 確保數值型別欄位正確
                numeric_fields = ['priority', 'difficulty']
                for field in numeric_fields:
                    if field in work and work[field] is not None:
                        work[field] = float(work[field])
                        
            except (ValueError, TypeError) as e:
                return False, f"Work item {i+1} data type error: {str(e)}"
        
        return True, "Work list data format is correct"
    
    def validate_employee_data(self, employee_data):
        """驗證技師清單資料格式"""
        if not isinstance(employee_data, list) or len(employee_data) == 0:
            return False, "Employee list must be a non-empty array"
        
        senior_count = 0
        junior_count = 0
        
        for i, employee in enumerate(employee_data):
            if not isinstance(employee, dict):
                return False, f"Employee item {i+1} must be an object"
            
            # 檢查必要欄位
            missing_fields = []
            for field in self.required_employee_fields:
                if field not in employee:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Employee item {i+1} is missing fields: {', '.join(missing_fields)}"
            
            # 驗證技師類型
            emp_type = employee.get('type', '').upper()
            if emp_type not in ['SENIOR', 'JUNIOR']:
                return False, f"Employee item {i+1} type must be SENIOR or JUNIOR"
            
            # 統計技師數量
            if emp_type == 'SENIOR':
                senior_count += 1
            else:
                junior_count += 1
        
        if senior_count == 0 and junior_count == 0:
            return False, "At least one employee is required"
        
        return True, f"Employee list data format is correct (Senior employees: {senior_count}, Junior employees: {junior_count})"
    
    def process_assignment(self, work_data, employee_data, external_senior_count=None, external_junior_count=None, generate_reports=False):
        """處理工作分配邏輯
        
        Args:
            generate_reports: 是否生成完整報告（默認False以保持API響應速度）
        """
        try:
            # 轉換為DataFrame
            work_df = pd.DataFrame(work_data)
            
            logger.info(f"開始工作分配 - 工作數量: {len(work_df)}")
            logger.info(f"技師數量: {len(employee_data)}人")
            
            # 使用重構後的分配函數
            result_df, senior_workloads, junior_workloads = assign_workers_to_tasks(
                work_data=work_df, 
                employee_data=employee_data
            )
            
            # 統計結果
            assigned_count = len(result_df[result_df['assigned_worker'] != 'UNASSIGNED'])
            unassigned_count = len(result_df[result_df['assigned_worker'] == 'UNASSIGNED'])
            
            logger.info(f"工作分配完成 - 已分配: {assigned_count}件, 未分配: {unassigned_count}件")
            
            # 確保所有欄位都存在
            if 'assigned_worker' not in result_df.columns:
                result_df['assigned_worker'] = 'UNASSIGNED'
            if 'worker_type' not in result_df.columns:
                result_df['worker_type'] = 'UNASSIGNED'
            if 'estimated_time' not in result_df.columns:
                result_df['estimated_time'] = 0
            
            # 指定欄位順序
            desired_order = [
                "measure_record_oid", "upload_end_time", "promise_time", "task_status", "task_status_name",
                "institution_id", "data_effective_rate", "num_af", "num_pvc", "num_sveb", "delay_days",
                "is_vip", "is_top_job", "is_simple_work", "priority", "actual_record_days", "source_file",
                "difficulty", "x_value", "worker_type", "assigned_worker", "estimated_time"
            ]
            
            # 只保留DataFrame中實際存在的欄位，並按指定順序排列
            ordered_cols = [col for col in desired_order if col in result_df.columns]
            # 如果有其他欄位不在desired_order中，也加到最後
            extra_cols = [col for col in result_df.columns if col not in ordered_cols]
            final_cols = ordered_cols + extra_cols
            
            # 創建按日期分組的結果目錄並獲取時間戳
            date_result_dir, timestamp = create_date_result_directory()
            
            # 保存分配結果CSV（添加時間戳）
            result_file = os.path.join(date_result_dir, f'result_with_assignments_{timestamp}.csv')
            result_df[final_cols].to_csv(result_file, index=False, encoding='utf-8')
            logger.info(f"分配結果已保存到: {result_file}")
            
            # 保存統計摘要（添加時間戳）
            summary_file = os.path.join(date_result_dir, f'assignment_summary_{timestamp}.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("工作分配統計摘要\n")
                f.write("="*50 + "\n")
                f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"時間戳: {timestamp}\n\n")
                f.write(f"基本統計:\n")
                f.write(f"  總工作數量: {len(work_data)} 件\n")
                f.write(f"  已分配工作: {assigned_count} 件\n")
                f.write(f"  分配成功率: {(assigned_count / len(work_data)) * 100:.1f}%\n\n")
                f.write(f"技師工作負載:\n")
                f.write(f"  資深技師: {senior_workloads}\n")
                f.write(f"  一般技師: {junior_workloads}\n")
            logger.info(f"統計摘要已保存到: {summary_file}")
            
            # 如果需要生成完整報告
            if generate_reports:
                generate_reports_for_api(work_df, employee_data, result_df, senior_workloads, junior_workloads, date_result_dir, timestamp)
            
            # 轉換回原始格式（按指定順序）
            result_data = result_df[final_cols].to_dict('records')
            
            # 獲取策略管理器的統計摘要
            strategy_manager = get_strategy_manager(work_data=work_df, employee_data=employee_data)
            strategy_summary = strategy_manager.get_strategy_summary()
            
            return {
                'success': True,
                'data': result_data,
                'statistics': {
                    'total_tasks': len(work_data),
                    'assigned_tasks': assigned_count,
                    'unassigned_tasks': unassigned_count,
                    'assignment_rate': round((assigned_count / len(work_data)) * 100, 2),
                    'senior_workers': strategy_summary['parameters']['senior_workers'],
                    'junior_workers': strategy_summary['parameters']['junior_workers'],
                    'senior_utilization': round(strategy_summary['senior_utilization'] * 100, 2),
                    'junior_utilization': round(strategy_summary['junior_utilization'] * 100, 2),
                    'overall_utilization': round(strategy_summary['overall_utilization'] * 100, 2),
                    'leftover_senior': strategy_summary['leftover_senior'],
                    'leftover_junior': strategy_summary['leftover_junior'],
                    'meets_minimum_target': strategy_summary['meets_minimum'],
                    'minimum_target': strategy_summary['parameters']['minimum_work_target'],
                    'senior_workloads': senior_workloads,
                    'junior_workloads': junior_workloads,
                    'config_source': {
                        'senior_workers_source': 'external_api' if external_senior_count is not None else 'employee_list',
                        'junior_workers_source': 'external_api' if external_junior_count is not None else 'employee_list'
                    }
                },
                'result_directory': date_result_dir,
                'timestamp': timestamp,
                'result_files': {
                    'assignment_result': f'result_with_assignments_{timestamp}.csv',
                    'summary': f'assignment_summary_{timestamp}.txt'
                }
            }
            
        except Exception as e:
            logger.error(f"Work assignment processing failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f"Work assignment processing failed: {str(e)}"
            }

# 建立API處理器實例
api_handler = WorkAssignmentAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Assign Manager API'
    })

@app.route('/api/assign', methods=['POST'])
def assign_work():
    """
    工作分配API端點（整合版本）
    
    支持兩種參數格式：
    1. 完整格式：包含所有必要欄位
    2. 簡化格式：只需要核心欄位 (measure_record_oid, priority, difficulty)
    
    請求格式:
    {
        "work_list": [
            {
                "measure_record_oid": "123",
                "priority": 1,
                "difficulty": 3,
                ... 其他欄位（可選）
            }
        ],
        "employee_list": [
            {
                "id": "S001",
                "name": "張三",
                "type": "SENIOR"
            }
        ],
        "generate_reports": true/false  // 可選，是否生成完整報告（默認false）
    }
    
    回應格式:
    {
        "success": true,
        "data": [ ... 原始工作資料 + assigned_worker, worker_type, estimated_time ],
        "statistics": { ... 統計資訊 },
        "result_directory": "結果保存目錄路徑",
        "message": "工作分配完成"
    }
    """
    try:
        # 取得請求資料
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'Request data cannot be empty'
            }), 400
        
        # 提取工作清單和技師清單（支援多種參數格式）
        work_list = request_data.get('work_list', request_data.get('work_data', []))
        employee_list = request_data.get('employee_list', request_data.get('employee_data', []))
        
        # 提取外部技師數量參數 (可選)
        external_senior_count = request_data.get('senior_workers_count')
        external_junior_count = request_data.get('junior_workers_count')
        
        # 是否生成完整報告
        generate_reports = request_data.get('generate_reports', False)
        
        # 驗證工作清單（使用簡化驗證）
        valid, message = api_handler.validate_work_data(work_list)
        if not valid:
            return jsonify({
                'success': False,
                'error': f'Work list format error: {message}'
            }), 400
        
        # 驗證技師清單
        valid, message = api_handler.validate_employee_data(employee_list)
        if not valid:
            return jsonify({
                'success': False,
                'error': f'Employee list format error: {message}'
            }), 400
        
        logger.info(f"收到工作分配請求 - 工作數量: {len(work_list)}, 技師數量: {len(employee_list)}, 生成報告: {generate_reports}")
        
        # 執行工作分配
        result = api_handler.process_assignment(
            work_list, employee_list, 
            external_senior_count, external_junior_count,
            generate_reports
        )
        
        if result['success']:
            response = {
                'success': True,
                'data': result['data'],
                'statistics': result['statistics'],
                'result_directory': result.get('result_directory', ''),
                'result_files': result.get('result_files', {}),
                'file_timestamp': result.get('timestamp', ''),
                'message': 'Work assignment completed',
                'timestamp': datetime.now().isoformat()
            }
            
            if generate_reports:
                response['message'] += ' with full reports generated'
                # 如果生成了完整報告，添加報告文件信息
                file_timestamp = result.get('timestamp', '')
                if file_timestamp:
                    response['result_files'].update({
                        'detailed_statistics': f'detailed_statistics_report_{file_timestamp}.txt',
                        'workforce_analysis': f'workforce_requirements_analysis_{file_timestamp}.txt',
                        'md_report': f'工作分配分析報告_{file_timestamp}.md'
                    })
            
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"API request processing failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'System error: {str(e)}'
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """取得系統配置資訊"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'minimum_work_target': MINIMUM_WORK_TARGET,
                'work_hours_per_day': WORK_HOURS_PER_DAY,
                'senior_time': SENIOR_TIME,
                'junior_time': JUNIOR_TIME,
                'required_work_fields': api_handler.required_work_fields,
                'required_employee_fields': api_handler.required_employee_fields,
                'output_fields': api_handler.output_fields
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get config: {str(e)}'
        }), 500

@app.route('/api/test/csv', methods=['POST'])
def test_with_csv():
    """
    使用CSV檔案進行測試的端點（保留原本功能）
    
    請求格式:
    {
        "work_file": "result.csv",  // 可選，預設使用result.csv
        "employee_file": "employee_list.csv",  // 可選，預設使用employee_list.csv
        "generate_reports": true/false  // 可選，是否生成完整報告（默認false）
    }
    """
    try:
        request_data = request.get_json() or {}
        
        # 取得檔案路徑
        work_file = request_data.get('work_file', 'result.csv')
        employee_file = request_data.get('employee_file', 'employee_list.csv')
        generate_reports = request_data.get('generate_reports', False)
        
        # 讀取工作清單CSV
        work_file_path = get_data_file_path(work_file)
        if not os.path.exists(work_file_path):
            return jsonify({
                'success': False,
                'error': f'Work list file not found: {work_file_path}'
            }), 400
        
        work_df = pd.read_csv(work_file_path)
        work_list = work_df.to_dict('records')
        
        # 讀取技師清單CSV
        employee_manager = EmployeeManager()
        try:
            employee_manager.load_employee_list_from_csv()
            employee_dict = employee_manager.get_employee_dict()
            
            # 轉換為API格式
            employee_list = []
            for worker_id in employee_dict['senior_workers']:
                employee_list.append({
                    'id': worker_id,
                    'type': 'SENIOR'
                })
            
            for worker_id in employee_dict['junior_workers']:
                employee_list.append({
                    'id': worker_id,
                    'type': 'JUNIOR'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to read employee list: {str(e)}'
            }), 400
        
        logger.info(f"使用CSV檔案測試 - 工作檔案: {work_file}, 技師檔案: {employee_file}, 生成報告: {generate_reports}")
        
        # 執行工作分配
        result = api_handler.process_assignment(work_list, employee_list, generate_reports=generate_reports)
        
        if result['success']:
            response = {
                'success': True,
                'data': result['data'],
                'statistics': result['statistics'],
                'result_directory': result.get('result_directory', ''),
                'result_files': result.get('result_files', {}),
                'file_timestamp': result.get('timestamp', ''),
                'message': 'CSV test completed successfully',
                'timestamp': datetime.now().isoformat(),
                'files_used': {
                    'work_file': work_file,
                    'employee_file': employee_file
                }
            }
            
            if generate_reports:
                response['message'] += ' with full reports generated'
                # 如果生成了完整報告，添加報告文件信息
                file_timestamp = result.get('timestamp', '')
                if file_timestamp:
                    response['result_files'].update({
                        'detailed_statistics': f'detailed_statistics_report_{file_timestamp}.txt',
                        'workforce_analysis': f'workforce_requirements_analysis_{file_timestamp}.txt',
                        'md_report': f'工作分配分析報告_{file_timestamp}.md'
                    })
            
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"CSV test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'CSV test failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 設定伺服器配置
    PORT = 7777
    HOST = '0.0.0.0'
    DEBUG = True
    
    print(f"🚀 工作分配管理系統API伺服器啟動中...")
    print(f"📡 服務地址: http://{HOST}:{PORT}")
    print(f"📋 健康檢查: http://{HOST}:{PORT}/health")
    print(f"🔧 API文檔: 請參考 API_文檔.md")
    print(f"🛠️ 調試模式: {'開啟' if DEBUG else '關閉'}")
    print("="*50)
    
    # 啟動Flask應用
    app.run(host=HOST, port=PORT, debug=DEBUG) 