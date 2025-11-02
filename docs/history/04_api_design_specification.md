# **API 設計規格 (API Design Specification)**
- **專案名稱**: 健康陪跑台語語音機器人
- **版本**: 1.1
- **日期**: 2025-07-28
- **作者**: 後端團隊
- **關聯架構**: `02_system_architecture_document.md`

---

## 1. 總覽 (Overview)

本文件詳細定義了「健康陪跑台語語音機器人」專案後端服務所提供的所有 API 端點。這是前端與後端團隊之間進行開發協作的核心契約。

### 1.1. 通用約定 (General Conventions)

- **基礎路徑 (Base Path)**: 所有 API 的基礎路徑為 `/api/v1`。
- **認證 (Authentication)**:
    - 除公開端點（如登入、註冊）外，所有需要授權的請求都必須在 HTTP Header 中包含 `Authorization` 欄位。
    - 格式為 `Authorization: Bearer <JWT_TOKEN>`。
- **請求格式 (Request Format)**: 所有 `POST`, `PUT`, `PATCH` 請求的 Body 均使用 `application/json` 格式。
- **回應格式 (Response Format)**: 所有 API 的回應 Body 均使用 `application/json` 格式。
- **日期與時間**: 所有日期時間格式均採用 `ISO 8601` 標準 (例如: `2025-07-28T12:30:00Z`)。

### 1.2. 標準錯誤回應 (Standard Error Response)

當 API 呼叫發生錯誤時，回應 Body 將包含以下結構：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "A human-readable error message."
  }
}
```

| HTTP 狀態碼 | `ERROR_CODE` 範例 | 說明 |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_INPUT`, `BAD_REQUEST` | 客戶端傳送的請求參數格式錯誤或缺失。 |
| `401 Unauthorized` | `UNAUTHENTICATED` | 未提供 Token 或 Token 無效/過期。 |
| `403 Forbidden` | `PERMISSION_DENIED` | 使用者已認證，但無權限執行此操作。 |
| `404 Not Found` | `RESOURCE_NOT_FOUND`, `USER_NOT_FOUND` | 請求的資源不存在。 |
| `409 Conflict` | `CONFLICT`, `USER_ALREADY_EXISTS` | 請求的操作與伺服器當前狀態衝突 (如資源已存在)。 |
| `500 Internal Server Error` | `INTERNAL_SERVER_ERROR` | 伺服器內部發生未預期的錯誤。 |

---

## 2. API 端點詳解

### **模組一：認證 (Authentication)**

---

### **1.1. 呼吸治療師登入**

- **端點**: `POST /auth/login`
- **說明**: 供呼吸治療師使用帳號密碼進行登入。
- **認證**: 無 (公開端點)。

**請求 Body:**

```json
{
  "account": "admin",
  "password": "admin"
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `account` | string | 是 | 使用者的登入帳號。 |
| `password` | string | 是 | 使用者的登入密碼。 |

**成功回應 (200 OK):**

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600.0,
    "user": {
      "id": 1,
      "account": "admin",
      "first_name": "大仁",
      "last_name": "陳",
      "title": "呼吸治療師"
    }
  }
}
```

**失敗回應:**

- `400 Bad Request`: 請求格式錯誤或缺少欄位。
- `401 Unauthorized`: 當帳號或密碼錯誤時。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

### **1.2. 患者 LIFF 登入**

- **端點**: `POST /auth/line/login`
- **說明**: 供**已註冊**的患者在 LIFF 環境中，使用 `lineUserId` 進行登入。
- **認證**: 無 (公開端點)。

**請求 Body:**

```json
{
  "lineUserId": "U123456789abcdef123456789abcdef"
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `lineUserId` | string | 是 | 從 LINE SDK (`liff.getProfile()`) 獲取的唯一使用者 ID。 |

**成功回應 (200 OK):**

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 604800.0,
    "user": {
      "id": 2,
      "line_user_id": "U123456789abcdef123456789abcdef",
      "first_name": "淑芬",
      "last_name": "林",
      "health_profile": {
        "height_cm": 160,
        "weight_kg": 55,
        "smoke_status": "never"
      }
    }
  }
}
```

**失敗回應:**

- `400 Bad Request`: 當 `lineUserId` 缺失時。
- `404 Not Found`: 當 `lineUserId` 尚未註冊時。

