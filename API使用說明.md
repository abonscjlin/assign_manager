# 工作分配管理系統 API 使用說明

## 📋 概述

工作分配管理系統API提供了統一的工作分配接口，支持多種數據格式和完整的報告生成功能。

## 🔧 主要改進

### ✅ 整合統一
- **合併端點**: 將 `process_assignment` 整合到 `/api/assign`
- **統一接口**: 支持完整格式和簡化格式的輸入
- **向前兼容**: 支持 `work_data`/`work_list` 和 `employee_data`/`employee_list` 參數

### 📁 結果管理  
- **按日期分組**: 結果自動保存到 `result/YYYYMMDD/` 目錄
- **時間戳標識**: 所有文件都包含時間戳（格式：`YYYYMMDD_HHMMSS`）避免覆蓋
- **完整報告**: 可選生成完整的分析報告（包含MD、統計、人力需求分析）
- **重用邏輯**: 使用 main_manager 相同的報告生成邏輯

### 📊 輸出格式
保持與原有格式完全一致的 statistics 輸出：
```json
{
  "statistics": {
    "assigned_tasks": 277,
    "assignment_rate": 85.49,
    "config_source": {
      "junior_workers_source": "employee_list",
      "senior_workers_source": "employee_list"
    },
    "junior_utilization": 99.92,
    "junior_workers": 10,
    "junior_workloads": {
      "he.yating": 457,
      "huang.xiaomin": 471,
      "liu.siyuan": 470,
      "song.jiaxin": 465,
      "wu.xiaodong": 469,
      "xu.zhihua": 463,
      "yang.yongkang": 465,
      "zheng.yuqing": 467,
      "zhou.wenjie": 456,
      "zhu.jiayi": 463
    },
    "leftover_junior": 4,
    "leftover_senior": 0,
    "meets_minimum_target": false,
    "minimum_target": 300,
    "overall_utilization": 99.94,
    "senior_utilization": 100.0,
    "senior_workers": 5,
    "senior_workloads": {
      "chen.minghua": 475,
      "li.jianguo": 475,
      "liu.dehua": 480,
      "wang.zhiqiang": 475,
      "zhang.yaqin": 475
    },
    "total_tasks": 324,
    "unassigned_tasks": 47
  }
}
```

## 🚀 API 端點

### 1. 工作分配 (主要端點)
**POST** `/api/assign`

#### 請求格式

##### 簡化格式 (推薦)
```json
{
  "work_list": [
    {
      "measure_record_oid": "WORK001",
      "priority": 1,
      "difficulty": 3
    }
  ],
  "employee_list": [
    {
      "id": "S001",
      "name": "張三",
      "type": "SENIOR"
    }
  ],
  "generate_reports": false
}
```

##### 完整格式
```json
{
  "work_list": [
    {
      "measure_record_oid": "WORK001",
      "upload_end_time": "2025-01-13",
      "promise_time": "2025-01-15",
      "task_status": "pending",
      "task_status_name": "待處理",
      "institution_id": "INST001",
      "data_effective_rate": 85.5,
      "num_af": 10,
      "num_pvc": 5,
      "num_sveb": 2,
      "delay_days": 0,
      "is_vip": true,
      "is_top_job": false,
      "is_simple_work": false,
      "priority": 1,
      "actual_record_days": 7,
      "source_file": "test.csv",
      "difficulty": 4,
      "x_value": 1.2
    }
  ],
  "employee_list": [
    {
      "id": "S001",
      "name": "張三",
      "type": "SENIOR"
    }
  ],
  "generate_reports": true
}
```

#### 回應格式
```json
{
  "success": true,
  "data": [
    {
      "measure_record_oid": "WORK001",
      "priority": 1,
      "difficulty": 3,
      "assigned_worker": "S001",
      "worker_type": "SENIOR",
      "estimated_time": 180
    }
  ],
  "statistics": {
    "total_tasks": 1,
    "assigned_tasks": 1,
    "assignment_rate": 100.0,
    "senior_workloads": {"S001": 180},
    "junior_workloads": {}
  },
  "result_directory": "/path/to/result/20250113",
  "message": "Work assignment completed",
  "timestamp": "2025-01-13T10:30:00"
}
```

