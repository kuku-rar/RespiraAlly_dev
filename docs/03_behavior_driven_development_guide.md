# 行為驅動情境 (BDD) 指南 - RespiraAlly

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-11-03`
**主要作者 (Lead Author):** `[技術負責人, 產品經理]`
**狀態 (Status):** `活躍 (Active)`

---

## 目錄 (Table of Contents)

- [Ⅰ. BDD 核心原則](#-bdd-核心原則)
- [Ⅱ. Gherkin 語法速查](#-gherkin-語法速查)
- [Ⅲ. BDD 範本 (`.feature` file)](#-bdd-範本-feature-file)
- [Ⅳ. 最佳實踐](#-最佳實踐)

---

**目的**: 本文件旨在為 RespiraAlly 專案提供一套標準化的指南和範本，用於編寫行為驅動開發 (BDD) 的情境。BDD 的核心是使用一種名為 Gherkin 的結構化自然語言，來描述系統的預期行為，確保業務人員、開發者和測試者對「完成」的定義達成共識。

---

## Ⅰ. BDD 核心原則

1.  **從對話開始**: BDD 不是關於寫測試，而是關於團隊成員（業務、開發、測試）之間的對話，以確保對需求的共同理解。
2.  **由外而內**: 我們從使用者與系統的互動（外部行為）開始定義，然後才深入到內部實現。
3.  **使用通用語言 (Ubiquitous Language)**: 在 BDD 情境中使用的術語，應與在 PRD 和程式碼中使用的術語保持一致。

---

## Ⅱ. Gherkin 語法速查

*   `Feature`: 描述一個高層次的功能，對應 PRD 中的一個核心史詩 (Core Epic)。
*   `Scenario`: 描述 `Feature` 下的一個具體業務場景或測試案例。
*   `Given`: **(給定)** 描述場景開始前的初始狀態或上下文。
*   `When`: **(當)** 描述使用者執行的某個具體操作或觸發的事件。
*   `Then`: **(那麼)** 描述在 `When` 發生後，系統應有的輸出或結果。
*   `And`, `But`: 用於連接多個 `Given`, `When`, 或 `Then` 步驟。
*   `Background`: 用於定義在該 Feature 的所有 Scenarios 之前都需要執行的 `Given` 步驟。
*   `Scenario Outline`: 用於執行同一個場景的多組不同數據的測試。

---

## Ⅲ. BDD 範本 (`.feature` file)

以下是針對 RespiraAlly 專案核心功能的 BDD 範本。

### 範例 1: 病患提交健康日誌

**檔案名稱**: `patient_health_log.feature`

```gherkin
# Feature: 病患健康日誌
# 目的: 讓病患可以每日記錄自己的健康狀況，以便治療師追蹤。
# 對應 PRD: 02_project_brief_and_prd.md (US-001)

Feature: Patient Health Log

  Background:
    Given a registered patient with user_id "123" is logged in
    And the patient is on the daily health log page

  @happy-path @smoke-test
  Scenario: 首次成功提交當日健康日誌
    Given the patient has not submitted the health log for today
    When the patient fills in "喝水量" with "2000"
    And the patient checks "按時服藥"
    And the patient fills in "運動時間" with "30"
    And the patient presses the "提交" button
    Then the system should save a new daily metric for user_id "123"
    And the patient should see a success message "今日健康日誌已成功記錄！"

  @sad-path
  Scenario: 提交已存在的當日健康日誌
    Given the patient has already submitted the health log for today
    When the patient tries to press the "提交" button again
    Then the system should prevent creating a new record
    And the patient should see an error message "您今天已經記錄過了喔！"

```

### 範例 2: 治療師查看病患儀表板

**檔案名稱**: `therapist_dashboard.feature`

```gherkin
# Feature: 治療師儀表板
# 目的: 讓治療師可以查看其管理的病患列表與關鍵指標。
# 對應 PRD: 02_project_brief_and_prd.md (US-004)

Feature: Therapist Dashboard

  Background:
    Given a therapist with user_id "therapist_01" is logged in
    And this therapist manages a patient named "陳美麗"

  @happy-path
  Scenario: 治療師查看病患列表
    When the therapist navigates to the patient dashboard page
    Then the therapist should see "陳美麗" in the patient list
    And the list should show "陳美麗"'s latest CAT score

  @edge-case
  Scenario Outline: 根據風險等級篩選病患
    Given patient "<patient_name>" has a risk level of "<risk_level>"
    When the therapist filters the list by risk level "<filter_by>"
    Then the visibility of "<patient_name>" in the list should be <should_see>

    Examples:
      | patient_name | risk_level | filter_by | should_see |
      | "王大明"     | "high"     | "high"    | "visible"  |
      | "林小美"     | "low"      | "high"    | "hidden"   |
      | "張健康"     | "medium"   | "all"     | "visible"  |

```

---

## Ⅳ. 最佳實踐

1.  **一個 Scenario 只測一件事**: 保持每個場景的專注性和簡潔性。
2.  **使用陳述式而非命令式**: `Then` 應該描述「系統的狀態是什麼」，而不是「系統應該做什麼」。
3.  **避免 UI 細節**: BDD 關注的是「行為」，而不是「實現方式」。
4.  **從使用者的角度編寫**: 讓非技術人員也能輕鬆讀懂。
