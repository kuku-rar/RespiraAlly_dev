#!/bin/bash
# 一鍵修復當前靜態文件問題

set -e

echo "🚨 執行緊急靜態文件修復..."
echo "📍 當前目錄: $(pwd)"

# 檢查是否在正確的專案根目錄
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ 錯誤：請在專案根目錄執行此腳本"
    echo "💡 正確路徑應包含 docker-compose.dev.yml"
    exit 1
fi

# 1. 強制重建前端
echo "🔨 步驟 1: 強制重建前端..."
cd services/web-app/frontend

# 清理所有快取
rm -rf dist .vite node_modules/.vite

# 獲取版本資訊
VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
BUILD_TIME=$(date -u +"%Y%m%d_%H%M%S")

echo "📦 構建版本: ${VERSION}-${BUILD_TIME}"

# 設定構建環境變數
export VITE_APP_VERSION="${VERSION}"
export VITE_BUILD_TIME="${BUILD_TIME}"

# 構建
npm run build

# 2. 驗證關鍵文件存在
echo "🔍 步驟 2: 驗證構建結果..."
if [ ! -f "dist/index.html" ]; then
    echo "❌ 構建失敗：index.html 不存在"
    exit 1
fi

# 3. 加入版本標記到 index.html（便於追蹤）
echo "🏷️ 步驟 3: 加入版本標記..."
if grep -q "build-version" dist/index.html; then
    echo "⚠️ 版本標記已存在，跳過"
else
    # 在 <title> 前加入 meta 標籤
    sed -i.bak "s/<title>/<meta name=\"build-version\" content=\"${VERSION}-${BUILD_TIME}\"><title>/" dist/index.html
    echo "✅ 版本標記已加入: ${VERSION}-${BUILD_TIME}"
fi

# 4. 回到專案根目錄
cd ../../../

# 5. 重啟相關容器
echo "🔄 步驟 4: 重啟容器..."
echo "⏳ 重啟 web-app 容器..."
docker-compose -f docker-compose.dev.yml restart web-app

echo "⏳ 重啟 nginx 容器..."
docker-compose -f docker-compose.dev.yml restart nginx

# 6. 等待容器啟動
echo "⏳ 等待容器啟動..."
sleep 8

# 7. 驗證服務狀態
echo "🔍 步驟 5: 驗證服務狀態..."

# 檢查容器狀態
echo "📋 容器狀態:"
docker-compose -f docker-compose.dev.yml ps web-app nginx

# 驗證 Flask 應用
echo "🌐 測試 Flask 健康狀態..."
if curl -s -f "http://localhost:5000/api/v1/overview/health" >/dev/null 2>&1; then
    echo "✅ Flask 應用正常"
else
    echo "⚠️ Flask 應用可能未完全啟動，請稍後再試"
fi

# 驗證 nginx
echo "🌐 測試 nginx 代理..."
if curl -s -f "http://localhost/" >/dev/null 2>&1; then
    echo "✅ nginx 代理正常"
else
    echo "⚠️ nginx 可能未完全啟動"
fi

# 8. 顯示版本資訊
echo "📄 步驟 6: 檢查部署版本..."
if curl -s "http://localhost/" | grep -o 'build-version[^>]*' | head -1; then
    echo "✅ 版本標記已正確部署"
else
    echo "⚠️ 無法讀取版本標記，但不影響功能"
fi

echo ""
echo "🎉 緊急修復完成！"
echo "📊 摘要:"
echo "   🏷️ 版本: ${VERSION}-${BUILD_TIME}"
echo "   📁 靜態文件: services/web-app/frontend/dist/"
echo "   🌐 測試 URL: http://localhost/"
echo ""
echo "🔍 如果仍有問題，請檢查："
echo "   1. docker-compose logs web-app"
echo "   2. docker-compose logs nginx"  
echo "   3. 瀏覽器開發者工具 Network 頁籤"