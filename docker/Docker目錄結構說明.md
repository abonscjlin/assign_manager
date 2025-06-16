# Docker目錄結構說明

## 🗂️ 新的目錄結構

為了避免多個Docker容器之間的混淆，我們已經實現了專用的目錄結構：

### 📁 目錄配置

```
使用者家目錄/
└── docker/                           # Docker專用總目錄
    └── assign_manager/               # 工作分配系統專用目錄
        ├── result/                   # 結果輸出目錄（掛載到容器）
        ├── employee_list.csv         # 技師清單檔案
        └── result.csv               # 工作清單檔案
```

### 🎯 實際路徑

- **Docker專用目錄**: `~/docker/assign_manager/`
- **結果輸出目錄**: `~/docker/assign_manager/result/`
- **技師清單檔案**: `~/docker/assign_manager/employee_list.csv`
- **工作清單檔案**: `~/docker/assign_manager/result.csv`
- **項目源代碼**: 仍在原來的項目目錄中

## 🔗 掛載配置

### Docker Compose掛載設定

```yaml
volumes:
  - ~/docker/assign_manager/result:/app/result                      # 結果輸出
  - ~/docker/assign_manager/employee_list.csv:/app/employee_list.csv:ro   # 技師清單（只讀）
  - ~/docker/assign_manager/result.csv:/app/result.csv:ro                 # 工作清單（只讀）
```

### 掛載說明

1. **結果目錄**: 容器生成的所有結果檔案都會保存到 `~/docker/assign_manager/result/`
2. **輸入檔案**: 從Docker專用目錄讀取（只讀模式）
   - 啟動時會自動從項目根目錄同步到Docker專用目錄
3. **代碼同步**: 透過Docker建構時從GitHub拉取

## 🚀 優勢特點

### ✅ 隔離性
- 每個Docker項目都有獨立的專用目錄
- 避免不同容器間的文件混淆
- 清晰的目錄層次結構

### ✅ 可擴展性
```
~/docker/
├── assign_manager/           # 工作分配系統
│   └── result/
├── project_a/               # 其他項目A
│   └── data/
└── project_b/               # 其他項目B
    └── output/
```

### ✅ 持久性
- 容器刪除後，結果文件仍然保留
- 便於備份和管理
- 獨立於項目源代碼位置

## 🔧 使用方式

### 啟動服務
```bash
./docker/docker-start.sh start
```

### 查看狀態
```bash
./docker/docker-start.sh status
```

### 查看結果
```bash
ls -la ~/docker/assign_manager/result/
```

### 查看日誌
```bash
./docker/docker-start.sh logs
```

## 📊 目錄自動創建

腳本會自動創建必要的目錄結構：

1. **檢查目錄**: 檢查 `~/docker/assign_manager/` 是否存在
2. **創建目錄**: 如果不存在則自動創建
3. **創建子目錄**: 創建 `result/` 子目錄
4. **同步檔案**: 從項目根目錄同步 `employee_list.csv` 和 `result.csv`
5. **權限設置**: 確保正確的讀寫權限

## 🔍 狀態檢查

### 啟動時的日誌輸出
```
[INFO] 創建專用Docker目錄: /Users/username/docker/assign_manager...
[INFO] 創建result目錄: /Users/username/docker/assign_manager/result...
[INFO] 同步輸入檔案到Docker專用目錄...
[INFO] 同步 employee_list.csv...
[INFO] 同步 result.csv...
[INFO] 檔案同步完成
[SUCCESS] 目錄結構準備完成
[INFO] 項目根目錄: /path/to/project
[INFO] Docker專用目錄: /Users/username/docker/assign_manager
```

### 狀態檢查輸出
```
Docker專用目錄: /Users/username/docker/assign_manager
結果輸出目錄: /Users/username/docker/assign_manager/result
輸入檔案:
  - employee_list.csv: /Users/username/docker/assign_manager/employee_list.csv
  - result.csv: /Users/username/docker/assign_manager/result.csv
```

## 🎉 遷移說明

### 從舊配置遷移

如果你之前使用過舊的配置：

1. **自動處理**: 新版本會自動創建新的目錄結構
2. **舊文件**: 項目根目錄的 `result/` 仍然保留（供開發使用）
3. **新文件**: 容器輸出將保存到 `~/docker/assign_manager/result/`

### 檔案同步

如果需要將舊結果文件遷移到新位置：

```bash
# 備份舊結果（可選）
cp -r ./result/* ~/docker/assign_manager/result/

# 或者創建符號連結
ln -s ~/docker/assign_manager/result ./docker_result
```

## 🛠️ 故障排除

### 權限問題
```bash
# 檢查目錄權限
ls -la ~/docker/assign_manager/

# 修復權限（如果需要）
chmod 755 ~/docker/assign_manager/
chmod 755 ~/docker/assign_manager/result/
```

### 目錄不存在
```bash
# 手動創建目錄
mkdir -p ~/docker/assign_manager/result
```

### 清理舊配置
```bash
# 清理Docker資源（不會刪除結果文件）
./docker/docker-start.sh cleanup
```

---

現在你的Docker容器有了更好的目錄組織！所有結果都會保存到專用的 `~/docker/assign_manager/result/` 目錄中。🎯 