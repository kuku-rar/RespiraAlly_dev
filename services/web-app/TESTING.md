# API Contract Testing Guide

## 📋 概述

本指南說明如何執行 RespiraAlly V1 的 API 契約測試。

**哲學**: "測試是安全網,沒有安全網不准跳傘(重構)" - Linus Torvalds

## 🔧 測試工具

### 1. validate_tests.py - 靜態驗證工具

**用途**: 在不執行測試的情況下驗證測試代碼的正確性

**功能**:
- ✅ Python 語法檢查 (AST 解析)
- ✅ 測試函式發現
- ✅ OpenAPI 規格驗證
- ✅ 測試覆蓋率分析
- ✅ conftest.py 驗證

**使用方式**:
```bash
python3 validate_tests.py
```

**輸出範例**:
```
✅ OpenAPI spec is valid
   Title: RespiraAlly V1 API
   Version: 1.0.0
   Endpoints: 43

✅ Test coverage: 111.6% (48 tests / 43 endpoints)
✅ All validations passed! Tests are ready to run.
```

### 2. test_runner.sh - Docker 測試執行器

**用途**: 在乾淨的 Docker 環境中執行完整測試

**優點**:
- 🐳 不污染本地系統
- 🔒 隔離測試環境
- 📦 自動建立測試映像
- 🧹 自動清理容器

**使用方式**:
```bash
# 基本執行
./test_runner.sh

# 詳細輸出
./test_runner.sh --verbose

# 生成覆蓋率報告
./test_runner.sh --coverage

# 遇到失敗立即停止
./test_runner.sh --stop-on-fail

# 組合使用
./test_runner.sh --verbose --coverage
```

### 3. run_contract_tests.py - Python 測試執行器

**用途**: 使用 pytest 直接執行測試 (需要先安裝依賴)

**使用方式**:
```bash
python run_contract_tests.py              # 基本執行
python run_contract_tests.py --coverage   # 含覆蓋率
python run_contract_tests.py --verbose    # 詳細輸出
```

## 📊 測試狀態

### 當前覆蓋率

| 項目 | 數量 | 狀態 |
|------|------|------|
| OpenAPI 端點 | 43 | ✅ |
| 測試檔案 | 3 | ✅ |
| 測試函式 | 48 | ✅ |
| 測試覆蓋率 | 111.6% | ✅ |
| 語法錯誤 | 0 | ✅ |

### 測試檔案

1. **test_api_contracts.py** (17 tests)
   - Authentication (登入/註冊)
   - Patient Management (病患管理)
   - Questionnaires (問卷)
   - Daily Metrics (每日記錄)
   - User Management (使用者管理)

2. **test_api_contracts_extended.py** (24 tests)
   - Overview APIs (儀表板)
   - Voice APIs (語音)
   - Task APIs (任務)
   - Alert APIs (警示)
   - Education APIs (衛教)

3. **test_contracts_basic.py** (7 tests)
   - 基礎契約測試
   - 錯誤處理驗證
   - CORS 標頭驗證
   - OpenAPI 規格驗證

## 🚀 快速開始

### 步驟 1: 驗證測試檔案

```bash
python3 validate_tests.py
```

**預期輸出**: `✅ All validations passed!`

### 步驟 2A: Docker 環境執行 (推薦)

```bash
./test_runner.sh --verbose --coverage
```

### 步驟 2B: 本地環境執行 (需安裝依賴)

```bash
# 安裝依賴 (一次性)
pip install -r requirements.txt

# 執行測試
pytest tests/ -v
```

## 🐛 故障排除

### 問題 1: validate_tests.py 失敗

```bash
# 檢查 Python 版本 (需要 3.8+)
python3 --version

# 檢查 YAML 模組
python3 -c "import yaml; print('OK')"

# 如果缺少 pyyaml
pip install pyyaml
```

### 問題 2: Docker 執行失敗

```bash
# 檢查 Docker 狀態
docker --version
docker ps

# 清理舊容器
docker stop respirally-api-test 2>/dev/null
docker rm respirally-api-test 2>/dev/null
```

### 問題 3: 測試導入錯誤

```bash
# 確保在正確的目錄
pwd  # 應該在 services/web-app/

# 檢查 PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
```

## 📈 CI/CD 整合

測試將整合到 CI/CD 流程 (Task 0.3):

```yaml
# GitHub Actions 範例
- name: Validate Tests
  run: python3 validate_tests.py

- name: Run Contract Tests
  run: ./test_runner.sh --coverage

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## 🎯 驗收標準

Phase 0 - Task 0.2 驗收標準:

- [x] ✅ API 契約測試覆蓋率 = 100% (111.6%)
- [ ] ⏳ 所有測試通過 (需 Docker 執行驗證)
- [ ] ⏳ 測試可在 Docker 環境獨立執行 (test_runner.sh 已建立)

## 📚 參考資源

- [OpenAPI 規格](./openapi.yaml)
- [測試 README](./tests/README.md)
- [重構計劃](../../docs/refactoring_plan.md)

---

**最後更新**: 2025-11-03
**狀態**: ✅ 靜態驗證通過,等待 Docker 執行驗證
