# 工作分配管理系統 API 文檔

## 📖 概述

工作分配管理系統提供了一套完整的 REST API，用於自動化工作任務分配。系統支援基於技師技能等級、工作難度和優先級的智能分配算法。

**Base URL**: `http://localhost:7777`  
**API Version**: 1.0.0  
**Content-Type**: `application/json`

---

## 🔗 API 端點總覽

| 端點 | 方法 | 功能 | 狀態 |
|------|------|------|------|
| `/health` | GET | 系統健康檢查 | ✅ 可用 |
| `/api/config` | GET | 獲取系統配置 | ✅ 可用 |
| `/process_assignment` | POST | 工作分配（統一參數格式） | ✅ 推薦 |
| `/api/assign` | POST | 工作分配（完整驗證版本） | ✅ 可用 |
| `/api/test/csv` | POST | CSV檔案測試 | ✅ 可用 |

---

## 📋 詳細 API 說明

### 1. 系統健康檢查

檢查 API 服務運行狀態。

#### 請求
```http
GET /health
```

#### 參數
無需參數

#### 回應
```json
{
  "service": "工作分配管理系統API",
  "status": "healthy",
  "timestamp": "2025-06-13T01:09:12.627425",
  "version": "1.0.0"
}
```

#### 回應欄位說明
| 欄位 | 類型 | 說明 |
|------|------|------|
| `service` | string | 服務名稱 |
| `status` | string | 服務狀態（healthy/unhealthy） |
| `timestamp` | string | 回應時間戳（ISO 8601格式） |
| `version` | string | API版本號 |

---

### 2. 獲取系統配置

獲取工作分配系統的配置參數。

#### 請求
```http
GET /api/config
```

#### 參數
無需參數

#### 回應
```json
{
  "success": true,
  "config": {
    "minimum_work_target": 300,
    "work_hours_per_day": 480,
    "senior_time": {
      "1": 5,
      "2": 10,
      "3": 20,
      "4": 30,
      "5": 40,
      "6": 50,
      "7": 60
    },
    "junior_time": {
      "1": 7,
      "2": 15,
      "3": 30,
      "4": 45,
      "5": 60,
      "6": 75,
      "7": 90
    },
    "required_work_fields": ["measure_record_oid", "priority", "difficulty"],
    "required_employee_fields": ["id", "type"],
    "output_fields": ["measure_record_oid", "assigned_worker", "worker_type", "estimated_time"]
  },
  "timestamp": "2025-06-13T01:09:12.627425"
}
```

#### 配置參數說明
| 參數 | 類型 | 說明 |
|------|------|------|
| `minimum_work_target` | integer | 最低工作目標（件數） |
| `work_hours_per_day` | integer | 每日工作時間（分鐘） |
| `senior_time` | object | 資深技師各難度完成時間（分鐘） |
| `junior_time` | object | 一般技師各難度完成時間（分鐘） |
| `required_work_fields` | array | 工作數據必要欄位 |
| `required_employee_fields` | array | 技師數據必要欄位 |
| `output_fields` | array | 輸出結果欄位 |

---

### 3. 工作分配（統一參數格式） 🌟 推薦

執行工作分配，使用統一的參數命名格式，支持向前兼容，只檢查核心必要欄位。

#### 請求
```http
POST /process_assignment
Content-Type: application/json
```

#### 請求參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `work_list` | array | ✅ | 工作清單陣列（推薦） |
| `employee_list` | array | ✅ | 技師清單陣列（推薦） |
| `work_data` | array | ⚠️ | 工作清單陣列（已棄用，向前兼容） |
| `employee_data` | array | ⚠️ | 技師清單陣列（已棄用，向前兼容） |

##### work_list 陣列元素

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| `measure_record_oid` | string | ✅ | 工作記錄唯一識別碼 | "75961" |
| `priority` | integer | ✅ | 工作優先級（1-5，1最高） | 1 |
| `difficulty` | integer | ✅ | 工作難度（1-7，1最簡單） | 2 |
| `x_value` | integer | ❌ | 工作量指標 | 637 |

##### employee_list 陣列元素

| 欄位 | 類型 | 必填 | 說明 | 可用值 |
|------|------|------|------|------|
| `id` | string | ✅ | 技師唯一識別碼 | "chen.minghua" |
| `type` | string | ✅ | 技師技能等級 | "SENIOR", "JUNIOR" |

#### 請求範例（推薦格式）
```json
{
  "work_list": [
    {
      "measure_record_oid": "75961",
      "priority": 1,
      "difficulty": 2,
      "x_value": 637
    },
    {
      "measure_record_oid": "76361",
      "priority": 1,
      "difficulty": 1,
      "x_value": 476
    }
  ],
  "employee_list": [
    {
      "id": "chen.minghua",
      "type": "SENIOR"
    },
    {
      "id": "huang.xiaomin",
      "type": "JUNIOR"
    }
  ]
}
```

