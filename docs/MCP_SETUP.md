# MCP (Model Context Protocol) 設置指南

> **更新時間**: 2025-11-03
> **專案**: RespiraAlly V1

## 📋 概述

本專案使用 MCP (Model Context Protocol) 整合多個外部服務和工具，提供增強的開發體驗。

## 🔧 已配置的 MCP 伺服器

| 伺服器 | 功能 | 需要 API Key |
|--------|------|--------------|
| **brave-search** | Brave 搜尋引擎 API | ✅ 是 |
| **context7** | Upstash Context7 服務 | ✅ 是 |
| **github** | GitHub API 整合 | ✅ 是 |
| **playwright** | 瀏覽器自動化測試 | ❌ 否 |
| **chrome-devtools** | Chrome DevTools 整合 | ❌ 否 |
| **reactbits** | React 開發工具 | ❌ 否 |
| **Figma** | Figma 設計工具整合 | ❌ 否 |
| **zeabur** | Zeabur 部署平台 | ✅ 是 |

## 🚀 快速開始

### 1. 複製 MCP 配置範本

```bash
cp .mcp.json.example .mcp.json
```

### 2. 設置環境變數

在專案根目錄的 `.env` 文件中添加以下 MCP 相關的環境變數：

```env
# ================================
# MCP (Model Context Protocol) 配置
# ================================

# Brave Search API
BRAVE_API_KEY=your_brave_api_key_here

# Context7 (Upstash) API
CONTEXT7_API_KEY=your_context7_api_key_here

# GitHub Personal Access Token
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here

# Zeabur Deployment Token
ZEABUR_TOKEN=your_zeabur_token_here
```

### 3. 獲取 API Keys

#### Brave Search API
1. 訪問 [Brave Search API](https://brave.com/search/api/)
2. 註冊並獲取 API key

#### Context7 (Upstash)
1. 訪問 [Upstash Console](https://console.upstash.com/)
2. 創建 Context7 項目並獲取 API key

#### GitHub Personal Access Token
1. 訪問 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 創建新的 token，需要以下權限：
   - `repo` - 完整的倉庫訪問權限
   - `workflow` - 工作流程訪問權限

#### Zeabur Token
1. 訪問 [Zeabur Dashboard](https://zeabur.com/)
2. 在設置中生成部署 token

## 📁 文件結構

```
.
├── .mcp.json              # MCP 配置文件（包含敏感資訊，不提交到 Git）
├── .mcp.json.example      # MCP 配置範本（可提交到 Git）
├── .env                   # 環境變數文件（包含 API keys，不提交到 Git）
└── docs/
    └── MCP_SETUP.md       # 本說明文件
```

## ⚠️ 安全注意事項

1. **絕不提交敏感資訊**
   - `.mcp.json` 和 `.env` 已在 `.gitignore` 中
   - 確保 API keys 不會被意外提交

2. **定期更新 API Keys**
   - 定期輪換 API keys 以提高安全性
   - 如果 key 洩露，立即撤銷並重新生成

3. **最小權限原則**
   - 只授予必要的權限給 API keys
   - 限制 token 的訪問範圍

## 🔍 驗證配置

確認 MCP 配置是否正確：

```bash
# 檢查配置文件格式
cat .mcp.json | python3 -m json.tool

# 檢查環境變數
grep "MCP" .env
```

## 🐛 故障排除

### MCP 伺服器無法啟動

1. **檢查 Node.js 版本**
   ```bash
   node --version  # 應該 >= 18.x
   npm --version
   ```

2. **檢查環境變數**
   ```bash
   # 確認環境變數已加載
   source .env
   echo $BRAVE_API_KEY
   ```

3. **清除 npm 緩存**
   ```bash
   npx clear-npx-cache
   ```

### API Key 無效

- 確認 API key 沒有過期
- 檢查 key 的權限設置
- 確認環境變數名稱正確（區分大小寫）

## 📚 參考資源

- [MCP 官方文檔](https://modelcontextprotocol.io/)
- [Claude Code MCP 指南](https://docs.claude.com/en/docs/claude-code/mcp)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Chrome DevTools MCP](https://github.com/chrome-devtools-mcp)

## 🆘 需要幫助？

如遇到問題，請：
1. 查看本文件的故障排除部分
2. 檢查 Claude Code 日誌
3. 參考官方文檔
4. 在專案 issue tracker 提出問題

---

**最後更新**: 2025-11-03
**維護者**: RespiraAlly 開發團隊
