# 健康陪跑台語語音機器人 (Beloved Grandson)

## 1. 專案概述

本專案是一個基於 Docker Compose 部署的微服務 AI 對話應用，旨在為慢性病患者提供一個台語語音互動的健康管理夥伴。系統整合了語音轉文字 (STT)、大型語言模型 (LLM) 及文字轉語音 (TTS) 等核心 AI 功能，並透過非同步任務佇列實現服務間的高效協作。

### 核心功能
*   **使用者管理**: 包含治療師、管理員與病患三種角色。
*   **病患儀表板**: 供治療師追蹤管理所有病患的健康狀況。
*   **健康數據追蹤**: 病患可每日記錄喝水、用藥、運動、抽菸等數據。
*   **臨床問卷**: 實現標準化的 CAT 與 MMRC 問卷，供病患每月填寫。
*   **AI 語音對話**: (開發中) 病患可透過台語語音與 AI 進行互動。

### 技術架構
| 組件 | 技術/服務 | 用途 |
| :--- | :--- | :--- |
| **Web 應用** | Flask | API Gateway, 處理使用者請求, WebSocket 通訊 |
| **非同步任務** | Celery / RabbitMQ | 處理耗時的 AI 任務 (STT, LLM, TTS) |
| **資料庫** | PostgreSQL | 儲存核心業務資料 (使用者, 健康數據等) |
| **快取** | Redis | 儲存 Session, 快取常用查詢 |
| **物件儲存** | MinIO | 儲存使用者上傳的音檔及 AI 生成的音檔 |
| **反向代理** | Nginx | (生產環境) 統一請求入口, 負載平衡 |
| **容器化** | Docker / Docker Compose | 統一部署與管理所有服務 |

---

## 2. 初次使用設定

在開始之前，請確保您的系統已安裝 **Docker** 和 **Docker Compose**。

### 步驟 1: 複製專案

```bash
git clone <您的專案 Git URL>
cd <專案目錄>
```

### 步驟 2: 設定環境變數

本專案使用兩個環境變數檔案，請分別建立：

**2.1. 專案根目錄 `.env`**

此檔案主要供 Docker Compose 使用，用於設定資料庫、MinIO 等服務的**帳號密碼**。

```bash
cp .env.example .env
```

**2.2. Web App 專用 `.flaskenv`**

此檔案位於 `services/web-app/` 目錄下，主要供 Flask 應用程式讀取，用於設定**服務連線 URL** 和 Flask 自身的行為。

```bash
cp services/web-app/.flaskenv.example services/web-app/.flaskenv
```

**重要提示**: 在本地開發環境中，您**無需修改**這兩個檔案的任何內容即可啟動。若要部署到生產環境，請務必修改 `.env` 檔案中的所有密碼，並考慮使用更安全的方式管理 `.flaskenv` 中的連線資訊。

### 步驟 3: 修正換行符號 (Windows 使用者)

為避免腳本執行錯誤，請確保以下檔案的換行符號為 `LF` (可在 VS Code 右下角切換)：
*   `.env`
*   `services\web-app\entrypoint.sh`
*   `infra\nginx\init-letsencrypt.sh`

---

## 3. 開發環境工作流程

### 步驟 1: 啟動開發環境

此指令會建置並啟動所有開發所需的服務。`--build` 參數會確保在您修改了 `requirements.txt` 等依賴後，容器會被重新建置。

```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### 步驟 2: 初始化與遷移資料庫

如果是**第一次**啟動專案，或在**模型 (models.py) 發生變更**後，需要執行以下資料庫遷移指令：

```bash
# 進入 web-app 容器
docker-compose -f docker-compose.dev.yml exec web-app bash

# 在容器內執行遷移 (如果是第一次，請先執行 flask db init)
flask db migrate -m "您的變更描述"
flask db upgrade

