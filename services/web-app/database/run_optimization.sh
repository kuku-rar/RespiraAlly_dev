#!/bin/bash

# RespiraAlly 資料庫優化腳本
# 此腳本用於執行所有資料庫優化

set -e  # 遇到錯誤立即停止

echo "=========================================="
echo "RespiraAlly 資料庫優化腳本"
echo "=========================================="

# 設定資料庫連線參數
DB_USER="${POSTGRES_APP_USER:-respirally}"
DB_NAME="${POSTGRES_APP_DB:-respirally}"
DB_HOST="${DATABASE_HOST:-postgres}"

echo "資料庫連線資訊："
echo "  使用者: $DB_USER"
echo "  資料庫: $DB_NAME"
echo "  主機: $DB_HOST"
echo ""

# 檢查 PostgreSQL 客戶端是否安裝
if ! command -v psql &> /dev/null; then
    echo "錯誤：找不到 psql 命令"
    echo "請確保您在 web-app 容器內執行此腳本"
    exit 1
fi

# 取得腳本所在目錄
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 執行優化腳本
echo "執行索引優化..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f "$SCRIPT_DIR/optimization/add_indexes.sql"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 優化完成！"
    echo ""
    echo "後續步驟："
    echo "1. 確認應用程式已設定排程任務（scheduled_jobs.py）"
    echo "2. 物化視圖將每 30 分鐘自動刷新"
    echo "3. 可執行以下命令手動刷新物化視圖："
    echo "   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'SELECT refresh_materialized_views();'"
else
    echo ""
    echo "❌ 優化失敗，請檢查錯誤訊息"
    exit 1
fi
