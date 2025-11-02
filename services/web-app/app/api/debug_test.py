# services/web-app/app/api/debug_test.py
"""
簡化的測試端點，用於診斷 500 錯誤問題
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, HealthProfile
import logging

logger = logging.getLogger(__name__)

debug_bp = Blueprint('debug', __name__, url_prefix='/api/v1/debug')

@debug_bp.route('/health', methods=['GET'])
def health_check():
    """基本健康檢查 - 不需要認證"""
    return jsonify({"status": "OK", "message": "API is working"})

@debug_bp.route('/db-test', methods=['GET'])
def db_test():
    """測試資料庫連接 - 不需要認證"""
    try:
        # 簡單的資料庫查詢
        user_count = db.session.query(User).count()
        return jsonify({
            "status": "OK", 
            "message": "Database connection working",
            "user_count": user_count
        })
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@debug_bp.route('/auth-test', methods=['GET'])
@jwt_required()
def auth_test():
    """測試 JWT 認證"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return jsonify({
            "status": "OK",
            "message": "JWT auth working",
            "user_id": current_user_id,
            "user_exists": user is not None,
            "user_account": user.account if user else None
        })
    except Exception as e:
        logger.error(f"Auth test failed: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@debug_bp.route('/overview-simple', methods=['GET'])
@jwt_required()
def overview_simple():
    """簡化版的總覽查詢"""
    try:
        current_user_id = get_jwt_identity()
        
        # 最基本的查詢
        total_patients = db.session.query(HealthProfile).filter(
            HealthProfile.staff_id == current_user_id
        ).count()
        
        return jsonify({
            "status": "OK",
            "message": "Simple overview working",
            "therapist_id": current_user_id,
            "total_patients": total_patients
        })
    except Exception as e:
        logger.error(f"Simple overview test failed: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500