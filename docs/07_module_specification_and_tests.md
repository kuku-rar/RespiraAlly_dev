# 模組規格與測試案例 - RespiraAlly

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-11-03`
**主要作者 (Lead Author):** `[開發工程師]`
**狀態 (Status):** `待開發 (To Do)`

---

## 目錄 (Table of Contents)

- [模組: `DailyMetricService`](#-模組-dailymetricservice)
  - [規格 1: `add_daily_metric`](#-規格-1-add_daily_metric)
  - [測試情境與案例](#-測試情境與案例-test-scenarios--cases)

---

**目的**: 本文件旨在將高層次的 BDD 情境分解到 `web-app` 服務中的具體模組，定義其詳細規格與測試場景，直接指導 TDD (測試驅動開發) 的實踐。

---

## 模組: `DailyMetricService`

**路徑**: `services/web-app/app/core/daily_metric_service.py`
**對應架構文件**: `[05_architecture_and_design_document.md](./05_architecture_and_design_document.md)`
**對應 BDD Feature**: `[patient_health_log.feature](./03_behavior_driven_development_guide.md)`

### 相關資料模型定義

本服務所操作的資料模型，例如 `DailyMetric`，統一在 `services/web-app/app/models/models.py` 中定義。這確保了所有資料庫實體及其關係的集中管理與可見性。

---

### 規格 1: `add_daily_metric`

**描述 (Description)**: 為指定病患新增一筆當日的健康日誌。如果當日已存在記錄，則應防止重複新增。

**契約式設計 (Design by Contract, DbC)**:
*   **前置條件 (Preconditions)**: 
    1.  `user_id` 必須對應到一個已存在的病患使用者。
    2.  `metric_data` (DTO) 中的所有數值 (如 `water_cc`, `exercise_min`) 必須為非負整數。
*   **後置條件 (Postconditions)**: 
    1.  如果當日無記錄，成功執行後，資料庫中會新增一筆對應 `user_id` 和今日日期的 `DailyMetric` 記錄。
    2.  返回新建立的 `DailyMetric` 實體物件。
    3.  如果當日已有記錄，函式應拋出 `ConflictError` 例外。
*   **不變性 (Invariants)**: 
    1.  一個病患在同一天只能有一筆 `DailyMetric` 記錄。

---

### 測試情境與案例 (Test Scenarios & Cases)

*以下是針對 `add_daily_metric` 規格需要覆蓋的 `pytest` 測試情境。*

#### 情境 1: 正常路徑 (Happy Path)

*   **測試案例 ID**: `test_add_daily_metric_success`
*   **描述**: 成功為病患新增第一筆當日健康日誌。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**: `mock` 一個 `DailyMetricRepository`，使其 `find_by_date` 方法返回 `None`。
    2.  **Act**: 呼叫 `daily_metric_service.add_daily_metric(user_id=1, metric_data=...)`。
    3.  **Assert**:
        *   驗證 `repository.add` 方法被以正確的參數呼叫了一次。
        *   驗證返回的物件是預期的 `DailyMetric` 實體。

#### 情境 2: 業務規則 (Business Rule)

*   **測試案例 ID**: `test_add_daily_metric_conflict`
*   **描述**: 當病患當日已提交過日誌時，嘗試再次提交。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**: `mock` 一個 `DailyMetricRepository`，使其 `find_by_date` 方法返回一個已存在的 `DailyMetric` 物件。
    2.  **Act & Assert**: 使用 `pytest.raises(ConflictError)` 來斷言當呼叫 `daily_metric_service.add_daily_metric(...)` 時，會拋出 `ConflictError` 例外。

#### 情境 3: 無效輸入 (違反前置條件)

*   **測試案例 ID**: `test_add_daily_metric_invalid_user`
*   **描述**: 嘗試為一個不存在的病患 ID 新增日誌。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**: `mock` `PatientRepository`，使其 `get_by_id` 方法返回 `None` (或在 Service 層的前置檢查中拋出 `NotFoundError`)。
    2.  **Act & Assert**: 預期 `daily_metric_service.add_daily_metric` 呼叫會拋出 `NotFoundError`。

*   **測試案例 ID**: `test_add_daily_metric_negative_value`
*   **描述**: 嘗試提交包含負數的健康數據。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**: 準備一個包含負數（如 `water_cc=-100`）的 `metric_data` DTO。
    2.  **Act & Assert**: 預期 Pydantic/Marshmallow 等驗證層會攔截並拋出 `ValidationError`，或者在 Service 層的檢查中拋出 `ValueError`。
