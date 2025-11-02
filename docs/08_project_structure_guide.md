# 專案結構指南 - RespiraAlly

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-11-03`
**主要作者 (Lead Author):** `[技術負責人]`
**狀態 (Status):** `活躍 (Active)`

---

## 1. 指南目的

*   為 `RespiraAlly` 專案提供一個標準化、可擴展且易於理解的目錄和文件結構。
*   確保團隊成員能夠快速定位代碼、配置文件和文檔，降低新成員的上手成本。
*   促進代碼的模塊化和關注點分離，提高可維護性。

## 2. 核心設計原則

*   **按服務劃分 (Organize by Service)**: 專案的核心是微服務架構，頂層目錄按服務 (`frontend`, `web-app`, `ai-worker`) 和基礎設施 (`infra`) 進行劃分。
*   **按功能組織 (Organize by Feature)**: 在每個服務內部，相關的功能應盡可能放在一起 (例如 `web-app/app/api/patients.py`)。
*   **明確的職責**: 每個頂層目錄都應該有其單一、明確的職責。
*   **配置外部化**: 應用程式的配置 (`.env`, `.flaskenv`) 與代碼分離，便於在不同環境中部署。

## 3. 頂層目錄結構

```plaintext
/mnt/a/AIPE01_期末專題/RespiraAlly_dev/
├── .github/              # CI/CD 工作流程
├── docs/                 # 專案文檔 (本文件、PRD、架構文件等)
├── infra/                # 基礎設施配置 (Nginx, Postgres)
├── scripts/              # 開發和運維輔助腳本
├── services/             # 所有微服務的原始碼
│   ├── frontend/         # 前端 React 應用
│   ├── web-app/          # 後端 Flask API 應用
│   └── ai-worker/        # AI 背景任務處理服務
├── .env.example          # Docker Compose 環境變數範本
├── .gitignore            # Git 忽略文件
├── docker-compose.dev.yml  # 開發環境 Docker Compose 配置
├── docker-compose.prod.yml # 生產環境 Docker Compose 配置
└── README.md             # 專案介紹和快速入門指南
```

## 4. 目錄詳解

### 4.1 `services/web-app/` - 後端 API 服務

*   **職責**: 提供 RESTful API，處理業務邏輯，與資料庫互動，並將非同步任務發布到 `ai-worker`。
*   **結構**:
    ```plaintext
    services/web-app/
    ├── app/                  # Flask 應用程式主目錄
    │   ├── __init__.py
    │   ├── app.py            # Flask App 工廠
    │   ├── config.py         # 組態設定
    │   ├── api/              # API 藍圖 (按資源劃分)
    │   │   ├── auth.py
    │   │   ├── patients.py
    │   │   └── ...
    │   ├── core/             # 核心業務邏輯與倉儲
    │   │   ├── patient_service.py
    │   │   └── patient_repository.py
    │   └── models/           # SQLAlchemy ORM 模型 (統一在 models.py 中定義)
    │       └── models.py
    ├── migrations/           # Alembic 資料庫遷移腳本
    ├── tests/                # Pytest 測試代碼
    ├── requirements.txt      # Python 依賴
    └── Dockerfile
    ```

### 4.2 `services/frontend/` - 前端儀表板服務

*   **職責**: 提供給呼吸治療師使用的 Web 儀表板。
*   **結構**:
    ```plaintext
    services/frontend/
    ├── public/               # 靜態資源
    ├── src/                  # React 應用程式原始碼
    │   ├── App.jsx           # 根元件
    │   ├── main.jsx          # 應用程式入口
    │   ├── pages/            # 頁面級元件 (Dashboard, PatientDetail)
    │   ├── shared/           # 跨頁面共享的邏輯與元件
    │   │   ├── api/          # API 呼叫封裝
    │   │   ├── components/   # 可重用 UI 元件
    │   │   └── contexts/     # React Context
    │   └── styles/           # 全域樣式
    ├── package.json          # Node.js 依賴
    ├── vite.config.js        # Vite 組態設定
    └── Dockerfile
    ```

### 4.3 `services/ai-worker/` - AI 背景任務服務

*   **職責**: 處理耗時的非同步任務，如 STT, LLM, TTS。
*   **結構**:
    ```plaintext
    services/ai-worker/
    ├── worker/               # Worker 應用程式主目錄
    │   ├── main.py           # 監聽 RabbitMQ 並分派任務
    │   ├── domain/           # 核心領域物件
    │   ├── llm_app/          # LLM 相關邏輯
    │   │   └── chat_pipeline.py
    │   ├── stt_app/          # 語音轉文字服務
    │   └── tts_app/          # 文字轉語音服務
    ├── requirements.txt      # Python 依賴
    └── Dockerfile
    ```

### 4.4 `infra/` - 基礎設施配置

*   **職責**: 存放所有與環境基礎設施相關的配置，使其與應用程式碼分離。
*   **結構**:
    ```plaintext
    infra/
    ├── nginx/                # Nginx 設定
    │   ├── default.conf
    │   └── Dockerfile.dev
    └── postgres/             # PostgreSQL 設定
        └── init.sql
    ```

## 5. 演進原則

*   本結構是一個起點，應根據專案的發展進行調整。
*   任何對服務邊界或頂層目錄結構的重大變更，都應透過團隊討論並更新本文件。
*   保持結構的清晰和一致性比嚴格遵守某個特定模式更重要。
