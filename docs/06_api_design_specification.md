# API 設計規範 - RespiraAlly v1

---

**文件版本 (Document Version):** `v1.1.0`
**最後更新 (Last Updated):** `2025-11-03`
**主要作者/設計師 (Lead Author/Designer):** `[技術負責人]`
**狀態 (Status):** `已批准 (Approved)`
**相關架構文件:** `[04_architecture_and_design_document.md](./04_architecture_and_design_document.md)`
**OpenAPI 定義文件:** `[openapi.yaml](/services/web-app/openapi.yaml)`

---

## 1. 引言 (Introduction)

### 1.1 目的 (Purpose)
為 RespiraAlly 後端服務 (`web-app`) 的消費者 (前端、LINE LIFF) 和實現者提供一個統一、明確的 RESTful API 接口契約。

### 1.2 快速入門 (Quick Start)

**治療師登入範例:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
-H "Content-Type: application/json" \
-d '{
  "account": "admin",
  "password": "admin"
}'
```

---

## 2. 設計原則與約定

*   **API 風格**: RESTful
*   **基本 URL**: `http://localhost:5000/api/v1` (開發), `https://your-domain.com/api/v1` (生產)
*   **請求與回應格式**: `application/json` (UTF-8)
*   **命名約定**: 
    *   資源路徑: 小寫，名詞複數 (e.g., `/patients`)
    *   JSON 欄位: `snake_case` (e.g., `user_id`, `record_date`)
*   **日期與時間格式**: ISO 8601 格式，UTC 時區 (e.g., `2025-11-03T10:00:00Z`)

---

## 3. 認證與授權

*   **認證機制**: JWT (JSON Web Token)。
*   **憑證傳遞**: 客戶端需在 `Authorization` header 中提供 `Bearer <access_token>`。
*   **Token 獲取**: 
    *   治療師: 透過 `POST /auth/login` 取得。
    *   病患: 透過 `POST /auth/line/login` 或 `POST /auth/line/register` 取得。
*   **權限模型**: 
    *   `@jwt_required()`: 任何登入的使用者。
    *   `@staff_required`: 僅限 `is_staff=true` 的使用者 (治療師/管理員)。
    *   `@admin_required`: 僅限 `is_admin=true` 的使用者 (管理員)。

---

## 4. 通用 API 行為

### 4.1 分頁 (Pagination)
*   **策略**: 基於頁碼 (Page-based) 的分頁。
*   **查詢參數**: `page` (預設 1) 和 `per_page` (預設 20)。
*   **回應結構**: 列表 API 的回應會包含一個 `pagination` 物件。
    ```json
    {
      "data": [ ... ],
      "pagination": {
        "total_items": 100,
        "total_pages": 5,
        "current_page": 1,
        "per_page": 20
      }
    }
    ```

### 4.2 排序 (Sorting)
*   **查詢參數**: `sort_by` 和 `order`。
*   **範例**: `GET /therapist/patients?sort_by=last_login&order=desc`

### 4.3 過濾 (Filtering)
*   **策略**: 直接使用欄位名作為查詢參數。
*   **範例**: `GET /therapist/patients?risk=high`

---

## 5. 錯誤處理

*   **標準錯誤回應格式**:
    ```json
    {
      "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "Patient with id 999 not found."
      }
    }
    ```
*   **通用 HTTP 狀態碼**: 
    *   `200 OK`, `201 Created`
    *   `400 Bad Request`: 請求格式錯誤。
    *   `401 Unauthorized`: Token 無效或未提供。
    *   `403 Forbidden`: 無權限訪問。
    *   `404 Not Found`: 資源不存在。
    *   `409 Conflict`: 資源衝突 (例如，重複提交當日日誌)。
    *   `500 Internal Server Error`: 伺服器內部錯誤。

---

## 6. API 端點詳述

### 6.1 資源群組：認證 (Authentication)

#### `POST /auth/login`
*   **描述**: 治療師使用帳號密碼登入。
*   **請求體**: `{ "account": "string", "password": "string" }`
*   **成功回應 (200 OK)**: 返回 `token`, `expires_in`, 和 `user` 物件。

#### `POST /auth/line/login`
*   **描述**: 已註冊病患使用 LINE User ID 登入。
*   **請求體**: `{ "lineUserId": "string" }`
*   **成功回應 (200 OK)**: 返回 `token`, `expires_in`, 和 `user` 物件。

