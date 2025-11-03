# services/web-app/create_rich_menus.py
import os
import sys
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    URIAction,
)

# ---

# 從專案根目錄的 .env 檔案載入環境變數
# __file__ 是當前檔案的路徑
# os.path.dirname(__file__) 是當前檔案所在的目錄
# os.path.join(...) 用於安全地組合路徑
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# 讀取 LINE Channel Access Token
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
if not CHANNEL_ACCESS_TOKEN:
    print("錯誤：在 .env 檔案中找不到 LINE_CHANNEL_ACCESS_TOKEN", file=sys.stderr)
    sys.exit(1)

# 讀取 LIFF Channel ID
LIFF_CHANNEL_ID = os.getenv('LIFF_CHANNEL_ID')
if not LIFF_CHANNEL_ID:
    print("警告：在 .env 檔案中找不到 LIFF_CHANNEL_ID，選單連結可能不完整。", file=sys.stderr)

# 初始化 line-bot-sdk 的設定
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# ---

# 選單 A: 訪客選單 (Guest Menu)
GUEST_MENU = {
    "size": {"width": 2500, "height": 843},
    "selected": True,
    "name": "Guest Menu",
    "chatBarText": "點我註冊",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": 2500, "height": 843},
            "action": {"type": "uri", "uri": f"https://liff.line.me/{LIFF_CHANNEL_ID}/register"}
        }
    ]
}

# 選單 B: 會員選單 (Member Menu)
MEMBER_MENU = {
    "size": {"width": 2500, "height": 843},
    "selected": True,
    "name": "Member Menu",
    "chatBarText": "選擇功能",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
            "action": {"type": "uri", "uri": f"https://liff.line.me/{LIFF_CHANNEL_ID}/voice-chat"}
        },
        {
            "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},
            "action": {"type": "uri", "uri": f"https://liff.line.me/{LIFF_CHANNEL_ID}/daily-metrics"}
        },
        {
            "bounds": {"x": 1667, "y": 0, "width": 833, "height": 843},
            "action": {"type": "uri", "uri": f"https://liff.line.me/{LIFF_CHANNEL_ID}/questionnaire/cat"}
        }
    ]
}

# ---

def create_rich_menu(api: MessagingApi, menu_definition: dict) -> str:
    """使用 line-bot-sdk 建立圖文選單並回傳其 ID。"""
    print(f"正在建立圖文選單: {menu_definition['name']}...")

    # 將字典中的 area 定義轉換為 RichMenuArea 物件列表
    areas = [
        RichMenuArea(
            bounds=RichMenuBounds(
                x=area['bounds']['x'],
                y=area['bounds']['y'],
                width=area['bounds']['width'],
                height=area['bounds']['height']
            ),
            action=URIAction(uri=area['action']['uri'])
        ) for area in menu_definition['areas']
    ]

    # 建立 RichMenuRequest 物件
    rich_menu_request = RichMenuRequest(
        size=RichMenuSize(
            width=menu_definition['size']['width'],
            height=menu_definition['size']['height']
        ),
        selected=menu_definition['selected'],
        name=menu_definition['name'],
        chat_bar_text=menu_definition['chatBarText'],
        areas=areas
    )

    # 呼叫 API 建立選單
    rich_menu_id = api.create_rich_menu(rich_menu_request=rich_menu_request).rich_menu_id
    print(f"成功建立選單。Rich Menu ID: {rich_menu_id}")
    return rich_menu_id

def upload_rich_menu_image(blob_api: MessagingApiBlob, rich_menu_id: str, image_path: str):
    """為指定的圖文選單上傳圖片。"""
    print(f"正在為 Rich Menu ID: {rich_menu_id} 上傳圖片 '{image_path}'...")

    # 確保圖片檔案存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"圖片檔案不存在: {image_path}")

    with open(image_path, 'rb') as f:
        blob_api.set_rich_menu_image(
            rich_menu_id=rich_menu_id,
            body=bytearray(f.read()),
            _headers={'Content-Type': 'image/png'}
        )
    print("圖片上傳成功。")

def set_default_rich_menu(api: MessagingApi, rich_menu_id: str):
    """將指定的圖文選單設為預設。"""
    print(f"正在將 Rich Menu ID {rich_menu_id} 設為預設...")
    api.set_default_rich_menu(rich_menu_id=rich_menu_id)
    print("預設圖文選單設定成功。")

def main():
    """主執行函式。"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_blob_api = MessagingApiBlob(api_client)

            # ---
            guest_menu_id = create_rich_menu(line_bot_api, GUEST_MENU)
            upload_rich_menu_image(line_bot_blob_api, guest_menu_id, 'rich_menu_guest.png')

            # ---
            member_menu_id = create_rich_menu(line_bot_api, MEMBER_MENU)
            upload_rich_menu_image(line_bot_blob_api, member_menu_id, 'rich_menu_member.png')

            # ---
            set_default_rich_menu(line_bot_api, guest_menu_id)

            print("\n--- ")
            print("請將以下這幾行更新到你的 .env 檔案中:")
            print(f"LINE_RICH_MENU_ID_GUEST={guest_menu_id}")
            print(f"LINE_RICH_MENU_ID_MEMBER={member_menu_id}")

    except Exception as e:
        print(f"\n--- ", file=sys.stderr)
        print(f"錯誤類型: {type(e).__name__}", file=sys.stderr)
        print(f"錯誤訊息: {e}", file=sys.stderr)
        # 如果是 API 錯誤，嘗試印出更詳細的資訊
        if hasattr(e, 'body'):
            print(f"伺服器回應內容: {e.body}", file=sys.stderr)

# ---
if __name__ == '__main__':
    print("--- LINE ")
    print("重要：請確保 'rich_menu_guest.png' 和 'rich_menu_member.png' 兩個圖片檔與此腳本在同一個目錄下。")

    # 取得腳本所在的目錄
    script_dir = os.path.dirname(__file__)
    # 將工作目錄切換到腳本所在的目錄，以確保相對路徑正確
    os.chdir(script_dir)

    main()
