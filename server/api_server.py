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
        """驗證工作清單資料格式"""
        if not isinstance(work_data, list) or len(work_data) == 0:
            return False, "Work list must be a non-empty array"
        
        for i, work in enumerate(work_data):
            if not isinstance(work, dict):
                return False, f"Work item {i+1} must be an object"
            
            # 檢查必要欄位
            missing_fields = []
            for field in self.required_work_fields:
                if field not in work:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Work item {i+1} is missing fields: {', '.join(missing_fields)}"
            
            # 驗證資料型別
            try:
                # 確保數值型別欄位正確
                numeric_fields = ['data_effective_rate', 'num_af', 'num_pvc', 'num_sveb', 
                                'delay_days', 'priority', 'actual_record_days', 'difficulty', 'x_value']
                for field in numeric_fields:
                    if field in work and work[field] is not None:
                        work[field] = float(work[field])
                
                # 確保布林型別欄位正確
                boolean_fields = ['is_vip', 'is_top_job', 'is_simple_work']
                for field in boolean_fields:
                    if field in work and work[field] is not None:
                        work[field] = bool(work[field])
                        
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
    
    def process_assignment(self, work_data, employee_data, external_senior_count=None, external_junior_count=None):
        """處理工作分配邏輯
        
        使用重構後的統一介面，通過 StrategyManager 處理所有計算邏輯。
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
        'service': '工作分配管理系統API'
    })

@app.route('/api/assign', methods=['POST'])
def assign_work():
    """
    工作分配API端點
    
    請求格式:
    {
        "work_list": [
            {
                "measure_record_oid": "123",
                "upload_end_time": "2025-01-01",
                "promise_time": "2025-01-02",
                ... 其他工作欄位
            }
        ],
        "employee_list": [
            {
                "id": "S001",
                "name": "張三",
                "type": "SENIOR"
            }
        ]
    }
    
    回應格式:
    {
        "success": true,
        "data": [ ... 原始工作資料 + assigned_worker, worker_type, estimated_time ],
        "statistics": { ... 統計資訊 },
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
        
        # 提取工作清單和技師清單 (支援兩種參數格式)
        work_list = request_data.get('work_list', request_data.get('work_data', []))
        employee_list = request_data.get('employee_list', request_data.get('employee_data', []))
        
        # 提取外部技師數量參數 (可選)
        external_senior_count = request_data.get('senior_workers_count')
        external_junior_count = request_data.get('junior_workers_count')
        
        # 驗證工作清單
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
        
        logger.info(f"收到工作分配請求 - 工作數量: {len(work_list)}, 技師數量: {len(employee_list)}")
        
        # 執行工作分配 (支持外部技師數量參數)
        result = api_handler.process_assignment(work_list, employee_list, external_senior_count, external_junior_count)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'statistics': result['statistics'],
                'message': 'Work assignment completed',
                'timestamp': datetime.now().isoformat()
            })
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

@app.route('/process_assignment', methods=['POST'])
def process_assignment_legacy():
    """
    工作分配API端點 (統一參數格式)
    使用 work_list 和 employee_list 參數格式 (與其他API一致)
    只檢查必要欄位：priority, difficulty 和 id, type
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'Request data cannot be empty'
            }), 400
        
        # 提取工作清單和技師清單 (統一格式)
        work_list = request_data.get('work_list', [])
        employee_list = request_data.get('employee_list', [])
        
        # 向前兼容：如果使用舊的參數名稱，自動轉換
        if not work_list and 'work_data' in request_data:
            work_list = request_data.get('work_data', [])
            logger.warning("Used deprecated 'work_data' parameter, please use 'work_list' instead")
            
        if not employee_list and 'employee_data' in request_data:
            employee_list = request_data.get('employee_data', [])
            logger.warning("Used deprecated 'employee_data' parameter, please use 'employee_list' instead")
        
        # 簡化驗證：只檢查核心欄位
        if not work_list:
            return jsonify({
                'success': False,
                'error': 'Work list cannot be empty'
            }), 400
            
        if not employee_list:
            return jsonify({
                'success': False,
                'error': 'Employee list cannot be empty'
            }), 400
        
        # 檢查工作數據必要欄位
        for i, work in enumerate(work_list):
            missing_fields = []
            if 'measure_record_oid' not in work:
                missing_fields.append('measure_record_oid')
            if 'priority' not in work:
                missing_fields.append('priority')
            if 'difficulty' not in work:
                missing_fields.append('difficulty')
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Work item {i+1} is missing fields: {", ".join(missing_fields)}'
                }), 400
        
        # 檢查技師數據必要欄位  
        for i, emp in enumerate(employee_list):
            if 'id' not in emp or 'type' not in emp:
                return jsonify({
                    'success': False,
                    'error': f'Employee item {i+1} is missing id or type field'
                }), 400
            if emp['type'].upper() not in ['SENIOR', 'JUNIOR']:
                return jsonify({
                    'success': False,
                    'error': f'Employee item {i+1} type must be SENIOR or JUNIOR'
                }), 400
        
        logger.info(f"收到工作分配請求 (統一格式) - 工作數量: {len(work_list)}, 技師數量: {len(employee_list)}")
        
        # 直接調用重構後的分配函數
        work_df = pd.DataFrame(work_list)
        
        result_df, senior_workload, junior_workload = assign_workers_to_tasks(work_df, employee_list)
        
        # 統計結果
        assigned_count = len(result_df[result_df['assigned_worker'] != 'UNASSIGNED'])
        
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
        
        return jsonify({
            'success': True,
            'data': result_df[final_cols].to_dict('records'),
            'statistics': {
                'total_tasks': len(work_list),
                'assigned_tasks': assigned_count,
                'unassigned_tasks': len(work_list) - assigned_count,
                'assignment_rate': round((assigned_count / len(work_list)) * 100, 2),
                'senior_workloads': senior_workload,
                'junior_workloads': junior_workload
            },
            'message': 'Work assignment completed',
            'timestamp': datetime.now().isoformat()
        })
            
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
        "employee_file": "employee_list.csv"  // 可選，預設使用employee_list.csv
    }
    """
    try:
        request_data = request.get_json() or {}
        
        # 取得檔案路徑
        work_file = request_data.get('work_file', 'result.csv')
        employee_file = request_data.get('employee_file', 'employee_list.csv')
        
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
        
        logger.info(f"使用CSV檔案測試 - 工作檔案: {work_file}, 技師檔案: {employee_file}")
        
        # 執行工作分配
        result = api_handler.process_assignment(work_list, employee_list)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'statistics': result['statistics'],
                'message': 'CSV test completed successfully',
                'timestamp': datetime.now().isoformat(),
                'files_used': {
                    'work_file': work_file,
                    'employee_file': employee_file
                }
            })
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