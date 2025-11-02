# services/web-app/app/api/overview.py
"""
總覽 API 端點
提供 Dashboard 的 KPI、趨勢、依從性分析等數據
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..core.overview_service import get_overview_service
from ..utils.response import (
    success_response,
    error_response,
    internal_error_response
)
import logging

logger = logging.getLogger(__name__)

overview_bp = Blueprint('overview', __name__, url_prefix='/api/v1/overview')
overview_service = get_overview_service()


@overview_bp.route('/kpis', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得關鍵績效指標',
    'description': '取得治療師管理的病患相關 KPI 數據',
    'tags': ['Overview'],
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '成功取得 KPI 數據',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'total_patients': {'type': 'integer', 'description': '總病患數'},
                                    'high_risk_patients': {'type': 'integer', 'description': '高風險病患數'},
                                    'average_adherence': {'type': 'number', 'description': '平均依從率'},
                                    'active_today': {'type': 'integer', 'description': '今日活躍用戶數'},
                                    'low_adherence_patients': {'type': 'integer', 'description': '低依從性病患數'},
                                    'improvement_rate': {'type': 'number', 'description': '改善率'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_overview_kpis():
    """取得關鍵績效指標"""
    try:
        current_user_id = get_jwt_identity()
        kpis = overview_service.get_kpis(current_user_id)
        return success_response(data=kpis)
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        return internal_error_response("Failed to retrieve KPIs")


@overview_bp.route('/trends', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得趨勢數據',
    'description': '取得 CAT、mMRC 和每日健康指標的趨勢數據',
    'tags': ['Overview'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'days',
            'in': 'query',
            'type': 'integer',
            'default': 30,
            'description': '天數範圍（預設 30 天）'
        }
    ],
    'responses': {
        '200': {
            'description': '成功取得趨勢數據',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'cat_trends': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'date': {'type': 'string'},
                                                'avg_score': {'type': 'number'},
                                                'count': {'type': 'integer'}
                                            }
                                        }
                                    },
                                    'mmrc_trends': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'date': {'type': 'string'},
                                                'avg_score': {'type': 'number'},
                                                'count': {'type': 'integer'}
                                            }
                                        }
                                    },
                                    'daily_trends': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'date': {'type': 'string'},
                                                'avg_water': {'type': 'number'},
                                                'avg_exercise': {'type': 'number'},
                                                'avg_medication': {'type': 'number'},
                                                'active_users': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_overview_trends():
    """取得趨勢數據"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # 限制最大天數
        if days > 365:
            days = 365
        elif days < 1:
            days = 30
        
        trends = overview_service.get_trends(current_user_id, days)
        return success_response(data=trends)
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return internal_error_response("Failed to retrieve trends")


@overview_bp.route('/adherence', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得依從性分析',
    'description': '取得病患藥物依從性的分析數據',
    'tags': ['Overview'],
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '成功取得依從性分析',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'distribution': {
                                        'type': 'object',
                                        'properties': {
                                            'excellent': {'type': 'integer', 'description': '優秀 (≥90%)'},
                                            'good': {'type': 'integer', 'description': '良好 (70-89%)'},
                                            'fair': {'type': 'integer', 'description': '尚可 (50-69%)'},
                                            'poor': {'type': 'integer', 'description': '不佳 (<50%)'}
                                        }
                                    },
                                    'low_adherence_patients': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'patient_id': {'type': 'integer'},
                                                'patient_name': {'type': 'string'},
                                                'adherence_rate': {'type': 'number'}
                                            }
                                        }
                                    },
                                    'total_patients': {'type': 'integer'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_overview_adherence():
    """取得依從性分析"""
    try:
        current_user_id = get_jwt_identity()
        adherence = overview_service.get_adherence_analysis(current_user_id)
        return success_response(data=adherence)
    except Exception as e:
        logger.error(f"Error getting adherence analysis: {e}")
        return internal_error_response("Failed to retrieve adherence analysis")


@overview_bp.route('/usage', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得使用統計',
    'description': '取得應用程式各功能的使用統計數據',
    'tags': ['Overview'],
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '成功取得使用統計',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'feature_usage': {
                                        'type': 'object',
                                        'properties': {
                                            'cat_questionnaire': {'type': 'integer'},
                                            'mmrc_questionnaire': {'type': 'integer'},
                                            'daily_metrics': {'type': 'integer'}
                                        }
                                    },
                                    'completion_rates': {
                                        'type': 'object',
                                        'properties': {
                                            'cat': {'type': 'number'},
                                            'mmrc': {'type': 'number'},
                                            'daily': {'type': 'number'}
                                        }
                                    },
                                    'daily_active_users': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'date': {'type': 'string'},
                                                'active_users': {'type': 'integer'}
                                            }
                                        }
                                    },
                                    'total_patients': {'type': 'integer'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_overview_usage():
    """取得使用統計"""
    try:
        current_user_id = get_jwt_identity()
        usage = overview_service.get_usage_statistics(current_user_id)
        return success_response(data=usage)
    except Exception as e:
        logger.error(f"Error getting usage statistics: {e}")
        return internal_error_response("Failed to retrieve usage statistics")


@overview_bp.route('/summary', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得總覽摘要',
    'description': '取得所有總覽數據的摘要（KPI、趨勢、依從性、使用統計）',
    'tags': ['Overview'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'trend_days',
            'in': 'query',
            'type': 'integer',
            'default': 30,
            'description': '趨勢天數範圍'
        }
    ],
    'responses': {
        '200': {
            'description': '成功取得總覽摘要',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'kpis': {'type': 'object'},
                                    'trends': {'type': 'object'},
                                    'adherence': {'type': 'object'},
                                    'usage': {'type': 'object'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_overview_summary():
    """取得總覽摘要 - 一次取得所有數據"""
    try:
        current_user_id = get_jwt_identity()
        trend_days = request.args.get('trend_days', 30, type=int)
        
        # 限制最大天數
        if trend_days > 365:
            trend_days = 365
        elif trend_days < 1:
            trend_days = 30
        
        # 平行取得所有數據
        summary = {
            'kpis': overview_service.get_kpis(current_user_id),
            'trends': overview_service.get_trends(current_user_id, trend_days),
            'adherence': overview_service.get_adherence_analysis(current_user_id),
            'usage': overview_service.get_usage_statistics(current_user_id)
        }
        
        return success_response(data=summary)
    except Exception as e:
        logger.error(f"Error getting overview summary: {e}")
        return internal_error_response("Failed to retrieve overview summary")
