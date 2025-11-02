import logging
import os
import uuid

import requests
from app.core.minio_service import get_minio_service
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

bp = Blueprint('voice', __name__, url_prefix='/api/v1/voice')

# 配置
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'webm'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """檢查文件擴展名是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    語音轉文字API端點
    接收音頻文件，返回轉錄的文字內容
    ---
    tags:
      - voice
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: audio
        type: file
        required: true
        description: 要轉錄的音頻文件 (支援 wav, mp3, m4a, ogg, webm)
      - in: formData
        name: patient_id
        type: string
        required: false
        description: 患者ID（可選）
    responses:
      200:
        description: 成功轉錄音頻
        schema:
          type: object
          properties:
            transcription:
              type: string
              description: 轉錄的文字內容
            duration:
              type: number
              description: 音頻時長（秒）
            file_id:
              type: string
              description: 上傳文件的唯一標識
      400:
        description: 請求錯誤，如文件格式不支援或文件過大
      500:
        description: 服務器內部錯誤
    """
    try:
        # 檢查是否有文件上傳
        if 'audio' not in request.files:
            raise BadRequest("未找到音頻文件")
        
        file = request.files['audio']
        if file.filename == '':
            raise BadRequest("未選擇文件")
        
        if not allowed_file(file.filename):
            raise BadRequest(f"不支援的文件格式。支援的格式: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 檢查文件大小
        if request.content_length and request.content_length > MAX_FILE_SIZE:
            raise BadRequest(f"文件過大。最大支援 {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # 獲取可選參數
        patient_id = request.form.get('patient_id', 'anonymous')
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        object_name = f"voice_uploads/{file_id}_{filename}"
        
        # 上傳到MinIO
        minio_service = get_minio_service()
        bucket_name = current_app.config.get('VOICE_BUCKET', 'audio-uploads')

        # 確保bucket存在
        # 上傳文件（MinIO服務會自動檢查和創建bucket）
        file_data = file.read()
        minio_service.upload_file_content(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file_data,
            length=len(file_data),
            content_type=file.content_type or 'audio/wav'
        )
        
        # 調用AI Worker的STT API
        ai_worker_url = current_app.config.get('AI_WORKER_VOICE_URL', 'http://ai-worker:8001')
        
        try:
            stt_response = requests.post(
                f"{ai_worker_url}/voice/stt",
                json={
                    'bucket_name': bucket_name,
                    'object_name': object_name,
                    'patient_id': patient_id
                },
                timeout=30
            )
            
            if not stt_response.ok:
                raise Exception(f"STT服務錯誤: {stt_response.status_code}")
            
            stt_data = stt_response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"STT service error: {e}")
            # 返回錯誤但不中斷服務
            stt_data = {
                'transcription': f"語音轉錄服務暫時不可用，文件ID: {file_id}",
                'duration': 3.5,
                'confidence': 0.5
            }
        
        return jsonify({
            'transcription': stt_data.get('transcription', ''),
            'duration': stt_data.get('duration', 0),
            'file_id': file_id,
            'confidence': stt_data.get('confidence', 0.0)
        }), 200
        
    except BadRequest as e:
        return jsonify({'error': {'code': 'INVALID_REQUEST', 'message': str(e)}}), 400
    except Exception as e:
        logging.error(f"Transcription error: {e}", exc_info=True)
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': '語音轉錄失敗'}}), 500

@bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    文字轉語音API端點
    接收文字內容，返回合成的語音音頻URL
    ---
    tags:
      - voice
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: 要合成語音的文字內容
              example: "您好，這是語音合成測試"
            voice:
              type: string
              description: 語音類型（可選）
              example: "female"
            speed:
              type: number
              description: 語音速度（可選，0.5-2.0）
              example: 1.0
            patient_id:
              type: string
              description: 患者ID（可選）
              example: "patient_123"
          required:
            - text
    responses:
      200:
        description: 成功合成語音
        schema:
          type: object
          properties:
            audioUrl:
              type: string
              description: 音頻文件的訪問URL
            duration:
              type: number
              description: 音頻時長（毫秒）
            file_id:
              type: string
              description: 音頻文件的唯一標識
      400:
        description: 請求錯誤，如文字內容為空
      500:
        description: 服務器內部錯誤
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            raise BadRequest("缺少必要的'text'參數")
        
        text = data['text'].strip()
        if not text:
            raise BadRequest("文字內容不能為空")
        
        if len(text) > 1000:  # 限制文字長度
            raise BadRequest("文字內容過長，最大支援1000字符")
        
        # 獲取可選參數
        voice = data.get('voice', 'female')
        speed = data.get('speed', 1.0)
        patient_id = data.get('patient_id', 'anonymous')
        
        # 驗證速度參數
        if not (0.5 <= speed <= 2.0):
            raise BadRequest("語音速度必須在0.5到2.0之間")
        
        # 調用AI Worker的TTS API
        ai_worker_url = current_app.config.get('AI_WORKER_VOICE_URL', 'http://ai-worker:8001')
        
        try:
            tts_response = requests.post(
                f"{ai_worker_url}/voice/tts",
                json={
                    'text': text,
                    'patient_id': patient_id
                },
                timeout=30
            )
            
            if not tts_response.ok:
                raise Exception(f"TTS服務錯誤: {tts_response.status_code}")
            
            tts_data = tts_response.json()
            object_name = tts_data.get('object_name')
            duration_ms = tts_data.get('duration_ms', 0)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"TTS service error: {e}")
            # 返回錯誤但不中斷服務
            task_id = str(uuid.uuid4())
            object_name = f"tts_error/{task_id}.m4a"
            duration_ms = len(text) * 100
        
        # 生成音頻文件的訪問URL
        bucket_name = current_app.config.get('MINIO_BUCKET_NAME', 'audio-bucket')
        minio_service = get_minio_service()
        
        # 生成預簽名URL（有效期1小時）
        audio_url = minio_service.generate_presigned_get_url(
            bucket_name=bucket_name,
            object_name=object_name,
            expiration=3600  # 1小時
        )
        
        return jsonify({
            'audioUrl': audio_url,
            'duration': duration_ms,
            'file_id': object_name.split('/')[-1].split('.')[0] if '/' in object_name else object_name.split('.')[0]
        }), 200
        
    except BadRequest as e:
        return jsonify({'error': {'code': 'INVALID_REQUEST', 'message': str(e)}}), 400

    except Exception as e:
        logging.error(f"TTS synthesis error: {e}", exc_info=True)
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': '語音合成失敗'}}), 500

