# services/web-app/app/api/daily_metrics.py
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from ..core.daily_metric_service import DailyMetricService
from ..core.user_repository import UserRepository
from flasgger import swag_from

daily_metrics_bp = Blueprint('daily_metrics_bp', __name__, url_prefix='/api/v1/patients')

def check_permission(current_user_id, target_patient_id):
    """Checks if the current user has permission to access the target patient's data."""
    if int(current_user_id) == target_patient_id:
        return True  # User can access their own data

    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    # Therapists can access their assigned patients
    if current_user and current_user.is_staff:
        target_patient = user_repo.find_by_id(target_patient_id)
        if target_patient and target_patient.therapist_id == current_user.id:
            return True

    return False

@daily_metrics_bp.route('/<int:patient_id>/daily_metrics', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '獲取每日健康日誌 (Get daily health metrics)',
    'description': '獲取指定病患在特定日期範圍內的每日健康日誌記錄。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'required': True,
            'description': '病患的 user_id',
            'schema': {'type': 'integer'}
        },
        {
            'name': 'start_date',
            'in': 'query',
            'required': False,
            'description': '查詢起始日期，格式 YYYY-MM-DD',
            'schema': {'type': 'string', 'format': 'date'}
        },
        {
            'name': 'end_date',
            'in': 'query',
            'required': False,
            'description': '查詢結束日期，格式 YYYY-MM-DD',
            'schema': {'type': 'string', 'format': 'date'}
        },
        {
            'name': 'page',
            'in': 'query',
            'description': '頁碼',
            'schema': {'type': 'integer', 'default': 1}
        },
        {
            'name': 'per_page',
            'in': 'query',
            'description': '每頁數量',
            'schema': {'type': 'integer', 'default': 30}
        }
    ],
    'responses': {
        '200': {'description': '成功獲取日誌列表'},
        '400': {'description': '日期格式錯誤或 start_date 晚於 end_date'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限查看此病患的日誌'},
        '404': {'description': '找不到該病患'},
        '500': {'description': '伺服器內部錯誤'}
    },
    'security': [{'bearerAuth': []}]
})
def get_daily_metrics(patient_id):
    try:
        current_user_id = get_jwt_identity()
        if not check_permission(current_user_id, patient_id):
            return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "You do not have permission to view these metrics."}}), 403

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)

        service = DailyMetricService()
        paginated_metrics, error = service.get_daily_metrics(patient_id, start_date, end_date, page, per_page)

        if error:
            if "not found" in error.lower():
                return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
            else:
                return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

        metrics_list = [
            {
                "log_id": metric.id,
                "created_at": metric.created_at.isoformat(),
                "water_cc": metric.water_cc,
                "medication": metric.medication,
                "exercise_min": metric.exercise_min,
                "cigarettes": metric.cigarettes
            } for metric in paginated_metrics.items
        ]

        return jsonify({
            "data": metrics_list,
            "pagination": {
                "total_items": paginated_metrics.total,
                "total_pages": paginated_metrics.pages,
                "current_page": paginated_metrics.page,
                "per_page": paginated_metrics.per_page
            }
        }), 200
    except Exception as e:
        logging.error(f"Error getting daily metrics for patient {patient_id}: {e}", exc_info=True)
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500

@daily_metrics_bp.route('/<int:patient_id>/daily_metrics', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': '新增每日健康日誌 (Add a new daily health metric)',
    'description': '供 LIFF 前端為指定病患新增一筆當日的健康日誌。如果當日已存在記錄，將會回傳 409 Conflict 錯誤。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'required': True,
            'description': '病患的 user_id',
            'schema': {'type': 'integer'}
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'DailyMetricInput',
                'properties': {
                    'water_cc': {'type': 'integer', 'description': '當日喝水量 (cc)。'},
                    'medication': {'type': 'boolean', 'description': '是否服藥。'},
                    'exercise_min': {'type': 'integer', 'description': '當日運動分鐘數。'},
                    'cigarettes': {'type': 'integer', 'description': '當日抽菸支數。'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': 'Daily metric created successfully.'},
        '400': {'description': '請求 Body 的資料格式錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患新增日誌。'},
        '404': {'description': '找不到具有指定 patient_id 的病患。'},
        '409': {'description': '當日已經存在一筆日誌記錄。'},
        '500': {'description': '伺服器內部錯誤'}
    },
    'security': [{'bearerAuth': []}]
})
def add_daily_metric(patient_id):
    try:
        current_user_id = get_jwt_identity()
        if int(current_user_id) != patient_id:
            return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "You can only add metrics for yourself."}}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

        service = DailyMetricService()
        new_metric, error = service.create_daily_metric(patient_id, data)

        if error:
            if "not found" in error.lower():
                return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
            if "already exists" in error.lower():
                return jsonify({"error": {"code": "CONFLICT", "message": error}}), 409
            return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

        return jsonify({
            "data": {
                "log_id": new_metric.id,
                "created_at": new_metric.created_at.isoformat(),
                "water_cc": new_metric.water_cc,
                "medication": new_metric.medication,
                "exercise_min": new_metric.exercise_min,
                "cigarettes": new_metric.cigarettes
            }
        }), 201
    except BadRequest:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid JSON format."}}), 400
    except Exception as e:
        logging.error(f"Error adding daily metric for patient {patient_id}: {e}", exc_info=True)
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500

