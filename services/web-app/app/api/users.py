# services/web-app/app/api/users.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core.user_service import create_user, get_user_by_id
from ..models import User

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

@users_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': '建立新使用者 (管理員專用)',
    'description': '供**管理員**建立新的使用者帳號（例如：呼吸治療師或其他管理員）。',
    'tags': ['Users'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'NewUser',
                'properties': {
                    'account': {'type': 'string', 'example': 'new_therapist_01'},
                    'password': {'type': 'string', 'format': 'password', 'example': 'a_very_strong_password'},
                    'first_name': {'type': 'string', 'example': '思敏'},
                    'last_name': {'type': 'string', 'example': '王'},
                    'email': {'type': 'string', 'example': 'sumin.wang@example.com'},
                    'is_staff': {'type': 'boolean', 'example': True},
                    'is_admin': {'type': 'boolean', 'example': False},
                    'title': {'type': 'string', 'example': '呼吸治療師'}
                },
                'required': ['account', 'password', 'is_staff', 'is_admin']
            }
        }
    ],
    'responses': {
        '201': {'description': '使用者建立成功'},
        '400': {'description': '請求無效或缺少必要欄位'},
        '401': {'description': '未提供 Token 或 Token 無效'},
        '403': {'description': '沒有管理員權限'},
        '409': {'description': '使用者帳號已存在'}
    }
})
def handle_create_user():
    """建立新使用者 (管理員專用)"""
    current_user_id = get_jwt_identity()
    admin_user = get_user_by_id(current_user_id)

    if not admin_user or not admin_user.is_admin:
        return jsonify({"error": {"code": "PERMISSION_DENIED", "message": "Admin access required"}}), 403

    data = request.get_json()
    new_user, error_msg = create_user(data)

    if error_msg:
        status_code = 409 if "exists" in error_msg else 400
        return jsonify({"error": {"code": "INVALID_INPUT", "message": error_msg}}), status_code

    # to_dict() 方法需要添加到 User 模型中
    user_data = {
        "id": new_user.id,
        "account": new_user.account,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "is_staff": new_user.is_staff,
        "is_admin": new_user.is_admin,
        "created_at": new_user.created_at.isoformat()
    }
    return jsonify({"data": user_data}), 201