#### 向前兼容範例（會顯示棄用警告）
```json
{
  "work_data": [...],
  "employee_data": [...]
}
```

#### 回應

##### 成功回應（200 OK）
```json
{
  "success": true,
  "data": [
    {
      "measure_record_oid": "75961",
      "assigned_worker": "chen.minghua",
      "worker_type": "SENIOR",
      "priority": 1,
      "difficulty": 2,
      "estimated_time": 10,
      "x_value": 637
    },
    {
      "measure_record_oid": "76361",
      "assigned_worker": "huang.xiaomin",
      "worker_type": "JUNIOR",
      "priority": 1,
      "difficulty": 1,
      "estimated_time": 10,
      "x_value": 476
    }
  ],
  "statistics": {
    "total_tasks": 2,
    "assigned_tasks": 2,
    "unassigned_tasks": 0,
    "assignment_rate": 100.0,
    "senior_workloads": {
      "chen.minghua": 10
    },
    "junior_workloads": {
      "huang.xiaomin": 10
    }
  },
  "message": "Work assignment completed",
  "timestamp": "2025-06-13T01:09:46.006364"
}
```

##### 回應欄位說明

**data 陣列元素：**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `measure_record_oid` | string | 工作記錄ID |
| `assigned_worker` | string | 分配到的技師ID |
| `worker_type` | string | 技師類型（SENIOR/JUNIOR） |
| `priority` | integer | 工作優先級 |
| `difficulty` | integer | 工作難度 |
| `estimated_time` | integer | 預估完成時間（分鐘） |
| `x_value` | integer | 工作量指標 |

**statistics 統計資訊：**
| 欄位 | 類型 | 說明 |
|------|------|------|
| `total_tasks` | integer | 總工作數量 |
| `assigned_tasks` | integer | 已分配工作數量 |
| `unassigned_tasks` | integer | 未分配工作數量 |
| `assignment_rate` | float | 分配成功率（%） |
| `senior_workloads` | object | 資深技師工作負荷（技師ID: 總時間） |
| `junior_workloads` | object | 一般技師工作負荷（技師ID: 總時間） |

##### 錯誤回應（400 Bad Request）
```json
{
  "success": false,
  "error": "Work item 1 is missing fields: priority, difficulty"
}
```

##### 錯誤回應（500 Internal Server Error）
```json
{
  "success": false,
  "error": "System error: Database connection failed"
}
```

---

### 4. 工作分配（完整驗證版本）

執行工作分配，使用完整的數據驗證，檢查所有必要欄位（18個），提供豐富的統計分析。

#### 請求
```http
POST /api/assign
Content-Type: application/json
```

#### 請求參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `work_list` | array | ✅ | 工作清單陣列（完整格式） |
| `employee_list` | array | ✅ | 技師清單陣列 |

##### work_list 陣列元素（完整格式）

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| `measure_record_oid` | integer | ✅ | 工作記錄ID | 75961 |
| `upload_end_time` | string | ❌ | 上傳結束時間 | "2025-06-11 10:39:51.814" |
| `promise_time` | string | ❌ | 承諾完成時間 | "2025-06-12 10:39:51.814" |
| `task_status` | integer | ❌ | 任務狀態代碼 | 2 |
| `task_status_name` | string | ❌ | 任務狀態名稱 | "IN_PROGRESS" |
| `institution_id` | string | ❌ | 機構ID | "ap037" |
| `data_effective_rate` | float | ❌ | 數據有效率 | 0.9894 |
| `num_af` | integer | ❌ | AF數量 | 0 |
| `num_pvc` | integer | ❌ | PVC數量 | 554 |
| `num_sveb` | integer | ❌ | SVEB數量 | 83 |
| `priority` | integer | ✅ | 工作優先級 | 1 |
| `difficulty` | integer | ✅ | 工作難度 | 2 |
| `x_value` | integer | ❌ | 工作量指標 | 637 |

#### 請求範例
```json
{
  "work_list": [
    {
      "measure_record_oid": 75961,
      "upload_end_time": "2025-06-11 10:39:51.814",
      "promise_time": "2025-06-12 10:39:51.814",
      "task_status": 2,
      "task_status_name": "IN_PROGRESS",
      "institution_id": "ap037",
      "data_effective_rate": 0.9894,
      "num_af": 0,
      "num_pvc": 554,
      "num_sveb": 83,
      "priority": 1,
      "difficulty": 2,
      "x_value": 637
    }
  ],
  "employee_list": [
    {
      "id": "chen.minghua",
      "type": "SENIOR"
    }
  ]
}
```

#### 回應
與簡化版本相同的格式，但包含所有原始工作欄位。

---

### 5. CSV檔案測試

