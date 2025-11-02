# services/web-app/app/utils/response.py
"""
統一的 API 回應格式工具函數
確保所有 API 回應格式一致
"""
from flask import jsonify
from typing import Any, Optional, Dict
from datetime import datetime
import uuid


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    建立成功回應

    Args:
        data: 回應資料
        message: 成功訊息
        meta: 額外的元資料

    Returns:
        Flask jsonify 回應和狀態碼
    """
    response = {
        "success": True,
        "data": data
    }

    if message:
        response["message"] = message

    if meta is None:
        meta = {}

    meta["timestamp"] = datetime.utcnow().isoformat() + "Z"
    meta["version"] = "1.0"
    response["meta"] = meta

    return jsonify(response), 200


def created_response(
    data: Any = None,
    message: Optional[str] = "Resource created successfully",
    meta: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    建立資源建立成功回應 (201)

    Args:
        data: 建立的資源資料
        message: 成功訊息
        meta: 額外的元資料

    Returns:
        Flask jsonify 回應和狀態碼
    """
    response = {
        "success": True,
        "data": data,
        "message": message
    }

    if meta is None:
        meta = {}

    meta["timestamp"] = datetime.utcnow().isoformat() + "Z"
    meta["version"] = "1.0"
    response["meta"] = meta

    return jsonify(response), 201


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
    request_id: Optional[str] = None
) -> tuple:
    """
    建立錯誤回應

    Args:
        code: 錯誤代碼（如 'VALIDATION_ERROR', 'NOT_FOUND'）
        message: 人類可讀的錯誤訊息
        status_code: HTTP 狀態碼
        details: 額外的錯誤詳情
        request_id: 請求 ID（用於追蹤）

    Returns:
        Flask jsonify 回應和狀態碼
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or str(uuid.uuid4())
        }
    }

    if details:
        response["error"]["details"] = details

    return jsonify(response), status_code


def validation_error_response(
    errors: Dict[str, Any],
    message: str = "Validation failed"
) -> tuple:
    """
    建立驗證錯誤回應

    Args:
        errors: 驗證錯誤詳情
        message: 錯誤訊息

    Returns:
        Flask jsonify 回應和狀態碼
    """
    return error_response(
        code="VALIDATION_ERROR",
        message=message,
        status_code=422,
        details=errors
    )


def not_found_response(
    resource: str = "Resource",
    identifier: Optional[Any] = None
) -> tuple:
    """
    建立資源未找到回應

    Args:
        resource: 資源類型名稱
        identifier: 資源識別符

    Returns:
        Flask jsonify 回應和狀態碼
    """
    message = f"{resource} not found"
    if identifier:
        message = f"{resource} with ID '{identifier}' not found"

    return error_response(
        code="NOT_FOUND",
        message=message,
        status_code=404
    )


def unauthorized_response(
    message: str = "Unauthorized access"
) -> tuple:
    """
    建立未授權回應

    Args:
        message: 錯誤訊息

    Returns:
        Flask jsonify 回應和狀態碼
    """
    return error_response(
        code="UNAUTHORIZED",
        message=message,
        status_code=401
    )


def forbidden_response(
    message: str = "Access forbidden"
) -> tuple:
    """
    建立禁止訪問回應

    Args:
        message: 錯誤訊息

    Returns:
        Flask jsonify 回應和狀態碼
    """
    return error_response(
        code="FORBIDDEN",
        message=message,
        status_code=403
    )


def internal_error_response(
    message: str = "An internal server error occurred",
    request_id: Optional[str] = None
) -> tuple:
    """
    建立內部錯誤回應

    Args:
        message: 錯誤訊息
        request_id: 請求 ID

    Returns:
        Flask jsonify 回應和狀態碼
    """
    return error_response(
        code="INTERNAL_ERROR",
        message=message,
        status_code=500,
        request_id=request_id
    )


def paginated_response(
    data: list,
    page: int,
    per_page: int,
    total: int,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    建立分頁回應

    Args:
        data: 當前頁資料
        page: 當前頁碼
        per_page: 每頁數量
        total: 總數量
        message: 成功訊息
        meta: 額外的元資料

    Returns:
        Flask jsonify 回應和狀態碼
    """
    total_pages = (total + per_page - 1) // per_page

    response = {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

    if message:
        response["message"] = message

    if meta is None:
        meta = {}

    meta["timestamp"] = datetime.utcnow().isoformat() + "Z"
    meta["version"] = "1.0"
    response["meta"] = meta

    return jsonify(response), 200


def no_content_response() -> tuple:
    """
    建立無內容回應 (204)

    Returns:
        空回應和狀態碼
    """
    return '', 204


def accepted_response(
    message: str = "Request accepted for processing",
    task_id: Optional[str] = None
) -> tuple:
    """
    建立請求已接受回應 (202)
    用於異步處理

    Args:
        message: 訊息
        task_id: 任務 ID（用於追蹤異步任務）

    Returns:
        Flask jsonify 回應和狀態碼
    """
    response = {
        "success": True,
        "message": message
    }

    if task_id:
        response["task_id"] = task_id

    response["meta"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0"
    }

    return jsonify(response), 202