---

### **1.3. 患者 LIFF 註冊**

- **端點**: `POST /auth/line/register`
- **說明**: 供新患者在 LIFF 環境中，使用 `lineUserId` 並填寫基本資料以完成註冊。
- **認證**: 無 (公開端點)。

**請求 Body:**

```json
{
  "lineUserId": "U_new_user_abcdef123456",
  "first_name": "美麗",
  "last_name": "陳",
  "gender": "female",
  "phone": "0987654321",
  "height_cm": 160,
  "weight_kg": 55,
  "smoke_status": "never"
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `lineUserId` | string | 是 | 從 LINE SDK 獲取的唯一使用者 ID。 |
| `first_name` | string | 是 | 名字。 |
| `last_name` | string | 是 | 姓氏。 |
| `gender` | string | 否 | 性別 (e.g., 'male', 'female', 'other')。 |
| `phone` | string | 否 | 聯絡電話。 |
| `height_cm` | integer | 否 | 身高 (公分)。 |
| `weight_kg` | integer | 否 | 體重 (公斤)。 |
| `smoke_status`| string | 否 | 抽菸狀況 (e.g., 'never', 'quit', 'current')。 |

**成功回應 (201 Created):**

*註冊成功後，系統會自動為使用者登入並發放 Token。*
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 604800.0,
    "user": {
      "id": 3,
      "line_user_id": "U_new_user_abcdef123456",
      "first_name": "美麗",
      "last_name": "陳"
    }
  }
}
```
***註**: 作為成功註冊的後續動作，系統後端會觸發一個非同步任務，將該使用者的 LINE 圖文選單更換為「會員專屬選單」。*

**失敗回應:**

- `400 Bad Request`: 缺少必要欄位。
- `409 Conflict`: 該 `lineUserId` 已經被註冊。

---

### **模組二：使用者與病患管理 (Users & Patients)**

---

### **2.1. 獲取管理的病患列表**

- **端點**: `GET /therapist/patients`
- **說明**: 獲取當前登入的呼吸治療師所管理的所有病患的簡要列表。
- **認證**: 必要 (Bearer Token)。

**請求參數 (Query Parameters):**

| 參數 | 類型 | 必要 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | integer | 否 | `1` | 頁碼。 |
| `per_page` | integer | 否 | `20` | 每頁數量。 |
| `sort_by` | string | 否 | `created_at` | 排序欄位。 |
| `order` | string | 否 | `desc` | 排序順序 (`asc` 或 `desc`)。 |

**成功回應 (200 OK):**

```json
{
  "data": [
    {
      "user_id": 2,
      "first_name": "淑芬",
      "last_name": "林",
      "gender": "female",
      "last_login": "2025-07-27T10:00:00Z",
      "last_cat_score": null,
      "last_mmrc_score": null
    }
  ],
  "pagination": {
    "total_items": 1,
    "total_pages": 1,
    "current_page": 1,
    "per_page": 20
  }
}
```
*註: `last_cat_score` 和 `last_mmrc_score` 為未來擴充欄位。*

**失敗回應:**

- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: Token 有效，但該使用者不是呼吸治療師 (`is_staff` 為 false)。

---

### **2.2. 獲取病患詳細健康檔案**

- **端點**: `GET /patients/{patient_id}/profile`
- **說明**: 獲取指定病患的詳細健康檔案資訊。
- **認證**: 必要 (Bearer Token)。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `patient_id` | integer | 病患的 `user_id`。 |

**成功回應 (200 OK):**

```json
{
  "data": {
    "user_id": 2,
    "first_name": "淑芬",
    "last_name": "林",
    "gender": "female",
    "email": null,
    "phone": "0912345678",
    "health_profile": {
      "height_cm": 155,
      "weight_kg": 60,
      "smoke_status": "quit",
      "updated_at": "2025-07-26T15:00:00Z"
    }
  }
}
```

**失敗回應:**

- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: 當前治療師無權限查看此病患的檔案。
- `404 Not Found`: 找不到具有指定 `patient_id` 的病患。

---

### **2.3. 建立新使用者 (管理員專用)**

- **端點**: `POST /users`
- **說明**: 供**管理員**建立新的使用者帳號（例如：呼吸治療師或其他管理員）。
- **認證**: 必要 (Bearer Token)。後端必須校驗發起請求的使用者是否具有 `is_admin: true` 權限。

