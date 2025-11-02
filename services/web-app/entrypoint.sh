#!/bin/sh

# 設置 -e 選項，讓腳本在任何指令失敗時立即退出
set -e

# 讓 Flask-Migrate 執行資料庫遷移
echo "Applying database migrations..."
flask db upgrade

# 執行傳遞給此腳本的任何命令 (來自 docker-compose 的 command)
# exec 會用指定的命令替換當前的 shell 進程，
# 這確保了應用程式能成為容器的主進程 (PID 1)，並能正確接收信號。
exec "$@"
