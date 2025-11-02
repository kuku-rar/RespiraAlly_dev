# services/web-app/app/api/education.py
"""
Education API endpoints for managing COPD education resources
衛教資源管理 API
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.milvus_education_service import get_milvus_education_service
from werkzeug.exceptions import BadRequest
import logging
import pandas as pd
import io

logger = logging.getLogger(__name__)

education_bp = Blueprint('education', __name__, url_prefix='/api/v1/education')

# 初始化 Milvus 服務
milvus_service = get_milvus_education_service()

# 修復 Flask 尾部斜杠重定向導致的 CORS 問題
@education_bp.route('', methods=['GET'])
@education_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得衛教資源列表',
    'description': '取得 COPD 衛教問答資源列表，支援類別篩選和關鍵字搜尋',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'category',
            'in': 'query',
            'required': False,
            'description': '篩選特定類別的衛教資源',
            'schema': {'type': 'string'}
        },
        {
            'name': 'q',
            'in': 'query', 
            'required': False,
            'description': '搜尋關鍵字（一般搜尋）',
            'schema': {'type': 'string'}
        },
        {
            'name': 'limit',
            'in': 'query',
            'required': False,
            'description': '返回結果數量上限',
            'schema': {'type': 'integer', 'default': 100}
        }
    ],
    'responses': {
        '200': {
            'description': '成功取得衛教資源列表',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'category': {'type': 'string'},
                                        'question': {'type': 'string'},
                                        'answer': {'type': 'string'},
                                        'keywords': {'type': 'string'},
                                        'notes': {'type': 'string'}
                                    }
                                }
                            },
                            'total': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        '401': {'description': 'Token 無效或未提供'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def get_education_list():
    """取得衛教資源列表"""
    try:
        category = request.args.get('category')
        search_query = request.args.get('q')
        limit = int(request.args.get('limit', 100))
        
        # 如果有搜尋關鍵字，使用一般查詢（未來可以改為語意搜尋）
        results = milvus_service.get_all(category=category, limit=limit)
        
        # 如果有搜尋關鍵字，進行文字篩選
        if search_query:
            search_lower = search_query.lower()
            results = [
                item for item in results
                if search_lower in item.get('question', '').lower() or
                   search_lower in item.get('answer', '').lower() or
                   search_lower in item.get('keywords', '').lower()
            ]
        
        return jsonify({
            "success": True,
            "data": results,
            "total": len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting education list: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

# 註：語意搜尋功能移至 ai-worker 使用
# web-app 只提供 CRUD 功能給前端衛教卡片管理

@education_bp.route('', methods=['POST'])
@education_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': '新增衛教資源',
    'description': '新增一筆 COPD 衛教問答資源',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['category', 'question', 'answer'],
                'properties': {
                    'category': {
                        'type': 'string',
                        'description': '問答類別',
                        'example': '疾病知識'
                    },
                    'question': {
                        'type': 'string',
                        'description': '問題內容',
                        'example': '什麼是 COPD？'
                    },
                    'answer': {
                        'type': 'string',
                        'description': '回答內容',
                        'example': 'COPD 是慢性阻塞性肺病...'
                    },
                    'keywords': {
                        'type': 'string',
                        'description': '關鍵詞（選填）',
                        'example': 'COPD, 肺病, 呼吸'
                    },
                    'notes': {
                        'type': 'string',
                        'description': '注意事項或補充說明（選填）',
                        'example': '請諮詢醫師'
                    }
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': '成功新增衛教資源',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'message': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': '請求格式錯誤或缺少必要欄位'},
        '401': {'description': 'Token 無效或未提供'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def create_education():
    """新增衛教資源"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Request body is required"
                }
            }), 400
        
        # 驗證必要欄位
        required_fields = ['category', 'question', 'answer']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": f"Field '{field}' is required"
                    }
                }), 400
        
        # 新增到 Milvus
        result = milvus_service.create(data)
        
        return jsonify({
            "success": True,
            "data": result
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating education item: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@education_bp.route('/<int:edu_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'summary': '更新衛教資源',
    'description': '更新指定的 COPD 衛教問答資源',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'edu_id',
            'in': 'path',
            'required': True,
            'description': '衛教資源 ID',
            'schema': {'type': 'integer'}
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'category': {'type': 'string'},
                    'question': {'type': 'string'},
                    'answer': {'type': 'string'},
                    'keywords': {'type': 'string'},
                    'notes': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': '成功更新衛教資源',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'message': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': '請求格式錯誤'},
        '401': {'description': 'Token 無效或未提供'},
        '404': {'description': '找不到指定的衛教資源'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def update_education(edu_id):
    """更新衛教資源"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Request body is required"
                }
            }), 400
        
        # 更新 Milvus 資料
        result = milvus_service.update(edu_id, data)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except ValueError as ve:
        # 找不到資源
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": str(ve)
            }
        }), 404
    except Exception as e:
        logger.error(f"Error updating education item: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@education_bp.route('/<int:edu_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'summary': '刪除衛教資源',
    'description': '刪除指定的 COPD 衛教問答資源',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'edu_id',
            'in': 'path',
            'required': True,
            'description': '衛教資源 ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        '200': {
            'description': '成功刪除衛教資源',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        '401': {'description': 'Token 無效或未提供'},
        '404': {'description': '找不到指定的衛教資源'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def delete_education(edu_id):
    """刪除衛教資源"""
    try:
        result = milvus_service.delete(edu_id)
        
        return jsonify({
            "success": True,
            "message": result.get("message", "Education item deleted successfully")
        }), 200
        
    except ValueError as ve:
        # 找不到資源
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": str(ve)
            }
        }), 404
    except Exception as e:
        logger.error(f"Error deleting education item: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@education_bp.route('/categories', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得所有衛教資源類別',
    'description': '取得系統中所有不重複的衛教資源類別',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '成功取得類別列表',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'array',
                                'items': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': 'Token 無效或未提供'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def get_categories():
    """取得所有衛教資源類別"""
    try:
        categories = milvus_service.get_categories()
        
        return jsonify({
            "success": True,
            "data": categories
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@education_bp.route('/batch', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': '批量匯入衛教資源',
    'description': '從 CSV 或 Excel 檔案批量匯入 COPD 衛教問答資源',
    'tags': ['Education'],
    'security': [{'bearerAuth': []}],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV 或 Excel 檔案（需包含類別、問題、回答等欄位）'
        }
    ],
    'responses': {
        '201': {
            'description': '成功批量匯入',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'imported': {'type': 'integer'},
                            'failed': {'type': 'integer'},
                            'total': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        '400': {'description': '檔案格式錯誤'},
        '401': {'description': 'Token 無效或未提供'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def batch_import():
    """批量匯入衛教資源"""
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "No file provided"
                }
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "No file selected"
                }
            }), 400
        
        # 讀取檔案
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(file.read()))
            else:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Unsupported file format. Please use CSV or Excel."
                    }
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"Error reading file: {str(e)}"
                }
            }), 400
        
        # 批量匯入
        success_count = 0
        failed_count = 0
        
        for _, row in df.iterrows():
            try:
                # 轉換欄位名稱（相容不同格式）
                data = {
                    "category": row.get("類別") or row.get("category", ""),
                    "question": row.get("問題") or row.get("問題（Q）") or row.get("question", ""),
                    "answer": row.get("回答") or row.get("回答（A）") or row.get("answer", ""),
                    "keywords": row.get("關鍵詞") or row.get("keywords", ""),
                    "notes": row.get("注意事項 / 補充說明") or row.get("notes", "")
                }
                
                # 清理 NaN 值
                for key in data:
                    if pd.isna(data[key]):
                        data[key] = ""
                
                # 跳過沒有問題或答案的項目
                if not data["question"] or not data["answer"]:
                    continue
                
                milvus_service.create(data)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error importing row: {e}")
                failed_count += 1
        
        return jsonify({
            "success": True,
            "imported": success_count,
            "failed": failed_count,
            "total": len(df)
        }), 201
        
    except Exception as e:
        logger.error(f"Error in batch import: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500