**請求 Body:**

```json
{
  "account": "new_therapist_01",
  "password": "a_very_strong_password",
  "first_name": "思敏",
  "last_name": "王",
  "email": "sumin.wang@example.com",
  "is_staff": true,
  "is_admin": false,
  "title": "呼吸治療師"
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `account` | string | 是 | 新使用者的登入帳號。 |
| `password` | string | 是 | 新使用者的登入密碼。 |
| `first_name`| string | 否 | 名字。 |
| `last_name` | string | 否 | 姓氏。 |
| `email` | string | 否 | 電子郵件，必須唯一。 |
| `is_staff` | boolean | 是 | 是否為員工 (如治療師)。 |
| `is_admin` | boolean | 是 | 是否為管理員。 |
| `title` | string | 否 | 職稱。如果 `is_staff` 為 true，建議提供此欄位。 |


**成功回應 (201 Created):**

```json
{
  "data": {
    "id": 4,
    "account": "new_therapist_01",
    "first_name": "思敏",
    "last_name": "王",
    "email": "sumin.wang@example.com",
    "is_staff": true,
    "is_admin": false,
    "created_at": "2025-07-28T10:00:00Z"
  }
}
```

**失敗回應:**

- `400 Bad Request`: 請求 Body 的資料格式錯誤或缺少必要欄位。
- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: 當前使用者不是管理員。
- `409 Conflict`: `account` 已存在。

---

### **模組三：健康數據與問卷 (Health Data & Questionnaires)**

---

### **3.1. 獲取每日健康日誌**

- **端點**: `GET /patients/{patient_id}/daily_metrics`
- **說明**: 獲取指定病患在特定日期範圍內的每日健康日誌記錄。
- **認證**: 必要 (Bearer Token)。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `patient_id` | integer | 病患的 `user_id`。 |

**請求參數 (Query Parameters):**

| 參數 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `start_date` | string | 否 | 查詢起始日期，格式 `YYYY-MM-DD`。 |
| `end_date` | string | 否 | 查詢結束日期，格式 `YYYY-MM-DD`。 |
| `page` | integer | 否 | 頁碼，預設為 `1`。 |
| `per_page` | integer | 否 | 每頁數量，預設為 `30`。 |

**成功回應 (200 OK):**

```json
{
  "data": [
    {
      "log_id": 1,
      "created_at": "2025-07-28T09:00:00Z",
      "water_cc": 2000,
      "medication": true,
      "exercise_min": 30,
      "cigarettes": 0
    }
  ],
  "pagination": {
    "total_items": 1,
    "total_pages": 1,
    "current_page": 1,
    "per_page": 30
  }
}
```

**失敗回應:**

- `400 Bad Request`: 日期格式錯誤或 `start_date` 晚於 `end_date`。
- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: 無權限查看此病患的日誌。
- `404 Not Found`: 找不到該病患。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

### **3.2. 新增每日健康日誌**

- **端點**: `POST /patients/{patient_id}/daily_metrics`
- **說明**: 供 LIFF 前端為指定病患新增一筆當日的健康日誌。
- **認證**: 必要 (Bearer Token)。後端需校驗 Token 中的 `user_id` 是否與 URL 中的 `patient_id` 一致。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `patient_id` | integer | 病患的 `user_id`。 |

**請求 Body:**

```json
{
  "water_cc": 2000,
  "medication": true,
  "exercise_min": 30,
  "cigarettes": 0
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `water_cc` | integer | 否 | 當日喝水量 (cc)。 |
| `medication` | boolean | 否 | 是否服藥。 |
| `exercise_min` | integer | 否 | 當日運動分鐘數。 |
| `cigarettes` | integer | 否 | 當日抽菸支數。 |

**成功回應 (201 Created):**

```json
{
  "data": {
    "log_id": 2,
    "created_at": "2025-07-28T11:00:00Z",
    "water_cc": 2000,
    "medication": true,
    "exercise_min": 30,
    "cigarettes": 0
  }
}
```

**失敗回應:**

- `400 Bad Request`: 請求 Body 的資料格式錯誤。
- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: 試圖為其他病患新增日誌。
- `404 Not Found`: 找不到具有指定 `patient_id` 的病患。
- `409 Conflict`: 當日已經存在一筆日誌記錄。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

### **3.3. 更新每日健康日誌**

- **端點**: `PUT /patients/{patient_id}/daily_metrics/{log_date}`
- **說明**: 供 LIFF 前端更新指定日期的健康日誌。
- **認證**: 必要 (Bearer Token)。後端需校驗 Token 中的 `user_id` 是否與 URL 中的 `patient_id` 一致。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `patient_id` | integer | 病患的 `user_id`。 |
| `log_date` | string | 要更新的日誌日期，格式 `YYYY-MM-DD`。 |

**請求 Body:**

```json
{
  "water_cc": 2200,
  "medication": true,
  "exercise_min": 20,
  "cigarettes": 1
}
```

**成功回應 (200 OK):**

```json
{
  "data": {
    "log_id": 1,
    "created_at": "2025-07-28T09:00:00Z",
    "water_cc": 2200,
    "medication": true,
    "exercise_min": 20,
    "cigarettes": 1
  }
}
```

**失敗回應:**

- `400 Bad Request`: 請求 Body 的資料格式或日期格式錯誤。
- `401 Unauthorized`: Token 無效或未提供。
- `403 Forbidden`: 試圖為其他病患更新日誌。
- `404 Not Found`: 找不到指定日期的日誌記錄。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

### **3.4. 問卷相關 API (CAT & MMRC)**

*此處省略 CAT 與 MMRC 的 GET, POST, PUT 端點的詳細規格，因其與程式碼高度一致，未發現明顯差異。其行為模式與每日健康日誌類似。*

---

### **模組四：對話與 AI 互動 (Chat & AI Interaction)**

---

### **4.1. 請求音檔上傳 URL**

- **端點**: `POST /audio/request-url`
- **說明**: 向伺服器請求一個有時效性的 URL，供客戶端直接將音檔上傳至 MinIO 物件儲存。
- **認證**: 無。

**請求 Body:**

```json
{
  "filename": "my-awesome-speech.m4a"
}
```

| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `filename` | string | 否 | 可選的檔案名稱。如果未提供，伺服器將生成一個唯一的名稱。 |

**成功回應 (200 OK):**

```json
{
    "url": "http://localhost:9000/audio-uploads/generated-unique-name.m4a?...",
    "object_name": "generated-unique-name.m4a"
}
```

**失敗回應:**

- `500 Internal Server Error`: 伺服器無法生成 URL。

---

### **4.2. 提交文字對話任務**
- **端點**: `POST /chat/text`
- **說明**: 供前端發起一個純文字的對話任務。後端會接收請求，將任務放入 RabbitMQ 佇列後立即返回，表示任務已接受。
- **認證**: 必要 (Bearer Token)。

**請求 Body:**
```json
{
  "patient_id": "2",
  "text": "我今天覺得有點喘"
}
```
| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `patient_id` | string | 是 | 發起對話的病患 ID。 |
| `text` | string | 是 | 使用者輸入的文字內容。 |

**成功回應 (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Message received and queued for processing."
}
```

**失敗回應:**
- `400 Bad Request`: 缺少 `patient_id` 或 `text`。
- `500 Internal Server Error`: 無法將訊息發布到佇列。

---

### **4.3. 提交語音對話任務**
- **端點**: `POST /chat/audio`
- **說明**: 在前端透過 `4.1` 的 URL 將音檔上傳至 MinIO 後，呼叫此 API 以觸發後續的非同步處理流程 (STT -> LLM -> TTS)。
- **認證**: 必要 (Bearer Token)。

**請求 Body:**
```json
{
  "patient_id": "2",
  "filename": "generated-unique-name.m4a"
}
```
| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `patient_id` | string | 是 | 發起對話的病患 ID。 |
| `filename` | string | 是 | 已上傳至 MinIO 的音檔 `object_name`。 |

**成功回應 (202 Accepted):**
```json
{
  "status": "accepted",
  "data": {
    "patient_id": "2",
    "object_name": "generated-unique-name.m4a",
    "bucket_name": "audio-uploads"
  }
}
```

**失敗回應:**
- `400 Bad Request`: 缺少 `patient_id` 或 `filename`。
- `500 Internal Server Error`: 無法將訊息發布到佇列。

---

### **4.4. 獲取對話列表**

- **端點**: `GET /patients/{patient_id}/conversations`
- **說明**: 獲取指定病患的所有對話列表 (每個列表項代表一次完整的對話會期)。
- **認證**: 必要 (Bearer Token)。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `patient_id` | integer | 病患的 `user_id`。 |

**成功回應 (200 OK):**

```json
[
    {
        "_id": "66a5d4a5b6c7d8e9f0a1b2c3",
        "patient_id": 2,
        "start_time": "2025-07-28T08:00:00Z",
        "summary": "使用者回報呼吸困難，AI建議休息並監測。"
    }
]
```

**失敗回應:**

- `404 Not Found`: 找不到該病患。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

### **4.5. 獲取單次對話的所有訊息**

- **端點**: `GET /conversations/{conversation_id}/messages`
- **說明**: 根據對話 ID，獲取該次對話中的所有訊息。
- **認證**: 必要 (Bearer Token)。

**URL 參數:**

| 參數 | 類型 | 說明 |
| :--- | :--- | :--- |
| `conversation_id` | string | 對話的 ID (`_id`)。 |

**成功回應 (200 OK):**

```json
[
    {
        "_id": "msg_1",
        "conversation_id": "66a5d4a5b6c7d8e9f0a1b2c3",
        "sender_type": "user",
        "content": "我今天覺得有點喘",
        "timestamp": "2025-07-28T08:00:00Z"
    },
    {
        "_id": "msg_2",
        "conversation_id": "66a5d4a5b6c7d8e9f0a1b2c3",
        "sender_type": "ai",
        "content": "這樣要多休息喔，有量血壓嗎？",
        "timestamp": "2025-07-28T08:00:05Z"
    }
]
```

**失敗回應:**

- `404 Not Found`: 找不到該對話。
- `500 Internal Server Error`: 伺服器內部錯誤。

---

## 5. 內部微服務 API (Internal Microservice APIs)

---

本章節定義服務內部 `ai-worker` 與各 AI 微服務 (`stt-service`, `llm-service`, `tts-service`) 之間的通訊契約。這些 API 不對外公開，僅在 Docker 內部網路中互相呼叫。

---

### **5.1. STT Service (Speech-to-Text)**

- **端點**: `POST /api/v1/transcribe`
- **服務**: `stt-service`
- **說明**: 接收音檔，回傳辨識後的文字。
- **請求格式**: `multipart/form-data`

**請求 Form-Data:**
| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `audio_file` | file | 是 | 待辨識的音檔。 |

**成功回應 (200 OK):**
```json
{
  "filename": "audio.wav",
  "transcribed_text": "這是辨識出來的文字"
}
```

**失敗回應:**
- `422 Unprocessable Entity`: 未提供 `audio_file` 檔案。

---

### **5.2. LLM Service (Large Language Model)**

- **端點**: `POST /api/v1/chat`
- **服務**: `llm-service`
- **說明**: 接收文字，回傳 AI 生成的回應。
- **請求格式**: `application/json`

**請求 Body:**
```json
{
  "text": "使用者輸入的最新文字"
}
```
| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `text` | string | 是 | 使用者輸入的文字內容。 |

**成功回應 (200 OK):**
```json
{
  "message": "這是由 LLM 生成的回應文本"
}
```

**失敗回應:**
- `422 Unprocessable Entity`: 請求 Body 中缺少 `text` 欄位。

---

### **5.3. TTS Service (Text-to-Speech)**

- **端點**: `POST /api/v1/synthesize`
- **服務**: `tts-service`
- **說明**: 接收文字，回傳合成後的語音。*注意：目前實作僅返回成功訊息，並未實際生成音檔。*
- **請求格式**: `application/json`

**請求 Body:**
```json
{
  "text": "這是要被轉換成語音的文字"
}
```
| 欄位 | 類型 | 必要 | 說明 |
| :--- | :--- | :--- | :--- |
| `text` | string | 是 | 要合成語音的文字。 |

**成功回應 (200 OK):**
```json
{
  "message": "Synthesize endpoint is working"
}
```
*註：在完整實作中，此端點應回傳 `audio/mpeg` 或 `audio/wav` 類型的音檔數據。*

**失敗回應:**
- `400 Bad Request`: 請求 Body 中缺少 `text` 欄位。

---