使用本地CSV檔案進行工作分配測試，適合開發和調試。

#### 請求
```http
POST /api/test/csv
Content-Type: application/json
```

#### 請求參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `work_file` | string | ❌ | "result.csv" | 工作清單CSV檔案名稱 |
| `employee_file` | string | ❌ | "employee_list.csv" | 技師清單CSV檔案名稱 |

#### 請求範例
```json
{
  "work_file": "result.csv",
  "employee_file": "employee_list.csv"
}
```

#### 回應
```json
{
  "success": true,
  "data": [...],
  "statistics": {...},
  "message": "CSV test completed successfully",
  "files_used": {
    "work_file": "result.csv",
    "employee_file": "employee_list.csv"
  },
  "timestamp": "2025-06-13T01:09:46.006364"
}
```

---

## 🛠️ 工作難度等級說明

系統使用1-7級難度分類：

| 難度等級 | 分類 | 資深技師時間 | 一般技師時間 | 說明 |
|----------|------|-------------|-------------|------|
| 1 | 簡單 | 5分鐘 | 7分鐘 | 基礎操作 |
| 2 | 簡單 | 10分鐘 | 15分鐘 | 輕度處理 |
| 3 | 中等 | 20分鐘 | 30分鐘 | 標準處理 |
| 4 | 中等 | 30分鐘 | 45分鐘 | 複雜處理 |
| 5 | 中等 | 40分鐘 | 60分鐘 | 高級處理 |
| 6 | 困難 | 50分鐘 | 75分鐘 | 專業技能需求 |
| 7 | 困難 | 60分鐘 | 90分鐘 | 高難度專業 |

---

## 📊 優先級說明

| 優先級 | 說明 | 處理順序 |
|--------|------|----------|
| 1 | 最高優先級 | 優先分配 |
| 2 | 高優先級 | 次優先分配 |
| 3 | 中等優先級 | 標準分配 |
| 4 | 低優先級 | 後續分配 |
| 5 | 最低優先級 | 最後分配 |

---

## ⚠️ 錯誤代碼說明

### HTTP 狀態碼

| 狀態碼 | 說明 | 原因 |
|--------|------|------|
| 200 | 成功 | 請求處理成功 |
| 400 | 錯誤請求 | 參數格式錯誤或缺少必要欄位 |
| 500 | 內部服務器錯誤 | 系統處理異常 |

### 常見錯誤訊息

| 錯誤訊息 | 原因 | 解決方案 |
|----------|------|----------|
| "Request data cannot be empty" | 請求body為空 | 提供正確的JSON數據 |
| "Work list cannot be empty" | work_list陣列為空 | 至少提供一個工作項目 |
| "Employee list cannot be empty" | employee_list陣列為空 | 至少提供一個技師 |
| "Work item X is missing fields: ..." | 必要欄位缺失 | 補充缺少的欄位 |
| "Employee item X type must be SENIOR or JUNIOR" | 技師類型錯誤 | 使用正確的技師類型 |
| "Work list format error: ..." | 工作清單格式錯誤 | 檢查JSON格式和數據類型 |
| "Employee list format error: ..." | 技師清單格式錯誤 | 檢查JSON格式和必要欄位 |
| "System error: ..." | 系統內部錯誤 | 檢查服務狀態或聯繫技術支援 |

---

## 💡 最佳實踐

### 1. 效能優化
- 單次請求建議不超過1000個工作項目
- 技師數量建議在10-50人之間以獲得最佳分配效果

### 2. 數據準備
- 確保工作難度分佈均勻
- 保持資深技師與一般技師的合理比例（建議1:2到1:3）

### 3. 錯誤處理
- 實現適當的重試機制
- 記錄並監控API回應時間

### 4. 安全考量
- 在生產環境中實施適當的認證機制
- 限制API請求頻率

---

## 📞 支援資訊

- **API版本**: 1.0.0
- **文檔更新日期**: 2025-06-13
- **技術支援**: 請參考項目README或提交issue

---

## 🔄 端點選擇建議

### `/process_assignment` vs `/api/assign`

| 特性 | `/process_assignment` | `/api/assign` |
|------|----------------------|---------------|
| **驗證嚴格度** | 僅檢查3個核心欄位 | 檢查18個完整欄位 |
| **統計詳細度** | 基本統計 | 豐富的策略分析 |
| **處理效能** | 較快 | 較慢（完整驗證） |
| **適用場景** | 快速測試、輕量級應用 | 正式生產、需要詳細分析 |
| **向前兼容** | 支援舊參數格式 | 僅支援新格式 |

**建議**：
- 開發測試階段使用 `/process_assignment`
- 生產環境使用 `/api/assign`

---

**注意**: 本API目前為開發版本，生產環境使用前請確保進行充分測試。所有錯誤訊息已統一使用英文格式。 