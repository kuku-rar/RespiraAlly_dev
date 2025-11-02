# 整合性架構與設計文件 - RespiraAlly

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-11-03`
**主要作者 (Lead Author):** `[技術架構師]`
**審核者 (Reviewers):** `[核心開發團隊]`
**狀態 (Status):** `已批准 (Approved)`

---

## 目錄 (Table of Contents)

- [第 1 部分：架構總覽 (Architecture Overview)](#第-1-部分架構總覽-architecture-overview)
- [第 2 部分：詳細設計 (Detailed Design)](#第-2-部分詳細設計-detailed-design)

---

**目的**: 本文件旨在將 RespiraAlly 的業務需求轉化為一個完整、內聚的技術藍圖。它從高層次的系統架構開始，逐步深入到具體的模組級實現細節，確保系統的穩固性與可維護性。

---

## 第 1 部分：架構總覽 (Architecture Overview)

*此部分關注系統的宏觀結構與指導原則，回答「系統由什麼組成？」以及「它們之間如何互動？」。*

### 1.1 系統架構圖 (System Architecture Diagram)

本專案採用微服務架構，確保關注點分離、可擴展性與可維護性。

```mermaid
graph TD
    subgraph "User Domain"
        User[<font size="4"><b>User</b></font><br/>(病患/治療師)]
    end

    subgraph "Public Network"
        User -- HTTPS --> Nginx
    end

    subgraph "Core Services"
        Nginx[<font size="4"><b>Nginx</b></font><br/>Reverse Proxy]
        Frontend[<font size="4"><b>Frontend</b></font><br/>(React UI for Therapist)]
        WebApp[<font size="4"><b>Web App</b></font><br/>(Flask API)]
    end

    subgraph "AI & Worker Services"
        AIWorker[<font size="4"><b>AI Worker</b></font><br/>(Python Async Tasks)]
        RabbitMQ[<font size="4"><b>RabbitMQ</b></font><br/>Message Queue]
    end

    subgraph "Data & Storage Layer"
        Postgres[<font size="4"><b>PostgreSQL</b></font><br/>Primary DB]
        Redis[<font size="4"><b>Redis</b></font><br/>Cache]
        MinIO[<font size="4"><b>MinIO</b></font><br/>Object Storage]
        Milvus[<font size="4"><b>Milvus</b></font><br/>Vector DB]
    end
    
    subgraph "External Services"
        LineAPI[<font size="4"><b>LINE API</b></font>]
        LLM_Service[<font size="4"><b>OpenAI/Google AI</b></font>]
    end

    %% Connections
    Nginx -- Serves UI --> Frontend
    Nginx -- /api routes --> WebApp

    User -- Interacts with --> Frontend
    User -- Interacts with LIFF via --> LineAPI
    LineAPI -- Webhook/Login --> WebApp

    Frontend -- REST API Calls --> WebApp
    
    WebApp -- Reads/Writes --> Postgres
    WebApp -- Caches data in --> Redis
    WebApp -- Publishes tasks --> RabbitMQ
    WebApp -- Manages files in --> MinIO

    AIWorker -- Consumes tasks from --> RabbitMQ
    AIWorker -- Reads/Writes --> Postgres
    AIWorker -- Accesses files in --> MinIO
    AIWorker -- Calls --> LLM_Service
    AIWorker -- Vector search/store --> Milvus
