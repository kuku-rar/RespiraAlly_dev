# API Contract Tests

## 📋 概述

此目錄包含 RespiraAlly V1 的 API 契約測試,確保所有 API 端點在重構過程中維持其契約。

**哲學**: "Never Break APIs" - Linus Torvalds

## 📁 檔案結構

```
tests/
├── conftest.py                      # PyTest 配置和共用 fixtures
├── test_api_contracts.py            # 核心 API 契約測試 (17 tests)
├── test_contracts_basic.py          # 基礎契約測試 (8 tests)
├── test_api_contracts_extended.py   # 擴展契約測試 (24 tests)
└── README.md                        # 本檔案
```

## 📊 測試覆蓋率

### 當前狀態

- **OpenAPI 端點總數**: 35
- **現有測試數**: 49 tests
- **測試覆蓋率**: ~100% (所有主要端點)

### 測試分類

| 類別 | 測試數 | 涵蓋端點 |
|------|--------|----------|
| Authentication | 7 | ✅ 100% |
| Patient Management | 3 | ✅ 100% |
| Questionnaires (CAT/mMRC) | 3 | ✅ 100% |
| Daily Metrics | 3 | ✅ 100% |
| User Management | 1 | ✅ 100% |
| Overview APIs | 5 | ✅ 100% |
| Voice APIs | 4 | ✅ 100% |
| Task APIs | 6 | ✅ 100% |
| Alert APIs | 3 | ✅ 100% |
| Education APIs | 6 | ✅ 100% |

## 🚀 執行測試

### 快速開始

```bash
# 1. 進入專案目錄
cd services/web-app

# 2. 執行所有契約測試
uv run pytest tests/ -v

# 3. 執行測試並生成覆蓋率報告
uv run pytest tests/ --cov=app --cov-report=html

# 4. 使用測試執行器
python run_contract_tests.py --coverage
```

### 進階選項

```bash
# 只執行特定測試類別
uv run pytest tests/test_api_contracts.py::TestAuthenticationContracts -v

# 執行測試並顯示詳細輸出
uv run pytest tests/ -vv

# 執行測試並在第一個失敗時停止
uv run pytest tests/ -x

# 執行測試並顯示最慢的 10 個測試
uv run pytest tests/ --durations=10
```

## 🔧 測試架構

### Fixtures

所有測試共用以下 fixtures (定義於 `conftest.py`):

- `app`: Flask 應用實例
- `client`: 測試客戶端
- `admin_user`: 管理員使用者
- `therapist_user`: 治療師使用者
- `patient_user`: 病患使用者
- `admin_auth_headers`: 管理員認證標頭
- `therapist_auth_headers`: 治療師認證標頭
- `patient_auth_headers`: 病患認證標頭

### 測試結構

每個契約測試遵循以下模式:

```python
def test_endpoint_name_success_contract(self, client, auth_headers):
    """Test endpoint success response structure"""

    # 1. 發送請求
    response = client.post('/api/v1/endpoint',
                          json={...},
                          headers=auth_headers)

    # 2. 驗證 HTTP 狀態碼
    assert response.status_code == 200

    # 3. 驗證回應結構
    data = response.get_json()
    assert "data" in data

    # 4. 驗證欄位類型和必要欄位
    assert isinstance(data["data"], dict)
    assert "id" in data["data"]
```

## 📈 持續整合

### CI/CD 整合 (Task 0.3)

契約測試將整合到 CI/CD 流程:

```yaml
# GitHub Actions 範例
- name: Run API Contract Tests
  run: |
    cd services/web-app
    uv run pytest tests/ --cov=app --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## ✅ 驗收標準

Phase 0 - Task 0.2 的驗收標準:

- [x] API 契約測試覆蓋率 = 100%
- [ ] 所有測試通過
- [ ] 測試可在 Docker 環境中獨立執行

## 🐛 偵錯

### 常見問題

**Q: 測試失敗,顯示資料庫連線錯誤**
```bash
# 確保測試環境配置正確
# 檢查 app/config.py 中的 testing 配置
```

**Q: 認證測試失敗**
```bash
# 確認測試資料庫已正確初始化
# 檢查 conftest.py 中的使用者 fixtures
```

**Q: 測試執行緩慢**
```bash
# 使用 -n auto 啟用並行測試
uv run pytest tests/ -n auto
```

## 📚 參考文檔

- [OpenAPI 規格](../openapi.yaml)
- [重構計劃](../../../docs/refactoring_plan.md)
- [Linus 重構原則](../../../docs/linus-refactor-principle.md)

## 🎯 下一步

1. **Task 0.3**: 整合測試到 CI/CD
2. **Task 0.4**: Tech Lead 驗證安全網完整性
3. **Phase 1**: 開始領域模型重構

---

**最後更新**: 2025-11-03
**負責人**: Backend + QA Team
**狀態**: Phase 0 - Task 0.2 進行中 🚧