### 2. 系統配置
**GET** `/api/config`

### 3. CSV測試
**POST** `/api/test/csv`

### 4. 健康檢查
**GET** `/health`

## 📁 結果文件結構

```
result/
└── 20250616/              # 按日期分組 (YYYYMMDD)
    ├── result_with_assignments_20250616_103000.csv           # 分配結果數據
    ├── assignment_summary_20250616_103000.txt                # 統計摘要
    ├── detailed_statistics_report_20250616_103000.txt       # 詳細統計報告*
    ├── workforce_requirements_analysis_20250616_103000.txt  # 人力需求分析*
    └── 工作分配分析報告_20250616_103000.md                   # MD格式綜合報告*
```

### 📋 文件命名規則
- **時間戳格式**: `YYYYMMDD_HHMMSS`（如：`20250616_103000`）
- **基本文件**: 始終包含時間戳，避免同日多次調用時的覆蓋問題
- **報告文件**: 當 `generate_reports: true` 時生成，也包含相同時間戳
- **統一時間戳**: 同一次API調用的所有文件使用相同時間戳，確保結果一致性
- **完整支持**: 所有核心模組都支持時間戳參數

*標記的文件只有在 `generate_reports: true` 時才會生成

## 🔧 使用示例

### Python 示例
```python
import requests

# 基本分配
response = requests.post('http://localhost:7777/api/assign', json={
    "work_list": [
        {"measure_record_oid": "W001", "priority": 1, "difficulty": 3},
        {"measure_record_oid": "W002", "priority": 2, "difficulty": 5}
    ],
    "employee_list": [
        {"id": "S001", "type": "SENIOR"},
        {"id": "J001", "type": "JUNIOR"}
    ]
})

if response.status_code == 200:
    result = response.json()
    print(f"分配成功率: {result['statistics']['assignment_rate']}%")
    print(f"結果保存到: {result['result_directory']}")
```

### cURL 示例
```bash
curl -X POST http://localhost:7777/api/assign \
  -H "Content-Type: application/json" \
  -d '{
    "work_list": [
      {"measure_record_oid": "W001", "priority": 1, "difficulty": 3}
    ],
    "employee_list": [
      {"id": "S001", "type": "SENIOR"}
    ],
    "generate_reports": true
  }'
```

## 🧪 測試工具

系統提供了完整的測試腳本：

```bash
# 基本測試
python test_api.py

# 指定API地址測試
python test_api.py http://localhost:7777
```

測試包含：
- ✅ 健康檢查
- ✅ 系統配置獲取
- ✅ 簡化格式分配
- ✅ CSV檔案分配
- ✅ 完整報告生成

## ⚡ 性能考量

### 響應時間
- **簡化分配**: < 1秒
- **完整報告**: 5-15秒（包含所有分析報告）

### 建議用法
- **即時API調用**: 使用 `generate_reports: false`
- **離線分析**: 使用 `generate_reports: true`
- **大量數據**: 考慮分批處理

## 🔍 故障排除

### 常見錯誤

1. **400 錯誤 - 數據格式問題**
   ```json
   {
     "success": false,
     "error": "Work item 1 is missing core fields: priority"
   }
   ```
   解決：確保每個工作項包含 `measure_record_oid`, `priority`, `difficulty`

2. **500 錯誤 - 內部錯誤**
   檢查服務器日誌，可能是數據計算錯誤

3. **超時錯誤**
   使用 `generate_reports: false` 或增加客戶端超時時間

### 調試建議
- 使用健康檢查確認服務狀態
- 查看 `result_directory` 確認文件生成
- 檢查服務器日誌獲取詳細錯誤信息

## 📞 技術支持

- 📋 完整文檔: `README.md`
- 🔧 配置說明: `config_params.py`
- 🧪 測試工具: `test_api.py`
- 📊 原始功能: `main_manager.py` 