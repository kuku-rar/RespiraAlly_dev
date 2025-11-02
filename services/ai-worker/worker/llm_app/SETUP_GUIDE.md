# Beloved Grandson LLM App - 長期追蹤健康陪伴機器人

## 🌟 功能特色

### 核心功能
- **智能對話**：台語風格的溫暖陪伴
- **風險檢查**：自動偵測危險內容並攔截
- **知識搜尋**：從 COPD 資料庫搜尋專業資訊
- **個管師通報**：緊急情況自動通報

### 🆕 長期追蹤功能
- **長期記憶管理**：基於 Milvus 的向量記憶系統
- **會話摘要**：自動生成分段和全量摘要
- **記憶檢索**：根據當前輸入智能搜索相關記憶
- **會話終結處理**：閒置超時自動整理記憶
- **用戶狀態管理**：跨會話的長期追蹤

## 🚀 快速啟動

### 1. 環境配置

複製配置模板：
```bash
cp config_template.env .env
```

編輯 `.env` 文件，配置必要參數：
```env
# OpenAI API
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MODEL_NAME=gpt-4o-mini

# Milvus 向量資料庫
MILVUS_URI=http://localhost:19530

# Redis 資料庫
REDIS_URL=redis://localhost:6379/0

# 長期記憶配置
MEM_COLLECTION=user_memory
MEM_THRESHOLD=0.80
```

### 2. 啟動基礎服務

```bash
# 啟動 Milvus 和 Redis
docker-compose up -d milvus redis
```

### 3. 載入 COPD 知識庫

```bash
python load_article.py
```

### 4. 運行方式

#### 方式一：測試 LLM Service
```bash
python llm_service.py
```

#### 方式二：完整 AI Worker（生產環境）
```bash
python ../main.py
```

## 📊 記憶管理工具

### 查看用戶記憶
```bash
python view_memory_collection.py
```

### 清空記憶集合
```bash
python clear_memory_collection.py
```

## 🔧 長期追蹤功能詳解

### 記憶管理系統
- **向量存儲**：每個用戶的對話摘要存為向量
- **智能檢索**：根據當前輸入自動搜索相關記憶
- **自動修剪**：保持每用戶最新 30 筆記錄

### 會話摘要流程
1. **分段摘要**：每 5 輪對話自動生成摘要
2. **全量 Refine**：會話結束時整合所有歷史
3. **記憶存儲**：將精煉摘要存入長期記憶

### 會話生命週期
```
啟動 → 對話 → 分段摘要 → 閒置檢測 → 會話結束 → Refine → 記憶存儲
```

## 🎯 使用範例

### 測試流程
```bash
$ python llm_service.py

===== 第 1 輪 測試開始 =====
用戶輸入: 我最近常常咳嗽，該注意什麼？
AI 回應: 阿公，咳嗽真的很不舒服呢...
===== 第 1 輪 測試結束 =====

===== 第 2 輪 測試開始 =====
用戶輸入: 最近心情不好，睡也睡不好，該怎樣調整？
AI 回應: ⭐ 追蹤重點：持續咳嗽症狀需關注
阿公，心情和睡眠確實很重要...
===== 第 2 輪 測試結束 =====
```

### 長期追蹤效果
```
第一次對話：
長輩：我最近咳嗽很厲害
金孫：阿公，咳嗽真的很不舒服...

[會話結束，生成記憶：持續咳嗽症狀]

第二次對話：
長輩：我又開始咳了
金孫：⭐ 追蹤重點：持續咳嗽症狀
阿公，上次您也提到咳嗽問題...
```

### 會話管理
- **活動追蹤**：自動記錄最後活動時間
- **超時處理**：5分鐘無活動自動收尾
- **資源清理**：確保 Agent 和記憶正確釋放

## 🛠️ 故障排除

### 常見問題

1. **Milvus 連接失敗**
   ```bash
   docker-compose ps milvus
   docker-compose logs milvus
   ```

2. **記憶檢索無效果**
   - 檢查 `MEM_THRESHOLD` 設置（推薦 0.80）
   - 確認向量維度 `MEM_DIM` 正確

3. **會話無法結束**
   - 檢查 Redis 連接
   - 確認 `set_state_if` 功能正常

### 環境變數說明

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| `MEM_COLLECTION` | Milvus 記憶集合名 | `user_memory` |
| `MEM_THRESHOLD` | 記憶檢索相似度閾值 | `0.80` |
| `STM_MAX_CHARS` | 短期記憶最大字數 | `1800` |
| `SUMMARY_MAX_CHARS` | 摘要最大字數 | `3000` |
| `REFINE_CHUNK_ROUNDS` | Refine 每塊輪數 | `20` |

## 🔍 系統架構

```
User Input
    ↓
Chat Pipeline (新增 UserSession)
    ├─ Guardrail Agent
    ├─ Health Agent
    └─ Memory Retrieval (新增)
    ↓
Response + Memory Update (新增)
    ↓
Session Management (新增)
    ├─ Activity Tracking
    ├─ Timeout Detection
    └─ Finalization
```

## 📈 效能優化

### 記憶系統
- **向量索引**：HNSW 算法，M=16, efConstruction=200
- **查詢優化**：COSINE 距離，ef=64
- **記憶修剪**：每次插入後自動清理舊記錄

### 會話管理
- **非阻塞**：使用後台線程處理超時
- **原子操作**：CAS 語義確保狀態一致性
- **優雅降級**：CrewAI 失敗時自動 fallback

## 🔒 安全性

- **記憶隔離**：每用戶獨立記憶空間
- **資料清理**：會話結束自動清理敏感資料
- **錯誤恢復**：記憶操作失敗不影響對話

立即體驗完整的長期追蹤健康陪伴功能！🎉
