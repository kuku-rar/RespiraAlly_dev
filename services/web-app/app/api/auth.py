# services/web-app/app/api/auth.py
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flasgger import swag_from
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest
from ..core.auth_service import login_user, login_line_user, register_line_user
from datetime import timedelta
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'summary': '呼吸治療師登入',
    'description': '供呼吸治療師使用帳號密碼進行登入。',
    'tags': ['Authentication'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'Login',
                'required': ['account', 'password'],
                'properties': {
                    'account': {'type': 'string', 'example': 'admin'},
                    'password': {'type': 'string', 'format': 'password', 'example': 'admin'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': '登入成功'},
        '400': {'description': '請求格式錯誤'},
        '401': {'description': '帳號或密碼錯誤'},
        '500': {'description': '伺服器內部錯誤'}
    }
})
def handle_login():
    """處理使用者登入"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "Request body must be JSON."}}), 400

        account = data.get('account')
        password = data.get('password')

        if not account or not password:
            return jsonify({"error": {"code": "INVALID_INPUT", "message": "Account and password are required."}}), 400

        user = login_user(account, password)

        if not user:
            return jsonify({"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid account or password."}}), 401

        identity = str(user.id)
        expires = timedelta(hours=1)
        
        # 添加 roles 到 JWT payload
        additional_claims = {
            'roles': ['staff'] if user.is_staff else ['patient']
        }
        if user.is_admin:
            additional_claims['roles'].append('admin')
            
        access_token = create_access_token(
            identity=identity,
            expires_delta=expires,
            additional_claims=additional_claims
        )

        user_info = {
            "id": user.id,
            "account": user.account,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_admin": getattr(user, 'is_admin', False),
        }
        if user.is_staff and hasattr(user, 'staff_details') and user.staff_details:
            user_info['title'] = user.staff_details.title

        return jsonify({
            "data": {
                "token": access_token,
                "expires_in": expires.total_seconds(),
                "user": user_info
            }
        }), 200
    except BadRequest:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid JSON format."}}), 400
    except Exception as e:
        logging.error(f"An unexpected error occurred during login: {e}", exc_info=True)
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500

@auth_bp.route('/line/login', methods=['POST'])
@swag_from({
    'summary': '患者 LIFF 登入',
    'description': '供**已註冊**的患者在 LIFF 環境中，使用 `lineUserId` 進行登入。',
    'tags': ['Authentication'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'LineLogin',
                'required': ['lineUserId'],
                'properties': {
                    'lineUserId': {'type': 'string', 'example': 'U123456789abcdef123456789abcdef'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': '登入成功'},
        '400': {'description': 'lineUserId 缺失'},
        '404': {'description': '使用者未註冊'}
    }
})
def handle_line_login():
    """處理 LINE 使用者登入"""
    data = request.get_json()
    line_user_id = data.get('lineUserId')

    if not line_user_id:
        return jsonify({"error": {"code": "INVALID_INPUT", "message": "lineUserId is required."}}), 400

    user = login_line_user(line_user_id)

    if not user:
        return jsonify({"error": {"code": "USER_NOT_FOUND", "message": "This LINE account is not registered."}}), 404

    identity = str(user.id)
    expires = timedelta(days=7)
    
    # 添加 roles 到 JWT payload
    additional_claims = {
        'roles': ['staff'] if user.is_staff else ['patient']
    }
    if user.is_admin:
        additional_claims['roles'].append('admin')
        
    access_token = create_access_token(
        identity=identity,
        expires_delta=expires,
        additional_claims=additional_claims
    )

    user_info = {
        "id": user.id,
        "line_user_id": user.line_user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "health_profile": {
            "height_cm": user.health_profile.height_cm if user.health_profile else None,
            "weight_kg": user.health_profile.weight_kg if user.health_profile else None,
            "smoke_status": user.health_profile.smoke_status if user.health_profile else None,
        }
    }

    return jsonify({
        "data": {
            "token": access_token,
            "expires_in": expires.total_seconds(),
            "user": user_info
        }
    }), 200

@auth_bp.route('/line/register', methods=['POST'])
@swag_from({
    'summary': '患者 LIFF 註冊',
    'description': '供新患者在 LIFF 環境中，使用 `lineUserId` 並填寫基本資料以完成註冊。',
    'tags': ['Authentication'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'LineRegister',
                'required': ['lineUserId', 'first_name', 'last_name'],
                'properties': {
                    'lineUserId': {'type': 'string', 'example': 'U_new_user_abcdef123456'},
                    'first_name': {'type': 'string', 'example': '美麗'},
                    'last_name': {'type': 'string', 'example': '陳'},
                    'gender': {'type': 'string', 'example': 'female'},
                    'phone': {'type': 'string', 'example': '0987654321'},
                    'height_cm': {'type': 'integer', 'example': 160},
                    'weight_kg': {'type': 'integer', 'example': 55},
                    'smoke_status': {'type': 'string', 'example': 'never'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': '註冊成功並自動登入'},
        '400': {'description': '缺少必要欄位'},
        '409': {'description': '使用者已存在'}
    }
})
def handle_line_register():
    """處理 LINE 使用者註冊"""
    data = request.get_json()

    new_user, error_msg = register_line_user(data)

    if error_msg:
        status_code = 409 if "already registered" in error_msg else 400
        error_code = "USER_ALREADY_EXISTS" if status_code == 409 else "INVALID_INPUT"
        return jsonify({"error": {"code": error_code, "message": error_msg}}), status_code

    # Link member rich menu upon successful registration
    try:
        from ..core.line_service import get_line_service
        from flask import current_app

        line_service = get_line_service()
        member_menu_id = current_app.config.get('LINE_RICH_MENU_ID_MEMBER')
        if member_menu_id:
            line_service.link_rich_menu_to_user(new_user.line_user_id, member_menu_id)
            logging.info(f"Successfully linked member rich menu to new user {new_user.id}")
    except Exception as e:
        logging.error(f"Failed to link rich menu for new user {new_user.id}: {e}", exc_info=True)
        # We don't fail the request for this, just log it.

    identity = str(new_user.id)
    expires = timedelta(days=7)
    access_token = create_access_token(identity=identity, expires_delta=expires)

    user_info = {
        "id": new_user.id,
        "line_user_id": new_user.line_user_id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name
    }

    return jsonify({
        "data": {
            "token": access_token,
            "expires_in": expires.total_seconds(),
            "user": user_info
        }
    }), 201

@auth_bp.route('/liff', methods=['GET'])
@swag_from({
    'summary': '提供 LIFF 頁面',
    'description': '提供 LINE Front-end Framework (LIFF) 的主要 HTML 頁面。',
    'tags': ['LIFF'],
    'responses': {
        '200': {
            'description': '成功回傳 LIFF HTML 頁面',
            'content': {
                'text/html': {}
            }
        }
    }
})
def serve_liff_page():
    """提供 LIFF 靜態頁面"""
    return send_from_directory(current_app.static_folder, 'liff.html')