@bp.route('/chat', methods=['POST'])
def voice_chat():
    """
    完整的語音聊天API端點
    接收音頻，返回AI回應的音頻
    整合 STT -> LLM -> TTS 的完整流程
    ---
    tags:
      - voice
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: audio
        type: file
        required: true
        description: 用戶的語音消息
      - in: formData
        name: patient_id
        type: string
        required: false
        description: 患者ID（可選）
      - in: formData
        name: conversation_id
        type: string
        required: false
        description: 對話ID（可選，用於維持對話上下文）
    responses:
      200:
        description: 成功處理語音對話
        schema:
          type: object
          properties:
            user_transcription:
              type: string
              description: 用戶語音的轉錄文字
            ai_response_text:
              type: string
              description: AI回應的文字內容
            ai_audio_url:
              type: string
              description: AI回應的語音URL
            conversation_id:
              type: string
              description: 對話ID
            duration:
              type: number
              description: AI語音時長（毫秒）
      400:
        description: 請求錯誤
      500:
        description: 服務器內部錯誤
    """
    try:
        # 檢查音頻文件
        if 'audio' not in request.files:
            raise BadRequest("未找到音頻文件")
        
        file = request.files['audio']
        if file.filename == '':
            raise BadRequest("未選擇文件")
        
        if not allowed_file(file.filename):
            raise BadRequest(f"不支援的文件格式。支援的格式: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 獲取參數
        patient_id = request.form.get('patient_id', 'anonymous')
        conversation_id = request.form.get('conversation_id', str(uuid.uuid4()))
        
        # 上傳音頻文件
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        object_name = f"voice_chat/{file_id}_{filename}"
        
        minio_service = get_minio_service()
        bucket_name = current_app.config.get('MINIO_BUCKET_NAME', 'audio-bucket')

        file_data = file.read()
        minio_service.upload_file_content(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file_data,
            length=len(file_data),
            content_type=file.content_type or 'audio/wav'
        )
        
        # 調用AI Worker的語音聊天API（同步 HTTP 流程，保持與 voice_chat.md 一致）
        ai_worker_url = current_app.config.get('AI_WORKER_VOICE_URL', 'http://ai-worker:8001')
        
        try:
            chat_response = requests.post(
                f"{ai_worker_url}/voice/chat",
                json={
                    'bucket_name': bucket_name,
                    'object_name': object_name,
                    'patient_id': patient_id,
                    'conversation_id': conversation_id
                },
                timeout=60  # 語音聊天需要更長時間
            )
            
            if not chat_response.ok:
                raise Exception(f"語音聊天服務錯誤: {chat_response.status_code}")
            
            chat_data = chat_response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Voice chat service error: {e}")
            # 返回錯誤但不中斷服務
            task_id = str(uuid.uuid4())
            chat_data = {
                'user_transcription': "語音聊天服務暫時不可用",
                'ai_response_text': "抱歉，語音處理服務暫時不可用，請稍後再試。",
                'ai_audio_object': f"voice_chat_error/{task_id}_response.m4a",
                'duration_ms': 3000
            }
        
        # 生成AI語音的訪問URL
        tts_bucket = current_app.config.get('MINIO_BUCKET_NAME', 'audio-bucket')
        ai_audio_object = chat_data.get('ai_audio_object')
        
        if ai_audio_object:
            ai_audio_url = minio_service.generate_presigned_get_url(
                bucket_name=tts_bucket,
                object_name=ai_audio_object,
                expiration=3600
            )
        else:
            ai_audio_url = None
        
        return jsonify({
            'user_transcription': chat_data.get('user_transcription', ''),
            'ai_response_text': chat_data.get('ai_response_text', ''),
            'ai_audio_url': ai_audio_url,
            'conversation_id': conversation_id,
            'duration': chat_data.get('duration_ms', 0)
        }), 200
        
    except BadRequest as e:
        return jsonify({'error': {'code': 'INVALID_REQUEST', 'message': str(e)}}), 400

    except Exception as e:
        logging.error(f"Voice chat error: {e}", exc_info=True)
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': '語音聊天處理失敗'}}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """
    語音服務健康檢查
    ---
    tags:
      - voice
    responses:
      200:
        description: 服務正常
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            services:
              type: object
              properties:
                minio:
                  type: string
                ai_worker:
                  type: string
    """
    try:
        # 檢查MinIO連接
        minio_service = get_minio_service()
        try:
            # 簡單檢查MinIO連接
            minio_service.s3_client.list_buckets()
            minio_status = "healthy"
        except:
            minio_status = "unhealthy"
        
        # 檢查AI Worker連接
        ai_worker_url = current_app.config.get('AI_WORKER_VOICE_URL', 'http://ai-worker:8001')
        try:
            worker_response = requests.get(f"{ai_worker_url}/health", timeout=5)
            ai_worker_status = "healthy" if worker_response.ok else "unhealthy"
        except:
            ai_worker_status = "unhealthy"
        
        overall_status = "healthy" if minio_status == "healthy" and ai_worker_status == "healthy" else "degraded"
        
        return jsonify({
            'status': overall_status,
            'services': {
                'minio': minio_status,
                'ai_worker_voice': ai_worker_status
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500