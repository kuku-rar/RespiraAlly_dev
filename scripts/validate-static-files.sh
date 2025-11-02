#!/bin/bash
# 完整驗證腳本 - 靜態文件系統測試

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 開始靜態文件系統驗證...${NC}"

# 測試配置
BASE_URL="http://localhost"
EXPECTED_VERSION_PATTERN="build-version.*content="
TEST_RESULTS=()

# 輔助函數
log_test() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name: $message${NC}"
        TEST_RESULTS+=("PASS")
    elif [ "$result" = "WARN" ]; then
        echo -e "${YELLOW}⚠️ $test_name: $message${NC}"
        TEST_RESULTS+=("WARN")
    else
        echo -e "${RED}❌ $test_name: $message${NC}"
        TEST_RESULTS+=("FAIL")
    fi
}

wait_for_service() {
    local url="$1"
    local timeout=30
    local counter=0
    
    echo -e "${YELLOW}⏳ 等待服務啟動...${NC}"
    
    while [ $counter -lt $timeout ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
        counter=$((counter + 1))
    done
    
    return 1
}

# 1. 基礎可用性測試
echo -e "${BLUE}1️⃣ 測試基礎可用性...${NC}"
if wait_for_service "$BASE_URL/"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
    if [ "$HTTP_CODE" = "200" ]; then
        log_test "基礎可用性" "PASS" "應用程式正常回應 ($HTTP_CODE)"
    else
        log_test "基礎可用性" "FAIL" "HTTP 狀態異常 ($HTTP_CODE)"
    fi
else
    log_test "基礎可用性" "FAIL" "應用程式無法存取 (超時)"
fi

# 2. 版本標記測試
echo -e "${BLUE}2️⃣ 測試版本標記...${NC}"
HTML_CONTENT=$(curl -s "$BASE_URL/" 2>/dev/null || echo "")
if echo "$HTML_CONTENT" | grep -q "$EXPECTED_VERSION_PATTERN"; then
    VERSION=$(echo "$HTML_CONTENT" | grep -o 'build-version[^>]*' | head -1 | cut -d'"' -f2)
    log_test "版本標記" "PASS" "版本標記正確: $VERSION"
else
    log_test "版本標記" "WARN" "版本標記缺失（不影響核心功能）"
fi

# 3. 靜態文件服務來源測試
echo -e "${BLUE}3️⃣ 測試靜態文件服務來源...${NC}"
# 嘗試獲取任何靜態資源
STATIC_TEST_URLS=(
    "$BASE_URL/assets/index.css"
    "$BASE_URL/assets/index.js" 
    "$BASE_URL/js/"
    "$BASE_URL/css/"
)

NGINX_SERVED=false
for test_url in "${STATIC_TEST_URLS[@]}"; do
    HEADERS=$(curl -I -s "$test_url" 2>/dev/null || echo "")
    if echo "$HEADERS" | grep -qi "x-served-by.*nginx"; then
        NGINX_SERVED=true
        break
    fi
done

if [ "$NGINX_SERVED" = true ]; then
    log_test "靜態文件來源" "PASS" "靜態文件由 nginx 直接服務"
else
    # 檢查是否至少能存取靜態文件
    if curl -f -s "$BASE_URL/assets/" > /dev/null 2>&1 || curl -f -s "$BASE_URL/static/" > /dev/null 2>&1; then
        log_test "靜態文件來源" "WARN" "靜態文件可能由 Flask 服務（性能次優）"
    else
        log_test "靜態文件來源" "FAIL" "無法存取任何靜態文件"
    fi
fi

# 4. 快取標頭測試
echo -e "${BLUE}4️⃣ 測試快取標頭...${NC}"
CACHE_TEST_PASSED=false

for test_url in "${STATIC_TEST_URLS[@]}"; do
    CACHE_HEADERS=$(curl -I -s "$test_url" 2>/dev/null | grep -i cache-control || echo "")
    if echo "$CACHE_HEADERS" | grep -q -E "public|max-age|immutable"; then
        CACHE_TEST_PASSED=true
        log_test "快取標頭" "PASS" "快取標頭正確設置: $(echo "$CACHE_HEADERS" | tr -d '\r')"
        break
    fi
done

if [ "$CACHE_TEST_PASSED" = false ]; then
    log_test "快取標頭" "WARN" "快取標頭未正確設置（影響性能）"
fi

# 5. API 路由測試
echo -e "${BLUE}5️⃣ 測試 API 路由...${NC}"
API_ENDPOINTS=(
    "$BASE_URL/api/v1/overview/health"
    "$BASE_URL/api/v1/overview/kpi"
    "$BASE_URL/api/"
)

API_WORKING=false
for endpoint in "${API_ENDPOINTS[@]}"; do
    if curl -f -s "$endpoint" > /dev/null 2>&1; then
        API_WORKING=true
        log_test "API 路由" "PASS" "API 端點正常: $endpoint"
        break
    fi
done

if [ "$API_WORKING" = false ]; then
    log_test "API 路由" "FAIL" "所有 API 端點皆無法存取"
fi

# 6. 建構資訊測試
echo -e "${BLUE}6️⃣ 測試建構資訊...${NC}"
if curl -f -s "$BASE_URL/build-info.json" > /dev/null 2>&1; then
    BUILD_INFO=$(curl -s "$BASE_URL/build-info.json" 2>/dev/null)
    if echo "$BUILD_INFO" | grep -q "version"; then
        VERSION=$(echo "$BUILD_INFO" | grep -o '"version"[^,]*' | cut -d'"' -f4)
        log_test "建構資訊" "PASS" "建構資訊可存取，版本: $VERSION"
    else
        log_test "建構資訊" "WARN" "建構資訊格式異常"
    fi
else
    log_test "建構資訊" "WARN" "建構資訊端點不存在（不影響核心功能）"
fi

# 7. Docker 容器狀態測試
echo -e "${BLUE}7️⃣ 測試 Docker 容器狀態...${NC}"
if command -v docker-compose >/dev/null 2>&1; then
    if [ -f "docker-compose.dev.yml" ]; then
        WEB_STATUS=$(docker-compose -f docker-compose.dev.yml ps web-app 2>/dev/null | grep -E "(Up|running)" || echo "")
        NGINX_STATUS=$(docker-compose -f docker-compose.dev.yml ps nginx 2>/dev/null | grep -E "(Up|running)" || echo "")
        
        if [ -n "$WEB_STATUS" ] && [ -n "$NGINX_STATUS" ]; then
            log_test "Docker 容器" "PASS" "核心容器正常運行"
        else
            log_test "Docker 容器" "WARN" "部分容器狀態異常"
        fi
    else
        log_test "Docker 容器" "WARN" "找不到 docker-compose 配置檔"
    fi
else
    log_test "Docker 容器" "WARN" "無法執行 docker-compose 命令"
fi

# 8. 效能測試（簡化版）
echo -e "${BLUE}8️⃣ 測試載入效能...${NC}"
LOAD_TIME=$(curl -w "%{time_total}" -o /dev/null -s "$BASE_URL/" 2>/dev/null || echo "999")
LOAD_TIME_INT=$(printf "%.0f" "$LOAD_TIME" 2>/dev/null || echo "999")

if [ "$LOAD_TIME_INT" -lt 5 ]; then
    log_test "載入效能" "PASS" "首頁載入時間: ${LOAD_TIME}秒"
elif [ "$LOAD_TIME_INT" -lt 10 ]; then
    log_test "載入效能" "WARN" "首頁載入較慢: ${LOAD_TIME}秒"
else
    log_test "載入效能" "FAIL" "首頁載入過慢: ${LOAD_TIME}秒"
fi

# 統計結果
echo ""
echo -e "${BLUE}📊 測試結果統計:${NC}"
TOTAL_TESTS=${#TEST_RESULTS[@]}
PASS_COUNT=$(printf '%s\n' "${TEST_RESULTS[@]}" | grep -c "PASS" || echo "0")
WARN_COUNT=$(printf '%s\n' "${TEST_RESULTS[@]}" | grep -c "WARN" || echo "0") 
FAIL_COUNT=$(printf '%s\n' "${TEST_RESULTS[@]}" | grep -c "FAIL" || echo "0")

echo -e "   ✅ 通過: ${GREEN}$PASS_COUNT${NC}"
echo -e "   ⚠️ 警告: ${YELLOW}$WARN_COUNT${NC}"
echo -e "   ❌ 失敗: ${RED}$FAIL_COUNT${NC}"
echo -e "   📝 總計: $TOTAL_TESTS 項測試"

# 整體評估
if [ "$FAIL_COUNT" -eq 0 ] && [ "$WARN_COUNT" -eq 0 ]; then
    echo -e "${GREEN}🎉 系統狀態: 優秀！所有測試都通過${NC}"
    exit 0
elif [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}✅ 系統狀態: 良好，有輕微警告但不影響核心功能${NC}"
    exit 0
elif [ "$FAIL_COUNT" -lt 3 ]; then
    echo -e "${YELLOW}⚠️ 系統狀態: 需要關注，有部分功能異常${NC}"
    exit 1
else
    echo -e "${RED}🚨 系統狀態: 嚴重問題，需要立即修復${NC}"
    exit 2
fi