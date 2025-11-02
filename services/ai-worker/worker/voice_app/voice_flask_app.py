#!/usr/bin/env python3
"""
AI Worker Voice Flask App
Flask應用程式，提供語音處理相關的API端點，基於RabbitMQ任務隊列
"""

import os
import json
import logging
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from voice_worker import get_voice_worker

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建Flask應用
app = Flask(__name__)
CORS(app)  # 啟用CORS

# 可選：僅在需要時從 API 進程啟動 RabbitMQ worker
voice_worker = None
worker_thread = None

def _maybe_start_worker_in_api_process():
    """僅當 VOICE_API_START_WORKER=true 時，在 API 行程內啟動消費者。"""
    try:
        start_flag = os.getenv("VOICE_API_START_WORKER", "false").lower() == "true"
        if not start_flag:
            logger.info("Skipping in-process voice worker (VOICE_API_START_WORKER is not true)")
            return
        global voice_worker, worker_thread
        if worker_thread is None:
            voice_worker = get_voice_worker()
            worker_thread = threading.Thread(target=voice_worker.start_consuming, daemon=True)
            worker_thread.start()
            logger.info("Voice worker thread started inside API process")
    except Exception as e:
        logger.error("Voice worker啟動失敗: %s", e)

@app.before_first_request
def initialize_worker():
    _maybe_start_worker_in_api_process()

@app.route('/')
def root():
    """根端點"""
    return jsonify({
        "message": "AI Worker Voice Flask API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/health')
def health_check():
    """整體健康檢查"""
    try:
        worker_status = "healthy" if voice_worker and voice_worker.connection else "unhealthy"
        
        return jsonify({
            "status": "healthy" if worker_status == "healthy" else "degraded",
            "service": "ai-worker-voice-flask-api",
            "version": "1.0.0",
            "components": {
                "voice_worker": worker_status,
                "rabbitmq": worker_status  # worker狀態反映rabbitmq狀態
            }
        })
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return jsonify({
            "status": "unhealthy",
            "service": "ai-worker-voice-flask-api",
            "error": str(e)
        }), 503

@app.route('/voice/stt', methods=['POST'])
def process_stt():
    """
    處理STT（語音轉文字）請求
    直接調用STT服務，不使用隊列
    """
    try:
        data = request.get_json()
        if not data or 'bucket_name' not in data or 'object_name' not in data:
            return jsonify({
                'error': 'Missing required fields: bucket_name, object_name'
            }), 400
        
        bucket_name = data['bucket_name']
        object_name = data['object_name']
        patient_id = data.get('patient_id', 'anonymous')
        
        # 直接調用STT服務
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from stt_app.stt_service import get_stt_service
        stt_service = get_stt_service()
        transcription = stt_service.transcribe_audio(bucket_name, object_name)
        
        return jsonify({
            'transcription': transcription,
            'duration': 3.5,  # 模擬時長
            'confidence': 0.95,  # 模擬置信度
            'patient_id': patient_id
        })
        
    except Exception as e:
        logger.error("STT processing error: %s", e)
        return jsonify({
            'error': f'STT processing failed: {str(e)}'
        }), 500

@app.route('/voice/tts', methods=['POST'])
def process_tts():
    """
    處理TTS（文字轉語音）請求
    直接調用TTS服務，不使用隊列
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        patient_id = data.get('patient_id', 'anonymous')
        
        if not text.strip():
            return jsonify({
                'error': 'Text content cannot be empty'
            }), 400
        
        # 直接調用TTS服務
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from tts_app.tts_service import get_tts_service
        tts_service = get_tts_service()
        object_name, duration_ms = tts_service.synthesize_text(text)
        
        return jsonify({
            'object_name': object_name,
            'duration_ms': duration_ms,
            'patient_id': patient_id
        })
        
    except Exception as e:
        logger.error("TTS processing error: %s", e)
        return jsonify({
            'error': f'TTS processing failed: {str(e)}'
        }), 500

@app.route('/voice/chat', methods=['POST'])
def process_voice_chat():
    """
    處理完整的語音聊天流程
    STT → LLM → TTS
    """
    try:
        data = request.get_json()
        if not data or 'bucket_name' not in data or 'object_name' not in data:
            return jsonify({
                'error': 'Missing required fields: bucket_name, object_name'
            }), 400
        
        bucket_name = data['bucket_name']
        object_name = data['object_name']
        patient_id = data.get('patient_id', 'anonymous')
        conversation_id = data.get('conversation_id')
        
        # Step 1: STT
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from stt_app.stt_service import get_stt_service
        stt_service = get_stt_service()
        user_transcription = stt_service.transcribe_audio(bucket_name, object_name)
        
        # Step 2: LLM
        ai_response_text = generate_llm_response(user_transcription, patient_id, conversation_id)
        
        # Step 3: TTS
        from tts_app.tts_service import get_tts_service
        tts_service = get_tts_service()
        ai_audio_object, duration_ms = tts_service.synthesize_text(ai_response_text)
        
        return jsonify({
            'user_transcription': user_transcription,
            'ai_response_text': ai_response_text,
            'ai_audio_object': ai_audio_object,
            'duration_ms': duration_ms,
            'conversation_id': conversation_id or 'new_conversation',
            'patient_id': patient_id
        })
        
    except Exception as e:
        logger.error("Voice chat processing error: %s", e)
        return jsonify({
            'error': f'Voice chat processing failed: {str(e)}'
        }), 500

def generate_llm_response(message: str, patient_id: str, conversation_id: str) -> str:
    """
    生成LLM回應（同步版本）
    """
    # 簡化的LLM邏輯，基於關鍵詞回應
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['你好', '哈囉', 'hello', '嗨']):
        return "您好！我是您的AI健康助理，很高興為您服務。請問有什麼可以幫助您的嗎？"
    
    elif any(word in message_lower for word in ['謝謝', '感謝', '謝了']):
        return "不客氣！我很高興能夠幫助您。如果還有其他問題，請隨時告訴我。"
    
    elif any(word in message_lower for word in ['再見', '拜拜', 'bye']):
        return "再見！祝您身體健康，有需要時隨時回來找我。"
    
    elif any(word in message_lower for word in ['頭痛', '痛', '不舒服']):
        return "我理解您感到不適。建議您適當休息，如果症狀持續或加重，請儘快諮詢醫師。"
    
    elif any(word in message_lower for word in ['睡眠', '失眠', '睡不著']):
        return "良好的睡眠很重要。建議建立規律作息，避免睡前使用3C產品，如持續失眠請諮詢醫師。"
    
    elif any(word in message_lower for word in ['運動', '健身']):
        return "規律運動對健康很有益！建議每週至少150分鐘中等強度運動。請根據自己的身體狀況適量運動。"
    
    elif any(word in message_lower for word in ['飲食', '吃', '營養']):
        return "均衡飲食很重要！建議多吃蔬果、適量蛋白質，少糖少油。如有特殊飲食需求，請諮詢營養師。"
    
    else:
        return f"我聽到您說：「{message}」。作為AI健康助理，我建議保持良好生活習慣。如有健康疑慮，請諮詢專業醫師。"

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "API端點不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "服務器內部錯誤"
    }), 500

if __name__ == "__main__":
    host = os.getenv("VOICE_FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("VOICE_FLASK_PORT", "8001"))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    logger.info("啟動AI Worker Voice Flask API on %s:%s", host, port)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )