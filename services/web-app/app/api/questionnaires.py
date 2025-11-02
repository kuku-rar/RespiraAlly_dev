# services/web-app/app/api/questionnaires.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from ..core.questionnaire_service import QuestionnaireService
from flasgger import swag_from

questionnaires_bp = Blueprint('questionnaires', __name__, url_prefix='/api/v1/patients')

def authorize_patient_access(fn):
    """Decorator to check if the current user can access the patient's data."""
    @wraps(fn)
    def wrapper(patient_id, *args, **kwargs):
        current_user_id = get_jwt_identity()
        jwt_payload = get_jwt()
        current_user_roles = jwt_payload.get('roles', [])

        # Allow access if the user is accessing their own data, or if they are staff/admin
        if int(current_user_id) == patient_id or 'staff' in current_user_roles or 'admin' in current_user_roles:
            return fn(patient_id, *args, **kwargs)
        else:
            return jsonify({
                "error": {
                    "code": "FORBIDDEN",
                    "message": "You are not authorized to access this resource."
                }
            }), 403
    return wrapper

#<editor-fold desc="CAT Questionnaire Endpoints">
@questionnaires_bp.route('/<int:patient_id>/questionnaires/cat', methods=['GET'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '獲取 CAT 問卷歷史記錄 (Get CAT History)',
    'description': '獲取指定病患的所有歷史 CAT 問卷記錄，用於繪製分數趨勢圖。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '頁碼'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 12, 'description': '每頁數量'}
    ],
    'responses': {
        '200': {'description': '成功獲取 CAT 問卷歷史'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限查看此病患的記錄'},
        '404': {'description': '找不到該病患'}
    },
    'security': [{'bearerAuth': []}]
})
def get_cat_history(patient_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    service = QuestionnaireService()
    paginated_records, error = service.get_cat_history(patient_id, page, per_page)

    if error:
        return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404

    records_list = [
        {
            "record_id": record.id,
            "record_date": record.record_date.isoformat(),
            "total_score": record.total_score,
            "scores": {
                "cough": record.cough_score,
                "phlegm": record.phlegm_score,
                "chest": record.chest_score,
                "breath": record.breath_score,
                "limit": record.limit_score,
                "confidence": record.confidence_score,
                "sleep": record.sleep_score,
                "energy": record.energy_score
            }
        } for record in paginated_records.items
    ]

    return jsonify({
        "data": records_list,
        "pagination": {
            "total_items": paginated_records.total,
            "total_pages": paginated_records.pages,
            "current_page": paginated_records.page,
            "per_page": paginated_records.per_page
        }
    }), 200

@questionnaires_bp.route('/<int:patient_id>/questionnaires/cat', methods=['POST'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '提交 CAT 問卷 (Submit CAT Questionnaire)',
    'description': '提交一份新的 CAT 問卷。如果當月已存在記錄，將回傳 409 Conflict。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'CatInput',
                'required': ['record_date', 'cough_score', 'phlegm_score', 'chest_score', 'breath_score', 'limit_score', 'confidence_score', 'sleep_score', 'energy_score'],
                'properties': {
                    'record_date': {'type': 'string', 'format': 'date', 'description': '記錄日期 (YYYY-MM-DD)'},
                    'cough_score': {'type': 'integer', 'description': '咳嗽程度 (0-5)'},
                    'phlegm_score': {'type': 'integer', 'description': '痰液狀況 (0-5)'},
                    'chest_score': {'type': 'integer', 'description': '胸口緊繃 (0-5)'},
                    'breath_score': {'type': 'integer', 'description': '氣喘程度 (0-5)'},
                    'limit_score': {'type': 'integer', 'description': '日常活動限制 (0-5)'},
                    'confidence_score': {'type': 'integer', 'description': '信心外出 (0-5)'},
                    'sleep_score': {'type': 'integer', 'description': '睡眠品質 (0-5)'},
                    'energy_score': {'type': 'integer', 'description': '精力程度 (0-5)'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': 'CAT questionnaire submitted successfully.'},
        '400': {'description': '請求 Body 的資料格式或分數範圍錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患提交問卷。'},
        '404': {'description': '找不到具有指定 patient_id 的病患。'},
        '409': {'description': '指定月份已存在問卷記錄。'}
    },
    'security': [{'bearerAuth': []}]
})
def submit_cat(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

    service = QuestionnaireService()
    new_record, error = service.submit_cat_questionnaire(patient_id, data)

    if error:
        if "not found" in error.lower():
            return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
        if "already exists" in error.lower():
            return jsonify({"error": {"code": "CONFLICT", "message": error}}), 409
        return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

    return jsonify({
        "data": {
            "record_id": new_record.id,
            "total_score": new_record.total_score,
            "message": "CAT questionnaire submitted successfully."
        }
    }), 201

@questionnaires_bp.route('/<int:patient_id>/questionnaires/cat/<int:year>/<int:month>', methods=['PUT'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '更新指定月份的 CAT 問卷 (Update CAT Questionnaire for a specific month)',
    'description': '更新指定年月份的 CAT 問卷。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {'name': 'year', 'in': 'path', 'required': True, 'description': '要更新的問卷年份 (e.g., 2025)', 'schema': {'type': 'integer'}},
        {'name': 'month', 'in': 'path', 'required': True, 'description': '要更新的問卷月份 (1-12)', 'schema': {'type': 'integer'}},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': { '$ref': '#/definitions/CatInput' }
        }
    ],
    'responses': {
        '200': {'description': 'CAT questionnaire updated successfully.'},
        '400': {'description': '請求 Body 的資料格式或日期格式錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患更新問卷。'},
        '404': {'description': '找不到指定月份的問卷記錄。'}
    },
    'security': [{'bearerAuth': []}]
})
def update_cat(patient_id, year, month):
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

    service = QuestionnaireService()
    updated_record, error = service.update_cat_questionnaire(patient_id, year, month, data)

    if error:
        if "not found" in error.lower():
            return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
        return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

    return jsonify({
        "data": {
            "record_id": updated_record.id,
            "total_score": updated_record.total_score,
            "message": "CAT questionnaire updated successfully."
        }
    }), 200
#</editor-fold>

#<editor-fold desc="MMRC Questionnaire Endpoints">
@questionnaires_bp.route('/<int:patient_id>/questionnaires/mmrc', methods=['GET'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '獲取 MMRC 問卷歷史記錄 (Get MMRC History)',
    'description': '獲取指定病患的所有歷史 MMRC 問卷記錄。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '頁碼'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 12, 'description': '每頁數量'}
    ],
    'responses': {
        '200': {'description': '成功獲取 MMRC 問卷歷史'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限查看此病患的記錄'},
        '404': {'description': '找不到該病患'}
    },
    'security': [{'bearerAuth': []}]
})
def get_mmrc_history(patient_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    service = QuestionnaireService()
    paginated_records, error = service.get_mmrc_history(patient_id, page, per_page)

    if error:
        return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404

    records_list = [
        {
            "record_id": record.id,
            "record_date": record.record_date.isoformat(),
            "score": record.score,
            "answer_text": record.answer_text
        } for record in paginated_records.items
    ]

    return jsonify({
        "data": records_list,
        "pagination": {
            "total_items": paginated_records.total,
            "total_pages": paginated_records.pages,
            "current_page": paginated_records.page,
            "per_page": paginated_records.per_page
        }
    }), 200

@questionnaires_bp.route('/<int:patient_id>/questionnaires/mmrc', methods=['POST'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '提交 MMRC 問卷 (Submit MMRC Questionnaire)',
    'description': '提交一份新的 MMRC 問卷。如果當月已存在記錄，將回傳 409 Conflict。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'MmrcInput',
                'required': ['record_date', 'score', 'answer_text'],
                'properties': {
                    'record_date': {'type': 'string', 'format': 'date', 'description': '記錄日期 (YYYY-MM-DD)'},
                    'score': {'type': 'integer', 'description': 'MMRC 分數 (0-4)'},
                    'answer_text': {'type': 'string', 'description': '使用者選擇的對應文字描述'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': 'MMRC questionnaire submitted successfully.'},
        '400': {'description': '請求 Body 的資料格式錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患提交問卷。'},
        '404': {'description': '找不到具有指定 patient_id 的病患。'},
        '409': {'description': '指定月份已存在問卷記錄。'}
    },
    'security': [{'bearerAuth': []}]
})
def submit_mmrc(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

    service = QuestionnaireService()
    new_record, error = service.submit_mmrc_questionnaire(patient_id, data)

    if error:
        if "not found" in error.lower():
            return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
        if "already exists" in error.lower():
            return jsonify({"error": {"code": "CONFLICT", "message": error}}), 409
        return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

    return jsonify({
        "data": {
            "record_id": new_record.id,
            "message": "MMRC questionnaire submitted successfully."
        }
    }), 201

@questionnaires_bp.route('/<int:patient_id>/questionnaires/mmrc/<int:year>/<int:month>', methods=['PUT'])
@jwt_required()
@authorize_patient_access
@swag_from({
    'summary': '更新指定月份的 MMRC 問卷 (Update MMRC Questionnaire for a specific month)',
    'description': '更新指定年月份的 MMRC 問卷。',
    'tags': ['Health Data & Questionnaires'],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'required': True, 'description': '病患的 user_id', 'schema': {'type': 'integer'}},
        {'name': 'year', 'in': 'path', 'required': True, 'description': '要更新的問卷年份 (e.g., 2025)', 'schema': {'type': 'integer'}},
        {'name': 'month', 'in': 'path', 'required': True, 'description': '要更新的問卷月份 (1-12)', 'schema': {'type': 'integer'}},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': { '$ref': '#/definitions/MmrcInput' }
        }
    ],
    'responses': {
        '200': {'description': 'MMRC questionnaire updated successfully.'},
        '400': {'description': '請求 Body 的資料格式或日期格式錯誤。'},
        '401': {'description': 'Token 無效或未提供。'},
        '403': {'description': '試圖為其他病患更新問卷。'},
        '404': {'description': '找不到指定月份的問卷記錄。'}
    },
    'security': [{'bearerAuth': []}]
})
def update_mmrc(patient_id, year, month):
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body cannot be empty."}}), 400

    service = QuestionnaireService()
    updated_record, error = service.update_mmrc_questionnaire(patient_id, year, month, data)

    if error:
        if "not found" in error.lower():
            return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": error}}), 404
        return jsonify({"error": {"code": "INVALID_INPUT", "message": error}}), 400

    return jsonify({
        "data": {
            "record_id": updated_record.id,
            "message": "MMRC questionnaire updated successfully."
        }
    }), 200
#</editor-fold>
