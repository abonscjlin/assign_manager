# 工作分配管理系統 (Work Assignment Management System)

一個智能化的工作分配管理系統，能夠自動分析工作負載、優化人力配置，並生成詳細的分析報告。

## 🌟 系統特色

### 核心功能
- **🎯 智能工作分配**：自動將工作分配給最適合的員工
- **📊 多策略優化**：支持多種分配策略的比較和分析
- **🔧 人力需求分析**：自動計算達成目標所需的人力配置
- **📋 MD格式報告**：生成結構化的Markdown分析報告
- **⚡ 實時監控**：即時顯示分配進度和效率指標

### 技術特點
- **參數化設計**：支持外部參數輸入，無硬編碼
- **遞增式算法**：智能計算最小人力增加方案
- **多格式輸出**：CSV數據文件、TXT摘要、MD報告
- **錯誤處理**：完善的異常處理和數據驗證
- **模組化架構**：易於擴展和維護

## 🏗️ 系統架構

```
assign_manager/
├── main_manager.py              # 主要管理器，統一執行流程
├── strategy_manager.py         # 策略管理器，核心分配算法
├── optimal_strategy_analysis.py # 最佳策略分析模組
├── incremental_workforce_calculator.py # 遞增式人力計算器
├── workforce_api.py            # 人力需求分析API
├── md_report_generator.py      # MD格式報告生成器
├── config_params.py           # 系統配置參數
├── result.csv                 # 原始工作數據
├── setup.py                   # 安裝和依賴管理
└── result/                    # 輸出結果目錄
    ├── result_with_assignments.csv          # 分配結果數據
    ├── assignment_summary.txt               # 分配摘要
    ├── detailed_statistics_report.txt      # 詳細統計報告
    ├── workforce_requirements_analysis.txt # 人力需求分析
    └── 工作分配分析報告_TIMESTAMP.md        # MD格式綜合報告
```

## 📦 安裝說明

### 使用 setup.py 安裝

1. **克隆或下載專案**
```bash
cd assign_manager
```

2. **檢查安裝配置**
```bash
python setup.py check
```

3. **安裝依賴套件**
```bash
# 開發模式安裝（推薦用於開發）
python setup.py develop

# 標準安裝
python setup.py install

# 安裝包含開發工具
python setup.py develop[dev]

# 僅安裝到用戶目錄
python setup.py install --user
```

4. **使用 pip 安裝（推薦）**
```bash
# 從當前目錄安裝
pip install -e .

# 安裝包含開發依賴
pip install -e .[dev]

# 或使用 requirements.txt
pip install -r requirements.txt
```

5. **驗證安裝**
```bash
python -c "import pandas, numpy; print('✅ 依賴套件安裝成功！')"
python main_manager.py --help
```

6. **創建分發包（可選）**
```bash
# 創建源代碼分發包
python setup.py sdist

# 創建二進制分發包
python setup.py bdist_wheel

# 打包文件會在 dist/ 目錄中
```

### 手動安裝依賴
如果不使用setup.py，也可以手動安裝：
```bash
pip install pandas numpy
```

## 🚀 使用方法

### 1. 快速開始
執行完整的工作分配流程：
```bash
python main_manager.py
```

### 2. 指定模式運行

#### 僅執行人力需求分析
```bash
python main_manager.py --workforce-only
```

#### 查看幫助信息
```bash
python main_manager.py --help
```

### 3. 配置系統參數

編輯 `config_params.py` 文件：
```python
# 人員配置
SENIOR_WORKERS = 5      # 資深員工數量
JUNIOR_WORKERS = 10     # 一般員工數量

# 目標設定
MINIMUM_WORK_TARGET = 300  # 最低完成目標

# 工作能力設定
SENIOR_WORK_CAPACITY = 480   # 資深員工工作時間(分鐘)
JUNIOR_WORK_CAPACITY = 480   # 一般員工工作時間(分鐘)

# 薪資設定(用於成本分析)
SENIOR_HOURLY_RATE = 1000   # 資深員工時薪
JUNIOR_HOURLY_RATE = 600    # 一般員工時薪
```

## 📊 執行流程

系統執行5個主要步驟：

### 第1步：最佳策略分析
- 分析當前配置下的最佳工作分配方案
- 計算各難度工作的分配比例
- 評估目標達成情況

