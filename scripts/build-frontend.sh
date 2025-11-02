#!/bin/bash
# 版本化前端構建腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 版本化前端構建開始...${NC}"

# 檢查是否在正確目錄
if [ ! -f "services/web-app/frontend/package.json" ]; then
    echo -e "${RED}❌ 錯誤：找不到前端專案${NC}"
    echo -e "${YELLOW}💡 請在專案根目錄執行此腳本${NC}"
    exit 1
fi

# 進入前端目錄
cd services/web-app/frontend

# 獲取版本資訊
VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "local-$(date +%s)")
BUILD_TIME=$(date -u +"%Y%m%d_%H%M%S")
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

echo -e "${BLUE}📋 構建資訊:${NC}"
echo -e "   🏷️  版本: ${GREEN}${VERSION}${NC}"
echo -e "   📅 時間: ${GREEN}${BUILD_TIME}${NC}"
echo -e "   🌿 分支: ${GREEN}${BRANCH}${NC}"

# 清理舊構建
echo -e "${YELLOW}🧹 清理舊構建文件...${NC}"
rm -rf dist .vite node_modules/.vite

# 檢查依賴
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 安裝依賴...${NC}"
    npm ci --prefer-offline --no-audit
fi

# 設定構建環境變數
export VITE_APP_VERSION="${VERSION}"
export VITE_BUILD_TIME="${BUILD_TIME}"
export VITE_GIT_BRANCH="${BRANCH}"

# 構建
echo -e "${BLUE}🔨 開始構建...${NC}"
npm run build

# 驗證構建結果
echo -e "${BLUE}🔍 驗證構建結果...${NC}"

# 檢查必要文件
REQUIRED_FILES=("dist/index.html" "dist/assets")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
        echo -e "${RED}❌ 構建失敗：缺少 ${file}${NC}"
        exit 1
    fi
done

# 統計構建文件
JS_COUNT=$(find dist -name "*.js" -type f | wc -l)
CSS_COUNT=$(find dist -name "*.css" -type f | wc -l)
TOTAL_SIZE=$(du -sh dist | cut -f1)

echo -e "${GREEN}✅ 構建完成！${NC}"
echo -e "${BLUE}📊 構建統計:${NC}"
echo -e "   📄 JavaScript 文件: ${JS_COUNT}"
echo -e "   🎨 CSS 文件: ${CSS_COUNT}"
echo -e "   📁 總大小: ${TOTAL_SIZE}"

# 加入版本標記到 index.html
echo -e "${BLUE}🏷️ 加入版本標記...${NC}"
BUILD_INFO="<!-- Build: ${VERSION}-${BUILD_TIME}, Branch: ${BRANCH} -->"
sed -i.bak "s/<title>/${BUILD_INFO}<title>/" dist/index.html
echo -e "   ✅ 版本標記已加入 index.html"

# 生成構建清單
echo -e "${BLUE}📋 生成構建清單...${NC}"
cat > dist/build-info.json << EOF
{
  "version": "${VERSION}",
  "buildTime": "${BUILD_TIME}",
  "branch": "${BRANCH}",
  "buildTimestamp": $(date +%s),
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)",
  "files": {
    "jsCount": ${JS_COUNT},
    "cssCount": ${CSS_COUNT},
    "totalSize": "${TOTAL_SIZE}"
  }
}
EOF

echo -e "   ✅ 構建清單已生成: dist/build-info.json"

# 回到專案根目錄
cd ../../../

echo -e "${GREEN}🎉 前端構建完成！${NC}"
echo -e "${BLUE}📋 後續步驟:${NC}"
echo -e "   1. 重啟容器: ${YELLOW}docker-compose -f docker-compose.dev.yml restart web-app nginx${NC}"
echo -e "   2. 測試應用: ${YELLOW}curl http://localhost/${NC}"
echo -e "   3. 檢查版本: ${YELLOW}curl http://localhost/build-info.json${NC}"