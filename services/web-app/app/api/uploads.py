# services/web-app/app/api/uploads.py

from flask import Blueprint, jsonify, request
from app.core import minio_service
from flasgger import swag_from

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/audio/request-url', methods=['POST'])
@swag_from({
    'summary': '請求音檔上傳的預簽章 URL',
    'description': '向伺服器請求一個有時效性的 URL，供客戶端直接將音檔上傳至 MinIO 物件儲存。',
    'tags': ['Uploads'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'id': 'UploadRequest',
                'properties': {
                    'filename': {
                        'type': 'string',
                        'description': '可選的檔案名稱。如果未提供，伺服器將生成一個唯一的名稱。',
                        'example': 'my-awesome-speech.wav'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': '成功生成預簽章 URL',
            'schema': {
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': '用於上傳的預簽章 URL (HTTP PUT)',
                        'example': 'http://minio:9000/audio-uploads/...'
                    },
                    'object_name': {
                        'type': 'string',
                        'description': '檔案在儲存桶中的最終名稱',
                        'example': 'audio-1234abcd.wav'
                    }
                }
            }
        },
        '500': {
            'description': '伺服器無法生成 URL'
        }
    }
})
def request_audio_upload_url():
    """請求音檔上傳 URL"""
    data = request.get_json()
    filename = data.get('filename') if data else None

    bucket_name = 'audio-uploads'
    result = minio_service.generate_presigned_upload_url(
        bucket_name=bucket_name,
        object_name=filename
    )

    if not result:
        return jsonify({"error": "Could not generate presigned URL"}), 500

    return jsonify(result), 200