#### `POST /auth/line/register`
*   **描述**: 新病患透過 LINE LIFF 註冊。
*   **請求體**: 包含 `lineUserId` 和病患基本資料。
*   **成功回應 (201 Created)**: 返回 `token`, `expires_in`, 和新建立的 `user` 物件。

### 6.2 資源群組：病患管理 (Patient Management)

#### `GET /therapist/patients`
*   **描述**: 獲取當前登入治療師所管理的所有病患列表。
*   **權限**: `@staff_required`
*   **查詢參數**: `page`, `per_page`, `risk`, `sort_by`, `order`。
*   **成功回應 (200 OK)**: 返回病患列表及分頁資訊。

#### `GET /patients/{patient_id}/profile`
*   **描述**: 獲取指定病患的詳細健康檔案。
*   **權限**: `@staff_required` (需為該病患的治療師)。
*   **成功回應 (200 OK)**: 返回 `Patient` 物件。

#### `GET /patients/{patient_id}/kpis`
*   **描述**: 獲取指定病患的關鍵績效指標 (KPIs)。
*   **權限**: `@staff_required` (需為該病患的治療師)。
*   **查詢參數**: `days` (計算天數)。
*   **成功回應 (200 OK)**: 返回 KPI 數據物件。

### 6.3 資源群組：健康數據與問卷 (Health Data & Questionnaires)

#### `GET /patients/{patient_id}/daily_metrics`
*   **描述**: 獲取病患的每日健康日誌。
*   **權限**: 治療師或病患本人。
*   **查詢參數**: `start_date`, `end_date`, `page`, `per_page`。
*   **成功回應 (200 OK)**: 返回 `DailyMetric` 列表及分頁資訊。

#### `POST /patients/{patient_id}/daily_metrics`
*   **描述**: 新增一筆當日的健康日誌。
*   **權限**: 病患本人。
*   **請求體**: `{ "water_cc": integer, "medication": boolean, ... }`
*   **成功回應 (201 Created)**: 返回新建立的 `DailyMetric` 物件。

#### `POST /patients/{patient_id}/questionnaires/cat`
*   **描述**: 提交一份新的 CAT 問卷 (每月一次)。
*   **權限**: 病患本人。
*   **請求體**: 包含 `record_date` 及 8 個問題的分數。
*   **成功回應 (201 Created)**: 返回包含 `record_id` 和 `total_score` 的物件。

*(MMRC 問卷有類似的 `GET` 和 `POST` 端點)*

### 6.4 資源群組：語音互動 (Voice Interaction)

#### `POST /voice/chat`
*   **描述**: 處理一個完整的語音互動流程。
*   **請求 (multipart/form-data)**: `audio` (音檔), `patient_id`, `conversation_id`。
*   **成功回應 (200 OK)**: 返回 `user_transcription`, `ai_response_text`, `ai_audio_url` 等資訊。

#### `POST /audio/request-url`
*   **描述**: 請求一個預簽名的 URL，用於將大型音檔直接上傳到物件儲存。
*   **請求體**: `{ "filename": "string" }`
*   **成功回應 (200 OK)**: 返回 `url` 和 `object_name`。

### 6.5 資源群組：儀表板總覽 (Dashboard Overview)

#### `GET /overview/kpis`
*   **描述**: 獲取治療師所管理群體的總體 KPIs。
*   **權限**: `@staff_required`
*   **成功回應 (200 OK)**: 返回如 `total_patients`, `high_risk_patients` 等數據。

---

## 7. 資料模型/Schema 定義 (節錄)

### 7.1 `Patient` (Summary in List)
```json
{
  "user_id": "integer",
  "first_name": "string",
  "last_name": "string",
  "risk_level": "string",
  "last_cat_score": "integer",
  "last_mmrc_score": "integer"
}
```

### 7.2 `DailyMetric`
```json
{
  "log_id": "integer",
  "created_at": "string (date-time)",
  "water_cc": "integer",
  "medication": "boolean",
  "exercise_min": "integer",
  "cigarettes": "integer"
}
```

### 7.3 `CATQuestionnaire`
```json
{
  "record_id": "integer",
  "record_date": "string (date)",
  "total_score": "integer",
  "scores": { ... }
}
```

---

## 8. API 版本控制

*   **策略**: URL 路徑版本控制 (`/v1`)。
*   **破壞性變更 (Breaking change)**: 任何會破壞現有客戶端整合的變更 (如刪除欄位、修改型別) 都必須在新的主版本 (`/v2`) 中進行。
*   **向後兼容變更 (Backward-compatible)**: 新增端點、新增可選參數、在回應中新增欄位，均視為向後兼容，不需變更版本。
