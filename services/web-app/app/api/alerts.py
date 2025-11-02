# services/web-app/app/api/alerts.py
"""
🚨 AI 即時通報系統 REST API 模組

功能概述:
- 提供治療師專用的 AI 通報管理介面
- 支援通報列表查詢、分頁、篩選（等級、類別、已讀狀態）
- 實現單一/批量已讀標記功能
- 整合權限控制確保資料安全

資訊流:
Client → JWT驗證 → 權限檢查 → 查詢過濾 → 資料回傳
   ↓         ↓         ↓         ↓         ↓
Request   Token    Staff?   Filters   Response
                              ↓
                    DatabaseQuery
                    (AlertNotification)

依賴關係:
- Flask: 路由與請求處理
- Flask-JWT-Extended: 身份驗證
- SQLAlchemy: ORM 資料操作
- Flasgger: API 文檔生成
- UserRepository: 用戶查詢
- AlertNotification Model: 通報資料模型

設計模式:
- RESTful API Pattern: 標準的 REST 端點設計
- Repository Pattern: 透過 UserRepository 存取用戶資料
- Authorization Pattern: JWT + 角色權限檢查
- Factory Pattern: Blueprint 工廠建立路由

API 端點:
- GET /alerts: 獲取通報列表（支援篩選、分頁）
- PUT /alerts/{id}/read: 標記單一通報為已讀
- PUT /alerts/batch/read: 批量標記通報為已讀

安全機制:
- JWT 必須驗證
- 治療師只能查看自己的通報 (therapist_id == current_user.id)
- 輸入參數驗證
- SQL 注入防護 (ORM)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..core.user_repository import UserRepository
from ..models import AlertNotification
from ..extensions import db
from datetime import datetime, timedelta

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/v1')

@alerts_bp.route('/alerts', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '獲取治療師的 AI 通報列表',
    'description': '獲取當前登入治療師的 AI 即時通報，支援分頁與篩選。',
    'tags': ['AI Alerts'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '頁碼'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20, 'description': '每頁數量'},
        {'name': 'level', 'in': 'query', 'type': 'string', 'description': '通報等級篩選 (info/warning/critical)'},
        {'name': 'category', 'in': 'query', 'type': 'string', 'description': '通報分類篩選 (adherence/health/system)'},
        {'name': 'unread_only', 'in': 'query', 'type': 'boolean', 'default': False, 'description': '只顯示未讀通報'},
        {'name': 'since', 'in': 'query', 'type': 'string', 'description': '獲取指定時間後的通報 (ISO格式)'}
    ],
    'responses': {
        '200': {'description': '成功獲取通報列表'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有治療師權限'}
    }
})
def get_alerts():
    """獲取治療師的 AI 通報列表"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    # 參數解析
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    level = request.args.get('level', type=str)
    category = request.args.get('category', type=str)
    unread_only = request.args.get('unread_only', False, type=bool)
    since = request.args.get('since', type=str)

    # 建立查詢
    query = AlertNotification.query.filter_by(therapist_id=current_user.id)

    # 篩選條件
    if level and level in ['info', 'warning', 'critical']:
        query = query.filter_by(level=level)
    
    if category and category in ['adherence', 'health', 'system']:
        query = query.filter_by(category=category)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    if since:
        try:
            since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
            query = query.filter(AlertNotification.created_at >= since_datetime)
        except ValueError:
            return jsonify({
                "error": {"code": "INVALID_INPUT", "message": "Invalid 'since' datetime format"}
            }), 400

    # 排序：未讀優先，然後按建立時間降序
    query = query.order_by(AlertNotification.is_read.asc(), AlertNotification.created_at.desc())

    # 分頁
    try:
        paginated_alerts = query.paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        return jsonify({
            "error": {"code": "INTERNAL_ERROR", "message": "Failed to retrieve alerts"}
        }), 500

    # 格式化回應
    alerts_list = [alert.to_dict() for alert in paginated_alerts.items]

    return jsonify({
        "data": alerts_list,
        "pagination": {
            "total_items": paginated_alerts.total,
            "total_pages": paginated_alerts.pages,
            "current_page": paginated_alerts.page,
            "per_page": paginated_alerts.per_page,
            "has_next": paginated_alerts.has_next,
            "has_prev": paginated_alerts.has_prev
        },
        "filters": {
            "level": level,
            "category": category,
            "unread_only": unread_only,
            "since": since
        },
        "summary": {
            "unread_count": AlertNotification.query.filter_by(
                therapist_id=current_user.id, is_read=False
            ).count()
        }
    }), 200

@alerts_bp.route('/alerts/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
@swag_from({
    'summary': '標記通報為已讀',
    'description': '將指定的通報標記為已讀狀態。',
    'tags': ['AI Alerts'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {'name': 'alert_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '通報 ID'}
    ],
    'responses': {
        '200': {'description': '成功標記為已讀'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有權限修改此通報'},
        '404': {'description': '找不到該通報'}
    }
})
def mark_alert_read(alert_id):
    """標記通報為已讀"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    # 查找通報
    alert = AlertNotification.query.filter_by(id=alert_id, therapist_id=current_user.id).first()
    
    if not alert:
        return jsonify({
            "error": {"code": "RESOURCE_NOT_FOUND", "message": "Alert not found or access denied"}
        }), 404

    # 更新狀態
    try:
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "data": {
                "alert_id": alert.id,
                "is_read": alert.is_read,
                "read_at": alert.read_at.isoformat() + 'Z',
                "message": "Alert marked as read"
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": {"code": "INTERNAL_ERROR", "message": "Failed to update alert status"}
        }), 500

@alerts_bp.route('/alerts/batch/read', methods=['PUT'])
@jwt_required()
@swag_from({
    'summary': '批量標記通報為已讀',
    'description': '批量將多個通報標記為已讀狀態。',
    'tags': ['AI Alerts'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'BatchReadAlerts',
                'required': ['alert_ids'],
                'properties': {
                    'alert_ids': {'type': 'array', 'items': {'type': 'integer'}, 'description': '通報 ID 陣列'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': '成功批量標記為已讀'},
        '400': {'description': '請求格式錯誤'},
        '401': {'description': 'Token 無效或未提供'},
        '403': {'description': '沒有治療師權限'}
    }
})
def batch_mark_alerts_read():
    """批量標記通報為已讀"""
    current_user_id = get_jwt_identity()
    user_repo = UserRepository()
    current_user = user_repo.find_by_id(current_user_id)

    if not current_user or not current_user.is_staff:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Staff access required"}}), 403

    data = request.get_json()
    if not data or 'alert_ids' not in data:
        return jsonify({
            "error": {"code": "INVALID_INPUT", "message": "alert_ids is required"}
        }), 400

    alert_ids = data['alert_ids']
    if not isinstance(alert_ids, list) or not alert_ids:
        return jsonify({
            "error": {"code": "INVALID_INPUT", "message": "alert_ids must be a non-empty array"}
        }), 400

    try:
        # 批量更新（只更新屬於當前治療師的通報）
        updated_count = AlertNotification.query.filter(
            AlertNotification.id.in_(alert_ids),
            AlertNotification.therapist_id == current_user.id,
            AlertNotification.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        }, synchronize_session=False)

        db.session.commit()

        return jsonify({
            "data": {
                "updated_count": updated_count,
                "requested_count": len(alert_ids),
                "message": f"Successfully marked {updated_count} alerts as read"
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": {"code": "INTERNAL_ERROR", "message": "Failed to batch update alerts"}
        }), 500