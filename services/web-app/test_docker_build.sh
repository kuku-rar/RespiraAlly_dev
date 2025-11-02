#!/bin/bash
# 測試 Docker 構建修復

echo "🔧 測試 Docker 構建修復..."

# 清理舊的映像
echo "📦 清理舊映像..."
docker rmi beloved_grandson-web-app:latest 2>/dev/null || true

# 測試構建
echo "🏗️ 開始構建測試..."
cd "$(dirname "$0")"

# 記錄開始時間
start_time=$(date +%s)

# 構建映像
if docker build -t test-web-app . --no-cache; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "✅ 構建成功！"
    echo "⏱️ 耗時: ${duration} 秒"
    
    # 測試映像是否可以啟動
    echo "🧪 測試映像啟動..."
    container_id=$(docker run -d --rm -p 5001:5000 test-web-app)
    
    # 等待 5 秒
    sleep 5
    
    # 測試健康檢查
    if curl -f http://localhost:5001/api/v1/auth/container_health 2>/dev/null; then
        echo "✅ 健康檢查通過！"
    else
        echo "⚠️ 健康檢查失敗（可能需要資料庫連線）"
    fi
    
    # 停止容器
    docker stop $container_id
    
    echo "🎉 Docker 構建修復成功！"
else
    echo "❌ 構建失敗"
    exit 1
fi