```

### 1.2 技術選型與決策 (Technology Stack & Decisions)

*   **技術棧 (Tech Stack):**
    *   **前端**: React, Vite, Ant Design
    *   **後端 (Web App)**: Python, Flask, SQLAlchemy
    *   **AI Worker**: Python, Pika (for RabbitMQ), Transformers, PyTorch
    *   **資料庫**: PostgreSQL (主要業務), Redis (快取), MinIO (物件儲存), Milvus (向量儲存)
    *   **訊息佇列**: RabbitMQ
    *   **容器化**: Docker, Docker Compose
    *   **反向代理**: Nginx

*   **架構決策記錄 (ADR):**
    *   **ADR-001**: 選擇微服務架構，將 `web-app` (同步 API) 與 `ai-worker` (非同步任務) 分離，以提高系統的回應速度和容錯能力。
    *   **ADR-002**: 採用 RabbitMQ 作為訊息佇列，以實現服務間的解耦和可靠的非同步通訊。
    *   **ADR-003**: 使用 MinIO 進行檔案儲存，以支援 S3 相容的 API，並簡化本地開發設定。
    *   **ADR-004**: 引入 Milvus 作為向量資料庫，為 RAG (檢索增強生成) 提供高效的語義搜索能力。

---

## 第 2 部分：詳細設計 (Detailed Design)

*此部分關注具體模組的實現細節，回答「每個部分如何工作？」。*

### 2.1 MVP 與模組優先級 (MVP & Module Priority)

根據 PRD，開發計畫分為兩個階段：

*   **第一階段 - 核心 MVP (Text-First):**
    *   **病患模組**: `web-app` 需實現病患註冊、登入、健康日誌與問卷提交的 API。
    *   **治療師模組**: `frontend` 需實現儀表板，`web-app` 提供對應的病患列表與數據 API。
    *   **AI 助理模組 (文字版)**: `web-app` 需整合 LINE Webhook，接收文字訊息並將任務發布到 RabbitMQ；`ai-worker` 實現 LLM+RAG 的純文字處理邏輯。

*   **第二階段 - 完整 MVP (Voice-Enabled):**
    *   **語音處理模組**: `ai-worker` 需整合 STT 與 TTS 服務。`web-app` 新增處理音檔上傳的 API。

### 2.2 核心功能：模組設計

#### 模組: `Nginx` (反向代理)
*   **職責**:
    *   作為所有傳入 HTTP 流量的單一入口點。
    *   將請求路由到適當的服務 (`frontend` 或 `web-app`)。
    *   處理 SSL 憑證終止。
    *   可在生產環境中配置負載平衡。

#### 模組: `frontend` (React 治療師儀表板)
*   **職責**:
    *   為治療師提供豐富、互動式的使用者介面。
    *   透過 REST API 與 `web-app` 進行通訊。
    *   處理使用者身份驗證和資料顯示。
*   **核心元件**:
    *   `src/pages/`: 頁面級元件 (e.g., `DashboardPage`, `PatientDetailPage`)。
    *   `src/shared/api/`: 封裝所有對後端 API 的呼叫。
    *   `src/shared/components/`: 可重用的 UI 元件 (e.g., 圖表、列表)。

#### 模組: `web-app` (Flask API 服務)
*   **職責**:
    *   為前端和外部服務 (如 LINE Webhook) 提供 REST API。
    *   管理業務邏輯、使用者資料和身份驗證。
    *   與 `PostgreSQL` 資料庫互動以進行持久化儲存。
    *   使用 `Redis` 進行快取和會話管理。
    *   將長時間執行的非同步任務 (如音訊處理) 發布到 `RabbitMQ`。
*   **核心元件**:
    *   `app/api/`: RESTful API 端點定義，按資源劃分 (e.g., `patients.py`, `auth.py`)。
    *   `app/core/`: 核心服務與倉儲層 (e.g., `patient_service.py`, `daily_metric_repository.py`)。
    *   `app/models/`: SQLAlchemy 資料庫模型定義。

#### 模組: `ai-worker` (Python 背景任務服務)
*   **職責**:
    *   從 `RabbitMQ` 佇列中消費任務。
    *   執行語音轉文字 (STT) 和文字轉語音 (TTS) 的轉換。
    *   與外部 AI 服務 (如 OpenAI, Google AI) 互動以進行語言模型處理。
    *   利用 `Milvus` 進行向量嵌入儲存和檢索 (RAG)。
    *   從 `MinIO` 物件儲存中儲存和檢索音訊檔案。
*   **核心元件**:
    *   `worker/main.py`: 監聽 RabbitMQ 佇列，根據任務類型分派處理器。
    *   `worker/llm_app/`: 處理與大型語言模型互動的邏輯，包含 RAG。
    *   `worker/stt_app/` & `worker/tts_app/`: (第二階段) 分別處理語音轉文字和文字轉語音的服務。

### 2.3 資料與儲存層 (Data & Storage Layer)

*   **PostgreSQL**: 主要的關聯式資料庫，用於儲存結構化資料，如使用者設定檔、訊息和指標。
*   **Redis**: 記憶體內資料儲存，用於快取頻繁存取的資料，以減少資料庫負載並提高回應時間。
*   **RabbitMQ**: 訊息代理，將 `web-app` 與 `ai-worker` 解耦，實現可靠的非同步任務處理。
*   **MinIO**: S3 相容的物件儲存服務，用於儲存大型二進位檔案，如使用者上傳的音訊。
*   **Milvus**: 向量資料庫，用於儲存和搜尋高維度向量嵌入，這對於 AI 驅動的功能 (如語義搜尋和檢索增強生成 RAG) 至關重要。

### 2.4 非功能性需求設計 (NFRs Design)

*   **性能 (Performance)**: API 回應時間 < 500ms。透過在 `web-app` 中使用 Redis 快取熱點數據 (如病患列表) 來達成。
*   **安全性 (Security)**: 所有需授權的 API 均透過 `Flask-JWT-Extended` 進行 JWT 驗證。密碼使用 `bcrypt` 進行雜湊儲存。
*   **可靠性 (Reliability)**: `web-app` 和 `ai-worker` 透過 RabbitMQ 解耦。即使 `ai-worker` 暫時離線，任務也會在佇列中等待，不會遺失。