# 開發測試用 API（無需認證）
@daily_metrics_bp.route('/test/daily_metrics', methods=['POST'])
@swag_from({
    'summary': '測試用每日健康日誌 API (Development Test Only)',
    'description': '僅供開發測試使用，無需認證。實際生產環境請使用有認證的 API。',
    'tags': ['Development'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'TestDailyMetricInput',
                'properties': {
                    'patient_id': {'type': 'integer', 'description': '病患 ID (測試用)'},
                    'water_cc': {'type': 'integer', 'description': '當日喝水量 (cc)'},
                    'medication': {'type': 'boolean', 'description': '是否服藥'},
                    'exercise_min': {'type': 'integer', 'description': '當日運動分鐘數'},
                    'cigarettes': {'type': 'integer', 'description': '當日抽菸支數'}
                },
                'required': ['patient_id', 'water_cc', 'medication', 'exercise_min', 'cigarettes']
            }
        }
    ],
    'responses': {
        '201': {'description': '測試記錄創建成功'},
        '400': {'description': '請求格式錯誤'},
        '500': {'description': '伺服器錯誤'}
    }
})
def test_add_daily_metric():
    """測試用 API - 開發環境使用"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "patient_id is required."}}), 400

        # 移除 patient_id 從 data 中，因為 service 不需要它
        metric_data = {k: v for k, v in data.items() if k != 'patient_id'}

        service = DailyMetricService()
        new_metric, error = service.create_daily_metric(patient_id, metric_data)

        if error:
            if "not found" in error.lower():
                return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
            if "already exists" in error.lower():
                return jsonify({"error": {"code": "CONFLICT", "message": error}}), 409
            return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

        return jsonify({
            "success": True,
            "message": "測試記錄已成功建立",
            "data": {
                "log_id": new_metric.id,
                "created_at": new_metric.created_at.isoformat(),
                "water_cc": new_metric.water_cc,
                "medication": new_metric.medication,
                "exercise_min": new_metric.exercise_min,
                "cigarettes": new_metric.cigarettes
            }
        }), 201
    except BadRequest:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid JSON format."}}), 400
    except Exception as e:
        logging.error(f"Error in test API for patient {data.get('patient_id', 'unknown')}: {e}", exc_info=True)
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500

@daily_metrics_bp.route('/<int:patient_id>/daily_metrics/<string:log_date>', methods=['PUT'])
@jwt_required()
@swag_from({
    'summary': '更新指定日期的健康日誌 (Update a daily health metric)',
    'description': '供 LIFF 前端更新指定日期的健康日誌。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'required': True,
            'description': '病患的 user_id',
            'schema': {'type': 'integer'}
        },
        {
            'name': 'log_date',
            'in': 'path',
            'required': True,
            'description': '要更新的日誌日期，格式 YYYY-MM-DD',
            'schema': {'type': 'string', 'format': 'date'}
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'DailyMetricUpdate',
                'properties': {
                    'water_cc': {'type': 'integer', 'description': '更新後的喝水量 (cc)。'},
                    'medication': {'type': 'boolean', 'description': '更新後的服藥狀況。'},
                    'exercise_min': {'type': 'integer', 'description': '更新後的運動分鐘數。'},
                    'cigarettes': {'type': 'integer', 'description': '更新後的抽菸支數。'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': 'Daily metric updated successfully.'},
        '400': {'description': '請求 Body 的資料格式或日期格式錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患更新日誌。'},
        '404': {'description': '找不到指定日期的日誌記錄。'},
        '500': {'description': '伺服器內部錯誤'}
    },
    'security': [{'bearerAuth': []}]
})
def update_daily_metric(patient_id, log_date):
    try:
        current_user_id = get_jwt_identity()
        if int(current_user_id) != patient_id:
            return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "You can only update metrics for yourself."}}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

        service = DailyMetricService()

        updated_metric, error = service.update_daily_metric(patient_id, log_date, data)

        if error:
            if "metric not found" in error.lower():
                return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
            return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

        return jsonify({
            "data": {
                "log_id": updated_metric.id,
                "created_at": updated_metric.created_at.isoformat(),
                "water_cc": updated_metric.water_cc,
                "medication": updated_metric.medication,
                "exercise_min": updated_metric.exercise_min,
                "cigarettes": updated_metric.cigarettes
            }
        }), 200
    except BadRequest:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid JSON format."}}), 400
    except Exception as e:
        logging.error(f"Error updating daily metric for patient {patient_id} on {log_date}: {e}", exc_info=True)
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500