# 完成後退出容器
exit
```

### 步驟 3: 建立測試資料集 (強烈建議)

為了方便測試所有 API 功能，我們提供了一個功能強大的資料生成腳本。它會**清除所有現有資料**，並建立一個包含大量擬真數據的全新資料集。

*   **執行指令**:
    ```bash
    docker-compose -f docker-compose.dev.yml exec web-app python seed_data.py
    ```
*   **生成內容**:
    *   **1 位管理員**:
        *   帳號: `admin`
        *   密碼: `admin`
    *   **5 位治療師**:
        *   帳號: `therapist_01` ~ `therapist_05`
        *   密碼: `password`
    *   **50 位病患**:
        *   帳號: `patient_001` ~ `patient_050`
        *   密碼: `password`
    *   **12 個月的歷史資料**:
        *   每位病患的每日健康日誌。
        *   每位病患的每月 CAT & MMRC 問卷。

### 常用開發指令

*   **查看所有服務日誌**:
    ```bash
    docker-compose -f docker-compose.dev.yml logs -f
    ```
*   **只查看特定服務日誌** (例如 `web-app`):
    ```bash
    docker-compose -f docker-compose.dev.yml logs -f web-app
    ```
*   **停止並移除所有開發容器**:
    ```bash
    docker-compose -f docker-compose.dev.yml down -v
    ```

---

## 4. 執行測試

本專案使用 `pytest` 進行單元測試與整合測試。所有測試相關的指令都應在 `web-app` 服務的容器內執行。

### 步驟 1: 執行基本測試

您可以使用以下指令來執行所有測試：

```bash
docker-compose -f docker-compose.dev.yml exec web-app pytest
```

若要執行特定模組的測試，可以指定檔案路徑：

```bash
docker-compose -f docker-compose.dev.yml exec web-app pytest tests/test_patients.py
```

### 步驟 2: 產生測試覆蓋率報告

為了評估測試的完整性，您可以產生一份覆蓋率報告。此報告會顯示哪些程式碼行有被測試覆蓋，哪些沒有。

```bash
docker-compose -f docker-compose.dev.yml exec web-app pytest --cov=app --cov-report=term-missing
```

*   `--cov=app`: 指定要計算覆蓋率的目標目錄 (我們的 Flask 應用程式位於 `app` 目錄下)。
*   `--cov-report=term-missing`: 在終端機中顯示報告，並特別標示出「未被覆蓋」的程式碼行號。

---

## 5. 生產環境部署 (全自動 HTTPS)

生產環境使用 `Nginx` 作為反向代理，並透過一個智慧型啟動腳本與 `Certbot` 深度整合，實現 SSL 憑證申請與續期的全自動化。您無需手動執行任何 `certbot` 指令或在主機上設定 `cron job`。

### 前置作業

1.  **網域名稱**: 您必須擁有一個或多個網域名稱 (例如 `your-domain.com`, `www.your-domain.com`)。
2.  **公開 IP**: 您需要一台具有公開 IP 位址的伺服器。
3.  **DNS 設定**: 請在您的網域服務商後台，為您所有要使用的網域名稱新增 `A` 紀錄，將它們指向伺服器的公開 IP。
4.  **防火牆**: 請確保您的伺服器防火牆已開啟 `80` (HTTP) 和 `443` (HTTPS) 連接埠。

### 部署步驟

#### 步驟 1: 設定 `.env` 環境變數

複製範例檔案，並填寫所有必要的資訊。

```bash
cp .env.example .env
```

接著，使用編輯器打開 `.env` 檔案，**務必填寫**以下變數：
*   `CERTBOT_DOMAINS`: **(必填)** 您的網域名稱，如果有多個，請用空格隔開。**第一個域名會被視為主域名**。例如：`CERTBOT_DOMAINS=teabe.idv.tw www.teabe.idv.tw`
*   `CERTBOT_EMAIL`: **(必填)** 您用於接收 Let's Encrypt 重要通知信的電子郵件。
*   `CERTBOT_STAGING`: **(選填)** 設為 `1` 使用 Let's Encrypt 的測試環境，設為 `0` 使用生產環境。**預設為 `1` (測試)**。建議首次部署或進行除錯時使用測試環境。

同時，也請務必修改檔案中所有預設的資料庫密碼，以策安全。

#### 步驟 2: 一鍵啟動！

完成 `.env` 設定後，執行以下單一指令即可建置、申請憑證並啟動所有服務。

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

腳本會自動處理所有事情：
*   如果沒有憑證，它會先用一個**自簽名憑證**啟動 Nginx。
*   然後在背景向 Let's Encrypt **申請真實憑證**。
*   成功取得後，會**自動重啟 Nginx** 以載入新憑證。
*   容器內部已包含一個**每日執行的排程任務**，會自動為您續期憑證。

現在，您可以透過 `https://<您的主域名>` 來存取您的應用程式了。

### 疑難排解與維護

#### Let's Encrypt 速率限制

在反覆測試的過程中，您可能會遇到 Let's Encrypt 的[速率限制](https://letsencrypt.org/docs/rate-limits/) (每週只能為同一個域名申請 5 次憑證)。

*   **症狀**: Nginx 容器不斷重啟，日誌中出現 `too many certificates already issued` 的錯誤。
*   **解決方法**:
    1.  編輯 `.env` 檔案，設定 `CERTBOT_STAGING=1` 來切換到測試環境。
    2.  執行 `docker-compose -f docker-compose.prod.yml down` 停止服務。
    3.  **(重要)** 執行 `rmdir /s /q data\certbot` (Windows) 或 `rm -rf data/certbot` (Linux/macOS) 來清除舊的憑證資料。
    4.  重新執行 `docker-compose -f docker-compose.prod.yml up --build -d`。服務將會用測試憑證啟動。
    5.  等待一週，讓速率限制解除後，再切換回 `CERTBOT_STAGING=0` 並重複清理步驟。

#### 停止生產環境

```bash
docker-compose -f docker-compose.prod.yml down -v
```
加上 `-v` 會一併刪除所有資料庫的 volume，請謹慎使用。

---

## 6. 服務入口 (開發環境)

| 服務 | 內部埠 | 外部 URL / 連線資訊 | 備註 |
| :--- | :--- | :--- | :--- |
| **Web App (API)** | `5000` | `http://localhost:5000` | 主要 API 服務 |
| **Swagger UI** | `5000` | `http://localhost:5000/apidocs/` | API 文件與測試介面 |
| **PostgreSQL** | `5432` | `localhost:15432` | DB, 帳密請見 `.env` |
| **Redis** | `6379` | `localhost:6379` | 快取服務 |
| **RabbitMQ UI** | `15672`| `http://localhost:15672` | 帳號/密碼: `guest`/`guest` |
| **MinIO Console**| `9001` | `http://localhost:9001` | 帳號/密碼: `minioadmin`/`minioadmin` |
| **LLM Service** | `8001` | `http://localhost:8001` | (若需單獨測試) |
| **STT Service** | `8002` | `http://localhost:8002` | (若需單獨測試) |
| **TTS Service** | `8003` | `http://localhost:8003` | (若需單獨測試) |

## 使用ubuntu WSL中執行docker指令會有

```sh
chmod +x services/web-app/entrypoint.sh
```

圖文選單，進入容器裡執行以下指令

```py
python create_rich_menus.py
```

Endpoint URL
`https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.ngrok-free.app/api/v1/auth/liff`

Webhook URL
`https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.ngrok-free.app/api/v1/chat/webhook`


```
1. 前後端分離
```
