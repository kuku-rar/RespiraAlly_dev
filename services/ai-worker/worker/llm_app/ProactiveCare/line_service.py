import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class LineService:
    def __init__(self):
        self.access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
        self.push_url = "https://api.line.me/v2/bot/message/push"
        if not self.access_token:
            print("⚠️ [Line Service] LINE_CHANNEL_ACCESS_TOKEN 未設定，推送功能將不可用。")

    def push_text_message(self, line_user_id: str, text: str) -> bool:
        """對指定使用者推送一則文字訊息"""
        if not self.access_token or not text.strip():
            print(f"[LINE Push] 缺少 Token 或訊息為空，跳過發送給 {line_user_id}")
            return False

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {"to": line_user_id, "messages": [{"type": "text", "text": text}]}

        try:
            response = requests.post(self.push_url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ [LINE Push] 成功發送訊息給 {line_user_id}")
                return True
            else:
                print(f"❌ [LINE Push] 發送失敗 (HTTP {response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ [LINE Push] 發送時發生錯誤: {e}")
            return False

# 提供一個方便使用的單例
line_service = LineService()