### 第2步：具體工作分配
- 將工作分配給具體的員工個體
- 平衡每個員工的工作負載
- 優化時間利用率

### 第3步：生成詳細報告
- 統計分析所有分配結果
- 生成詳細的數據報告
- 提供性能評估建議

### 第4步：人力需求分析
- 檢測是否達成最低目標
- 計算達標所需的人力配置
- 提供成本效益分析

### 第5步：生成MD格式報告
- 整合所有分析結果
- 生成結構化的Markdown報告
- 包含完整的數據表格和分析

## 📋 輸出文件說明

### CSV 數據文件
- **result_with_assignments.csv**：包含每項工作的詳細分配信息
  - `assigned_worker`：分配的具體員工
  - `worker_type`：員工類型 (SENIOR/JUNIOR)
  - `estimated_time`：預估完成時間

### 文本報告
- **assignment_summary.txt**：分配摘要，包含關鍵統計數字
- **detailed_statistics_report.txt**：詳細統計分析報告
- **workforce_requirements_analysis.txt**：人力需求分析結果

### Markdown 報告
- **工作分配分析報告_TIMESTAMP.md**：完整的分析報告，包含：
  - 📊 執行概覽和KPI指標
  - 🎯 工作分配統計分析
  - 👥 員工工作負載詳情
  - 🔧 人力需求分析建議

## ⚙️ 高級功能

### 外部參數支持
系統支持運行時參數覆蓋，適合批次處理和自動化：

```python
from strategy_manager import StrategyManager

# 使用自定義參數
custom_params = {
    'senior_workers': 8,
    'junior_workers': 12,
    'minimum_work_target': 350
}

manager = StrategyManager()
result = manager.advanced_optimal_strategy_analysis(**custom_params)
```

### 多策略比較
支持4種不同的人力配置策略：
- **senior_only**：優先增加資深員工
- **junior_only**：優先增加一般員工
- **balanced**：平衡增加兩種員工
- **cost_optimal**：成本最優策略

### API 接口
提供程式化接口供其他系統調用：

```python
from workforce_api import calculate_required_workforce, get_current_status

# 獲取當前狀態
status = get_current_status()

# 計算所需人力
result = calculate_required_workforce(target=350)
```

## 🔧 常見問題

### Q: 如何修改工作時間設定？
A: 編輯 `config_params.py` 中的 `SENIOR_WORK_CAPACITY` 和 `JUNIOR_WORK_CAPACITY` 參數。

### Q: 系統支援哪些數據格式？
A: 目前支援CSV格式的工作數據，需包含以下欄位：
- `difficulty`：工作難度 (1-7)
- `priority`：優先權 (1-6)
- `estimated_time`：預估時間

### Q: 如何自定義輸出目錄？
A: 系統會自動在 `result/` 目錄下生成所有輸出文件。如需修改，請編輯各模組中的路徑設定。

### Q: 報告生成失敗怎麼辦？
A: 檢查以下項目：
1. `result/` 目錄是否存在且有寫入權限
2. 原始數據文件 `result.csv` 是否存在
3. 所有依賴套件是否正確安裝

## 📈 性能優化建議

### 大量數據處理
- 建議工作數據量控制在10,000件以內以獲得最佳性能
- 對於更大的數據集，考慮分批處理

### 記憶體使用
- 系統在處理過程中會載入完整數據到記憶體
- 建議至少預留512MB可用記憶體

### 執行時間
- 典型執行時間：372件工作約0.2秒
- 複雜分析可能需要1-2秒

## 🤝 技術支援

### 系統需求
- Python 3.7+
- pandas 1.0+
- numpy 1.18+

### 相容性
- 支援 Windows、macOS、Linux
- 支援中文檔名和路徑
- 相容於各種Python環境

### 疑難排解
如遇到問題，請檢查：
1. Python版本是否符合需求
2. 所有依賴套件是否正確安裝
3. 數據文件格式是否正確
4. 系統權限是否足夠

---

**開發版本：** v2.0  
**最後更新：** 2025年6月  
**授權：** MIT License  

---

> 💡 **提示**：首次使用建議先執行 `python main_manager.py --help` 查看所有可用選項。

## 💰 成本計算公式詳解

### 基礎參數設定

