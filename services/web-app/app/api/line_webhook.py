# services/web-app/app/api/line_webhook.py
"""
LINE Messaging API Webhook 處理端點
接收來自 LINE 平台的 webhook 事件並委派給 LineService 處理
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
import logging

# 創建 Blueprint，使用 'chat' 作為名稱以符合 URL /api/v1/chat/webhook
chat_bp = Blueprint('chat', __name__, url_prefix='/api/v1/chat')

logger = logging.getLogger(__name__)

@chat_bp.route('/webhook', methods=['POST'])
@swag_from({
    'summary': 'LINE Messaging API Webhook',
    'description': '接收來自 LINE 平台的 webhook 事件（訊息、關注、取消關注等）',
    'tags': ['LINE Webhook'],
    'parameters': [
        {
            'name': 'X-Line-Signature',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'LINE Platform 簽名，用於驗證請求來源'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'LINE webhook 事件內容',
            'schema': {
                'type': 'object',
                'properties': {
                    'destination': {'type': 'string'},
                    'events': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {'description': 'Webhook 處理成功'},
        '400': {'description': '簽名驗證失敗或請求格式錯誤'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def line_webhook():
    """
    處理 LINE Platform 傳來的 Webhook 事件

    LINE Platform 會將使用者的互動事件（如發送訊息、加好友等）
    透過 HTTP POST 請求發送到此端點
    """
    from ..core.line_service import get_line_service

    # 取得請求內容（原始 JSON 字串）
    body = request.get_data(as_text=True)

    # 取得 LINE 的簽名標頭，用於驗證請求確實來自 LINE Platform
    signature = request.headers.get('X-Line-Signature', '')

    if not signature:
        logger.warning("收到沒有 X-Line-Signature 的 webhook 請求")
        return jsonify({
            "error": {
                "code": "MISSING_SIGNATURE",
                "message": "Missing X-Line-Signature header"
            }
        }), 400

    try:
        # 使用 LineService 處理 webhook
        # handle_webhook 會驗證簽名並觸發相應的事件處理器
        line_service = get_line_service()
        line_service.handle_webhook(body, signature)

        logger.info("LINE webhook 處理成功")
        return jsonify({"status": "OK"}), 200

    except Exception as e:
        logger.error(f"處理 LINE webhook 時發生錯誤: {e}", exc_info=True)
        return jsonify({
            "error": {
                "code": "WEBHOOK_PROCESSING_ERROR",
                "message": "Failed to process webhook"
            }
        }), 500

@chat_bp.route('/webhook', methods=['GET'])
@swag_from({
    'summary': 'LINE Webhook 健康檢查',
    'description': '用於驗證 webhook 端點是否可訪問',
    'tags': ['LINE Webhook'],
    'responses': {
        '200': {'description': 'Webhook 端點正常運作'}
    }
})
def line_webhook_health():
    """
    Webhook 健康檢查端點
    LINE Platform 可能會發送 GET 請求來驗證端點是否可訪問
    """
    return jsonify({
        "status": "OK",
        "service": "LINE Webhook",
        "endpoint": "/api/v1/chat/webhook"
    }), 200
