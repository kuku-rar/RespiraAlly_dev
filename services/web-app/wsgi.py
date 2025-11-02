# services/web-app/wsgi.py

import os
from dotenv import load_dotenv

# 在應用程式啟動前載入 .env 檔案
# 這確保 os.getenv() 能讀取到 .flaskenv 或 .env 中的變數
dotenv_path = os.path.join(os.path.dirname(__file__), '.flaskenv')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app.app import create_app
from app.extensions import socketio
from app.core.notification_service import start_notification_listener

# 建立 Flask app instance
# 使用環境變數 FLASK_CONFIG 來決定要載入的設定，預設為 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')
app, socketio = create_app(config_name)

if __name__ == '__main__':
    # 啟動背景的 RabbitMQ 監聽器，並傳入 app 實例
    start_notification_listener(app)
    # 使用 socketio.run 來啟動伺服器，這樣才能支援 WebSocket
    socketio.run(app, host='0.0.0.0', port=5000)
