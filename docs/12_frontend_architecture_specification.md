# 前端架構與開發規範 - RespiraAlly Dashboard & LIFF

---

**文件版本 (Document Version):** `v1.0`  
**最後更新 (Last Updated):** `2025-11-03`  
**主要作者 (Lead Author):** `Gemini`  
**審核者 (Reviewers):** `[前端技術負責人]`  
**狀態 (Status):** `草稿 (Draft)`

**相關文檔 (Related Documents):**
- 專案 PRD: `[連結到 02_project_brief_and_prd.md]`
- 系統架構文檔: `[連結到 05_architecture_and_design_document.md]`
- API 設計規範: `[連結到 06_api_design_specification.md]`

---

## 目錄 (Table of Contents)
- [第一部分：前端架構的系統化分層](#第一部分前端架構的系統化分層)
- [第二部分：技術選型與架構決策](#第二部分技術選型與架構決策)
- [第三部分：前端工程化實踐](#第三部分前端工程化實踐)
- [第四部分：前後端協作契約](#第四部分前後端協作契約)
- [第五部分：監控、日誌與安全](#第五部分監控日誌與安全)

---

## 第一部分：前端架構的系統化分層

本專案前端採用了清晰的多應用 (Multi-App) 架構，將職責明確分離為兩個獨立的單頁應用 (SPA)：

1.  **`dashboard`**: 供呼吸治療師使用的後台管理儀表板。
2.  **`liff`**: 供病患在 LINE 環境中使用的前端應用。

這種分離確保了兩端用戶體驗的獨立性，並允許各自獨立迭代。

```mermaid
graph TD
    subgraph "用戶"
        Therapist[治療師]
        Patient[病患]
    end

    subgraph "前端應用 (React)"
        DashboardApp[Dashboard 應用<br/>(治療師端)]
        LIFFApp[LIFF 應用<br/>(病患端)]
    end

    subgraph "共享模組 (src/shared)"
        SharedComponents[共享組件]
        SharedHooks[共享 Hooks]
        SharedContexts[共享 Contexts]
        SharedAPI[共享 API 客戶端]
    end

    Therapist --> DashboardApp
    Patient --> LIFFApp

    DashboardApp --> SharedComponents
    DashboardApp --> SharedHooks
    DashboardApp --> SharedContexts
    DashboardApp --> SharedAPI

    LIFFApp --> SharedComponents
    LIFFApp --> SharedHooks
    LIFFApp --> SharedContexts
    LIFFApp --> SharedAPI

    SharedAPI --> Backend[後端 API]

    style DashboardApp fill:#e3f2fd
    style LIFFApp fill:#e8f5e9
```

### 2.1 用戶感知層 (Perception Layer)
- **UI 組件庫**: **Ant Design (`antd`)** 作為主 UI 框架，提供穩定、豐富的基礎組件。
- **圖表**: **Recharts** 用於數據可視化，如在治療師儀表板中顯示病患指標趨勢。
- **樣式方案**: 採用 **CSS Modules** 進行組件級樣式隔離，並搭配全局樣式表 (`src/styles/index.css`) 進行基礎設定。

### 2.2 互動邏輯層 (Interaction Layer)
- **路由管理**: **React Router (`react-router-dom`)** 負責應用的頁面導航。`App.jsx` 中定義了頂層路由，將流量分發到 `dashboard` 和 `liff` 兩個子應用。
- **表單處理**: **React Hook Form** 結合 **Zod** 進行表單狀態管理和客戶端驗證，提供高效且類型安全的表單開發體驗。

### 2.3 狀態管理層 (State Management Layer)
本專案採用了分層的狀態管理策略：
- **伺服器狀態 (Server State)**: **TanStack React Query (`@tanstack/react-query`)** 是核心的數據獲取與快取引擎。所有與後端 API 的通訊都由它管理，自動處理快取、重新驗證、加載和錯誤狀態。
- **全局 UI 狀態 (Global UI State)**: 使用 **React Context API** (`src/shared/contexts`) 管理跨組件共享的 UI 狀態，例如 `AuthContext` (用戶認證)、`ThemeContext` (主題) 和 `AccessibilityContext` (無障礙設定)。
- **本地組件狀態 (Local State)**: 使用 React 原生的 `useState` 和 `useReducer` 處理單一組件內部的狀態。

### 2.4 數據通訊層 (Data Communication Layer)
- **API 客戶端**: **Axios** 被封裝在 `src/shared/api` 中，作為所有 HTTP 請求的客戶端。它配置了攔截器 (interceptors) 來統一處理請求頭 (如 Authorization) 和響應錯誤。
- **數據轉換**: Zod 用於在 API 邊界驗證和解析響應數據，確保進入前端應用的數據類型正確。

### 2.5 基礎設施層 (Infrastructure Layer)
- **構建工具**: **Vite** 提供了極速的開發伺服器和高效的生產環境打包。
- **測試框架**: **Vitest** 結合 **React Testing Library** 進行單元測試和組件測試。
- **CI/CD**: `package.json` 中定義了 `lint`, `test`, `build` 等腳本，可直接整合到 GitHub Actions 或其他 CI/CD 平台。

---

## 第二部分：技術選型與架構決策

| 領域 | 技術/方案 | 決策理由 |
|:---|:---|:---|
| **前端框架** | **React** | 團隊熟悉度高，生態系統成熟，擁有豐富的第三方庫。 |
| **構建工具** | **Vite** | 提供卓越的開發體驗 (HMR) 和快速的建置速度。 |
| **狀態管理** | **TanStack React Query + Context** | 專門的伺服器狀態管理庫能極大簡化數據獲取邏輯；Context 足以應對全局 UI 狀態，避免引入 Redux 等重型庫的複雜性。 |
| **UI 組件庫** | **Ant Design** | 提供了一套完整、高質量的企業級 UI 組件，可加速開發。 |
| **路由** | **React Router** | React 生態中最主流、功能最強大的路由解決方案。 |
| **表單** | **React Hook Form + Zod** | 性能優異（非受控組件），結合 Zod 可實現端到端的類型安全驗證。 |
| **API 通訊** | **Axios** | 功能強大，支持攔截器、取消請求等高級功能，是成熟的 HTTP 客戶端。 |
| **測試** | **Vitest** | 與 Vite 無縫整合，API 兼容 Jest，提供了現代化的測試體驗。 |

---

## 第三部分：前端工程化實踐

### 7.1 項目結構與代碼組織
專案結構遵循「關注點分離」和「按功能組織」的原則。

```
src/
├── apps/               # 多應用入口
│   ├── dashboard/      # 治療師儀表板應用
│   └── liff/           # 病患 LIFF 應用
├── assets/             # 靜態資源 (圖片, 字體)
├── hooks/              # 全局共享的自定義 Hooks
├── pages/              # 通用頁面 (如登入頁)
├── shared/             # 跨應用的共享模組
│   ├── api/            # API 客戶端封裝
│   ├── components/     # 共享 UI 組件
│   ├── contexts/       # React Context
│   ├── hooks/          # 共享業務 Hooks
│   └── utils/          # 工具函數
├── styles/             # 全局樣式
└── main.jsx            # 應用主入口
```

### 7.2 代碼質量保證
- **ESLint**: 用於靜態程式碼分析，確保風格一致並發現潛在錯誤。
- **TypeScript**: 雖然專案目前使用 `.jsx`，但已安裝 `typescript` 和 `@types`，具備隨時遷移到 TypeScript 的能力。`tsc --noEmit` 腳本用於類型檢查。

### 7.3 測試策略
- **單元測試**: 使用 `vitest` 測試獨立的 Hooks 和工具函數。
- **組件測試**: 使用 `vitest` 和 `@testing-library/react` 測試組件的渲染和互動是否符合預期。
- **E2E 測試**: (建議) 使用 Playwright 或 Cypress 對關鍵用戶流程（如登入、提交表單）進行端到端測試。

### 7.4 CI/CD 集成
`package.json` 中的 `scripts` 已為 CI/CD 流程準備就緒：
1.  `pnpm install`: 安裝依賴。
2.  `pnpm lint`: 執行程式碼檢查。
3.  `pnpm test:run`: 運行所有測試。
4.  `pnpm build`: 產生生產環境的打包文件。

---

## 第四部分：前後端協作契約

### 8.1 API 通訊規範
- 所有 API 請求通過 `axios` 實例發出，該實例配置了 `baseURL`。
- `Authorization` 頭由 `AuthContext` 和 `axios` 攔截器自動處理，攜帶 JWT。
- 推薦使用 `Zod` 在 API 層對響應數據進行驗證，確保數據進入應用時的類型安全。

### 8.2 錯誤處理策略
- **React Query**: 自動處理 API 請求的錯誤狀態，可以通過 `isError` 和 `error` 屬性在組件中獲取。
- **Axios 攔截器**: 統一處理 401 (未授權) 等全局性 HTTP 錯誤，例如自動跳轉到登錄頁。
- **Error Boundary**: 使用 `react-error-boundary` 在組件樹的頂層捕獲渲染時的錯誤，防止整個應用崩潰。

---

## 第五部分：監控、日誌與安全

### 9.1 前端監控策略
- **性能監控**: (建議) 整合 `web-vitals` 庫來收集 Core Web Vitals (LCP, FID, CLS) 並發送到分析服務。
- **錯誤追蹤**: (建議) 整合 Sentry 或 LogRocket 等服務，自動捕獲和報告生產環境中的 JavaScript 錯誤。

### 9.2 前端安全實踐
- **XSS 防護**: React 默認對 JSX 內容進行轉義，已提供基礎防護。避免使用 `dangerouslySetInnerHTML`。
- **CSRF 防護**: 依賴後端 API 的 CSRF 保護機制 (如 CSRF Token 或 SameSite Cookies)。
- **環境變數**: API 金鑰等敏感資訊通過 `.env` 文件管理，並使用 `VITE_` 前綴，不會暴露在客戶端。
- **依賴安全**: (建議) 定期運行 `pnpm audit` 並使用 Dependabot 等工具自動更新依賴，修補已知的安全漏洞。