```python
# 預設人力配置
SENIOR_WORKERS = 5      # 資深員工人數
JUNIOR_WORKERS = 10     # 一般員工人數

# 成本權重設定（在 incremental_workforce_calculator.py 中定義）
senior_cost_weight = 1.5    # 資深員工成本權重
junior_cost_weight = 1.0    # 一般員工成本權重
```

### 成本計算邏輯

#### 1. 基礎成本計算
```
基礎成本 = (資深員工人數 × 資深成本權重) + (一般員工人數 × 一般成本權重)
基礎成本 = (5 × 1.5) + (10 × 1.0) = 7.5 + 10 = 17.5 單位
```

#### 2. 新配置成本計算
```
新配置成本 = (新資深員工人數 × 資深成本權重) + (新一般員工人數 × 一般成本權重)

例如推薦配置 9資深 + 10一般：
新配置成本 = (9 × 1.5) + (10 × 1.0) = 13.5 + 10 = 23.5 單位
```

#### 3. 成本增加計算
```
成本增加 = 新配置成本 - 基礎成本
成本增加 = 23.5 - 17.5 = 6.0 單位

成本增加百分比 = (成本增加 ÷ 基礎成本) × 100%
成本增加百分比 = (6.0 ÷ 17.5) × 100% = 34.3%
```

### 核心計算公式實現

```python
# 在 incremental_workforce_calculator.py 第79行實現
total_cost = senior_workers * senior_cost_weight + junior_workers * junior_cost_weight
base_cost = base_senior_workers * senior_cost_weight + base_junior_workers * junior_cost_weight
cost_increase = total_cost - base_cost
cost_increase_percentage = (cost_increase / base_cost) * 100 if base_cost > 0 else 0
```

### 計算範例：34.3%成本增加的由來

**情境：從5資深+10一般 → 9資深+10一般**

```
基礎配置成本：
5 × 1.5 + 10 × 1.0 = 17.5 單位

推薦配置成本：
9 × 1.5 + 10 × 1.0 = 23.5 單位

成本增加：
23.5 - 17.5 = 6.0 單位

成本增加百分比：
(6.0 ÷ 17.5) × 100% = 34.285...% ≈ 34.3%
```

**關鍵要點：**
- 雖然只增加4名資深員工，但由於資深員工成本權重較高（1.5倍）
- 相對於基礎成本17.5單位，6.0單位的增加確實達到34.3%
- 這個百分比反映的是相對成本增加，而非絕對人數增加比例

## ⏱️ 工作時間配置

### 資深員工作業時間（分鐘）
```python
SENIOR_TIME = {
    1: 60,  # 難度1：60分鐘
    2: 50,  # 難度2：50分鐘  
    3: 40,  # 難度3：40分鐘
    4: 30,  # 難度4：30分鐘
    5: 20,  # 難度5：20分鐘
    6: 10,  # 難度6：10分鐘
    7: 5    # 難度7：5分鐘
}
```

### 一般員工作業時間
```python
# 一般員工需要1.5倍時間
JUNIOR_TIME = {k: int(v * 1.5) for k, v in SENIOR_TIME.items()}
```

## 📋 系統配置參數表

| 參數 | 預設值 | 說明 | 位置 |
|------|--------|------|------|
| SENIOR_WORKERS | 5 | 資深員工人數 | config_params.py |
| JUNIOR_WORKERS | 10 | 一般員工人數 | config_params.py |
| WORK_HOURS_PER_DAY | 480 | 每人每日工時（分鐘）| config_params.py |
| MINIMUM_WORK_TARGET | 300 | 每日最低工作完成目標 | config_params.py |
| senior_cost_weight | 1.5 | 資深員工成本權重 | incremental_workforce_calculator.py |
| junior_cost_weight | 1.0 | 一般員工成本權重 | incremental_workforce_calculator.py |

## 🔧 重要注意事項

1. **成本權重可調整**：可在初始化 `IncrementalWorkforceCalculator` 時自定義成本權重
2. **目標不可降低**：系統設計確保 `MINIMUM_WORK_TARGET` 不會被降低
3. **時間單位統一**：所有時間計算均以分鐘為單位
4. **報告自動生成**：每次執行都會生成帶時間戳的報告文件
5. **成本計算基於相對權重**：實際金額需要根據具體薪資標準進行換算