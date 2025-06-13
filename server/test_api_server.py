#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Server 測試腳本
==================

測試工作分配管理系統的API功能
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta

# API Server 位址
API_BASE_URL = "http://localhost:7777"

def test_health_check():
    """測試健康檢查端點"""
    print("🔍 測試健康檢查...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康檢查成功: {data['status']}")
            print(f"   服務: {data['service']}")
            print(f"   版本: {data['version']}")
            return True
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康檢查錯誤: {str(e)}")
        return False

def test_get_config():
    """測試取得配置端點"""
    print("\n🔍 測試系統配置...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/config")
        if response.status_code == 200:
            data = response.json()
            config = data['config']
            print("✅ 配置取得成功:")
            print(f"   最低工作目標: {config['minimum_work_target']} 件")
            print(f"   每人日工時: {config['work_hours_per_day']} 分鐘")
            print(f"   必要工作欄位數: {len(config['required_work_fields'])}")
            print(f"   必要員工欄位數: {len(config['required_employee_fields'])}")
            return True
        else:
            print(f"❌ 配置取得失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 配置取得錯誤: {str(e)}")
        return False

def create_sample_data():
    """建立測試用的樣本資料"""
    
    # 建立工作清單樣本
    work_list = []
    base_date = datetime.now()
    
    for i in range(20):  # 建立20筆工作
        work = {
            "measure_record_oid": f"WRK{i+1:04d}",
            "upload_end_time": (base_date - timedelta(days=i)).strftime("%Y-%m-%d"),
            "promise_time": (base_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "task_status": 1,
            "task_status_name": "待處理",
            "institution_id": f"INS{(i % 5)+1:03d}",
            "data_effective_rate": round(85 + (i % 15), 2),
            "num_af": i % 10,
            "num_pvc": (i * 2) % 15,
            "num_sveb": (i * 3) % 8,
            "delay_days": max(0, i - 10),
            "is_vip": i % 5 == 0,
            "is_top_job": i % 7 == 0,
            "is_simple_work": i % 3 == 0,
            "priority": (i % 3) + 1,  # 優先權1-3
            "actual_record_days": i % 15 + 1,
            "source_file": f"source_{i+1}.dat",
            "difficulty": (i % 7) + 1,  # 難度1-7，與實際數據一致
            "x_value": round(i * 1.5 + 10, 2)
        }
        work_list.append(work)
    
    # 建立員工清單樣本
    employee_list = [
        {"id": "chen.minghua", "type": "SENIOR"},
        {"id": "li.jianguo", "type": "SENIOR"},
        {"id": "wang.zhiqiang", "type": "SENIOR"},
        {"id": "huang.xiaomin", "type": "JUNIOR"},
        {"id": "zhou.wenjie", "type": "JUNIOR"},
        {"id": "wu.xiaodong", "type": "JUNIOR"},
        {"id": "zheng.yuqing", "type": "JUNIOR"},
        {"id": "liu.siyuan", "type": "JUNIOR"}
    ]
    
    return work_list, employee_list

def test_work_assignment():
    """測試工作分配端點"""
    print("\n🔍 測試工作分配...")
    
    # 建立測試資料
    work_list, employee_list = create_sample_data()
    
    # 準備請求資料
    request_data = {
        "work_list": work_list,
        "employee_list": employee_list
    }
    
    try:
        # 發送API請求
        print(f"📤 發送請求: {len(work_list)}筆工作, {len(employee_list)}名員工")
        response = requests.post(
            f"{API_BASE_URL}/api/assign",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 工作分配成功!")
                
                # 顯示統計資訊
                stats = data['statistics']
                print(f"📊 分配統計:")
                print(f"   總工作數: {stats['total_tasks']}")
                print(f"   已分配: {stats['assigned_tasks']}")
                print(f"   未分配: {stats['unassigned_tasks']}")
                print(f"   分配率: {stats['assignment_rate']}%")
                print(f"   資深員工: {stats['senior_workers']}人")
                print(f"   一般員工: {stats['junior_workers']}人")
                
                # 顯示員工工作量
                print(f"👨‍💼 資深員工工作量:")
                for name, workload in stats['senior_workloads'].items():
                    print(f"   {name}: {workload}分鐘")
                
                print(f"👩‍💼 一般員工工作量:")
                for name, workload in stats['junior_workloads'].items():
                    print(f"   {name}: {workload}分鐘")
                
                # 檢查輸出資料格式
                result_data = data['data']
                first_record = result_data[0] if result_data else {}
                
                print(f"📋 輸出欄位檢查:")
                print(f"   原始欄位數: {len([k for k in first_record.keys() if k not in ['assigned_worker', 'worker_type', 'estimated_time']])}")
                print(f"   新增欄位: {', '.join([k for k in ['assigned_worker', 'worker_type', 'estimated_time'] if k in first_record])}")
                
                # 顯示幾筆分配結果樣本
                print(f"📝 分配結果樣本 (前3筆):")
                for i, record in enumerate(result_data[:3]):
                    print(f"   {i+1}. {record['measure_record_oid']} -> {record['assigned_worker']} ({record['worker_type']}) {record['estimated_time']}分")
                
                return True
            else:
                print(f"❌ 工作分配失敗: {data['error']}")
                return False
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            print(f"   回應: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 工作分配錯誤: {str(e)}")
        return False

def test_csv_endpoint():
    """測試CSV檔案端點"""
    print("\n🔍 測試CSV檔案功能...")
    
    try:
        # 使用預設的CSV檔案
        request_data = {
            "work_file": "result.csv",
            "employee_file": "employee_list.csv"
        }
        
        print("📤 發送CSV測試請求...")
        response = requests.post(
            f"{API_BASE_URL}/api/test/csv",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ CSV測試成功!")
                
                # 顯示統計資訊
                stats = data['statistics']
                print(f"📊 CSV分配統計:")
                print(f"   總工作數: {stats['total_tasks']}")
                print(f"   已分配: {stats['assigned_tasks']}")
                print(f"   分配率: {stats['assignment_rate']}%")
                print(f"   來源檔案: {data['source']['work_file']}, {data['source']['employee_file']}")
                
                return True
            else:
                print(f"❌ CSV測試失敗: {data['error']}")
                return False
        else:
            print(f"❌ CSV API請求失敗: {response.status_code}")
            print(f"   回應: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CSV測試錯誤: {str(e)}")
        return False

def test_error_handling():
    """測試錯誤處理"""
    print("\n🔍 測試錯誤處理...")
    
    success_count = 0
    total_tests = 2
    
    # 測試空資料
    print("   測試空工作清單...")
    response = requests.post(
        f"{API_BASE_URL}/api/assign",
        json={"work_list": [], "employee_list": [{"id": "test.employee", "type": "SENIOR"}]},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 400:
        print("   ✅ 空工作清單錯誤處理正確")
        success_count += 1
    else:
        print("   ❌ 空工作清單錯誤處理異常")
    
    # 測試無效員工類型
    print("   測試無效員工類型...")
    work_list, _ = create_sample_data()
    response = requests.post(
        f"{API_BASE_URL}/api/assign",
        json={
            "work_list": work_list[:1],
            "employee_list": [{"id": "test.invalid", "type": "INVALID"}]
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 400:
        print("   ✅ 無效員工類型錯誤處理正確")
        success_count += 1
    else:
        print("   ❌ 無效員工類型錯誤處理異常")
    
    print("✅ 錯誤處理測試完成")
    return success_count == total_tests

def save_test_results():
    """保存測試結果到檔案"""
    print("\n💾 保存測試結果...")
    
    # 建立測試資料
    work_list, employee_list = create_sample_data()
    
    # 準備請求資料
    request_data = {
        "work_list": work_list,
        "employee_list": employee_list
    }
    
    try:
        # 發送API請求
        response = requests.post(
            f"{API_BASE_URL}/api/assign",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                # 保存結果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 保存完整回應
                with open(f"test_api_result_{timestamp}.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 保存為CSV
                result_df = pd.DataFrame(data['data'])
                result_df.to_csv(f"test_api_result_{timestamp}.csv", index=False, encoding='utf-8')
                
                print(f"✅ 測試結果已保存:")
                print(f"   JSON: test_api_result_{timestamp}.json")
                print(f"   CSV:  test_api_result_{timestamp}.csv")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 保存測試結果錯誤: {str(e)}")
        return False

def main():
    """主測試函數"""
    print("🧪 API Server 功能測試")
    print("=" * 50)
    
    # 等待API server啟動
    print("⏳ 等待API server啟動...")
    time.sleep(2)
    
    test_results = []
    
    # 執行各項測試
    test_results.append(("健康檢查", test_health_check()))
    test_results.append(("系統配置", test_get_config()))
    test_results.append(("工作分配", test_work_assignment()))
    test_results.append(("CSV功能", test_csv_endpoint()))
    test_results.append(("錯誤處理", test_error_handling()))
    test_results.append(("保存結果", save_test_results()))
    
    # 測試總結
    print("\n" + "=" * 50)
    print("📋 測試結果總結:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 測試統計: {passed}/{total} 通過 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有測試通過！API server功能正常！")
    else:
        print("⚠️  部分測試失敗，請檢查API server狀態")

if __name__ == "__main__":
    main() 