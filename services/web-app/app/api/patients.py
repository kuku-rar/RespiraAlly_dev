# services/web-app/app/api/patients.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core.patient_service import PatientService
from ..core.user_repository import UserRepository

patients_bp = Blueprint('patients', __name__, url_prefix='/api/v1')
patient_service = PatientService()

@patients_bp.route('/therapist/patients', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '獲取管理的病患列表',
    'description': '獲取當前登入的呼吸治療師所管理的所有病患的簡要列表，支援風險篩選和分頁。',
    'tags': ['Patients'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '頁碼'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20, 'description': '每頁數量'},
        {'name': 'risk', 'in': 'query', 'type': 'string', 'description': '風險等級篩選 (high, medium, low)', 'required': False},
        {'name': 'limit', 'in': 'query', 'type': 'integer', 'description': '限制返回數量（覆蓋per_page）'},
        {'name': 'sort_by', 'in': 'query', 'type': 'string', 'default': 'last_login', 'description': '排序欄位'},
        {'name': 'order', 'in': 'query', 'type': 'string', 'default': 'desc', 'enum': ['asc', 'desc'], 'description': '排序順序'}
    ],
    'responses': {
        '200': {'description': '成功獲取病患列表'},
        '400': {'description': '參數驗證失敗'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有治療師權限'}
    }
})
def get_therapist_patients():
    """獲取治療師的病患列表，支援風險篩選和分頁"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    # 從請求中獲取所有查詢參數
    query_params = request.args.to_dict()

    # 調用服務層
    response_data, status_code = patient_service.get_patients_by_therapist(
        therapist_id=current_user.id,
        **query_params
    )

    return jsonify(response_data), status_code

@patients_bp.route('/patients/<int:patient_id>/profile', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '獲取病患詳細健康檔案',
    'description': '獲取指定病患的詳細健康檔案資訊。',
    'tags': ['Patients'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '病患的 user_id'}
    ],
    'responses': {
        '200': {'description': '成功獲取病患檔案'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限查看此病患'},
        '404': {'description': '找不到該病患'}
    }
})
def get_patient_profile(patient_id):
    """獲取病患詳細健康檔案"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    profile_data = patient_service.get_patient_profile(patient_id)

    if not profile_data:
        return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": "Patient not found"}}), 404

    user, health_profile = profile_data

    # 權限校驗：確保當前治療師是該病患的個管師
    if health_profile.staff_id != current_user.id:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "You are not authorized to view this patient's profile"}}), 403

    # 格式化回傳資料
    response_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "gender": user.gender,
        "email": user.email,
        "phone": user.phone,
        "health_profile": {
            "height_cm": health_profile.height_cm,
            "weight_kg": health_profile.weight_kg,
            "smoke_status": health_profile.smoke_status,
            "updated_at": health_profile.updated_at.isoformat() if health_profile.updated_at else None
        }
    }

    return jsonify({"data": response_data}), 200

@patients_bp.route('/patients/<int:patient_id>/kpis', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '獲取個別病患 KPI 指標',
    'description': '獲取指定病患的關鍵績效指標，包括最新問卷分數、依從性統計等。',
    'tags': ['Patients'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {'name': 'patient_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '病患的 user_id'},
        {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 7, 'description': '計算天數範圍（默認7天）'}
    ],
    'responses': {
        '200': {'description': '成功獲取病患 KPI'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限查看此病患'},
        '404': {'description': '找不到該病患'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def get_patient_kpis(patient_id):
    """獲取個別病患的 KPI 指標"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    # 權限檢查：確保治療師只能查看自己管理的病患
    patient_profile = patient_service.get_patient_profile(patient_id)
    if not patient_profile:
        return jsonify({"error": {"code": "RESOURCE_NOT_FOUND", "message": "Patient not found"}}), 404
    
    user, health_profile = patient_profile
    if health_profile.staff_id != current_user.id:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "You are not authorized to view this patient's KPIs"}}), 403

    # 獲取參數
    days = request.args.get('days', 7, type=int)
    
    try:
        # 計算 KPI
        kpi_data = patient_service.calculate_patient_kpis(patient_id, days)
        
        return jsonify({
            "data": kpi_data,
            "meta": {
                "patient_id": patient_id,
                "calculation_days": days,
                "calculated_at": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
            }
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error calculating patient KPIs for patient {patient_id}: {e}", exc_info=True)
        return jsonify({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Failed to calculate patient KPIs"
            }
        }), 500

@patients_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients_generic():
    """
    統一的病患查詢端點，用於捕獲錯誤調用並重定向到正確的端點
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 記錄調用信息
    logger.warning(f"錯誤的API調用: /api/v1/patients 被調用，參數: {dict(request.args)}")
    logger.warning(f"請求來源: {request.headers.get('Referer', 'Unknown')}")
    logger.warning(f"用戶代理: {request.headers.get('User-Agent', 'Unknown')}")
    
    # 獲取當前用戶
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)
    
    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403
    
    # 重定向到正確的端點
    return jsonify({
        "error": {
            "code": "ENDPOINT_DEPRECATED",
            "message": "This endpoint is deprecated. Please use /api/v1/therapist/patients instead.",
            "redirect_to": "/api/v1/therapist/patients",
            "current_params": dict(request.args)
        }
    }), 308  # 308 Permanent Redirect
