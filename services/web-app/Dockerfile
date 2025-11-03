# ===============================================
# 建置 Python 後端
# ===============================================
FROM python:3.11-slim AS backend

# 設定工作目錄
WORKDIR /usr/src/app

# 安裝系統依賴（包含編譯工具）
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 設定 entrypoint.sh 執行權限
RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 5000

# 明確指定使用 shell 執行 entrypoint
ENTRYPOINT ["/bin/sh", "/usr/src/app/entrypoint.sh"]

# CMD 提供容器的預設啟動命令。
# 這個命令會被 docker-compose.yml 中的 'command' 指令覆蓋。
# 我們將其設定為生產環境的啟動命令作為一個合理的預設值。
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "1", "--bind", "0.0.0.0:5000", "wsgi:app"]
