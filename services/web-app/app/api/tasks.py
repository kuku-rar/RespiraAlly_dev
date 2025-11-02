# services/web-app/app/api/tasks.py
"""
任務管理 API 端點
提供 CRUD 操作和任務排程功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from datetime import datetime
from ..models.models import Task, User
from ..extensions import db
from ..utils.response import (
    success_response,
    error_response,
    internal_error_response,
    paginated_response
)
import logging

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/v1/tasks')


# 修復 Flask 尾部斜杠重定向導致的 CORS 問題
@tasks_bp.route('', methods=['GET'])
@tasks_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得任務列表',
    'description': '取得當前用戶的任務列表，支援篩選和分頁',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': '頁碼'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 20,
            'description': '每頁數量'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'description': '任務狀態篩選 (pending/in_progress/completed)'
        },
        {
            'name': 'type',
            'in': 'query',
            'type': 'string',
            'description': '任務類型篩選 (education/tracking/assessment/appointment)'
        },
        {
            'name': 'patient_id',
            'in': 'query',
            'type': 'integer',
            'description': '病患 ID 篩選'
        }
    ],
    'responses': {
        '200': {
            'description': '成功取得任務列表',
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
                                        'id': {'type': 'integer'},
                                        'title': {'type': 'string'},
                                        'description': {'type': 'string'},
                                        'type': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'priority': {'type': 'integer'},
                                        'due_date': {'type': 'string'},
                                        'patient_name': {'type': 'string'}
                                    }
                                }
                            },
                            'pagination': {'type': 'object'}
                        }
                    }
                }
            }
        },
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_tasks():
    """取得任務列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 分頁參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 篩選參數
        status = request.args.get('status')
        task_type = request.args.get('type')
        patient_id = request.args.get('patient_id', type=int)
        
        # 建立查詢
        query = Task.query.filter(Task.assignee_id == current_user_id)
        
        # 應用篩選
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.type == task_type)
        if patient_id:
            query = query.filter(Task.patient_id == patient_id)
        
        # 排序
        query = query.order_by(Task.due_date.asc(), Task.priority.desc())
        
        # 分頁
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 格式化回應
        tasks_data = []
        for task in paginated.items:
            task_dict = task.to_dict()
            # 加入病患名稱
            if task.patient:
                task_dict['patient_name'] = task.patient.display_name
            else:
                task_dict['patient_name'] = None
            tasks_data.append(task_dict)
        
        return paginated_response(
            data=tasks_data,
            page=page,
            per_page=per_page,
            total=paginated.total
        )
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return internal_error_response("Failed to retrieve tasks")


@tasks_bp.route('', methods=['POST'])
@tasks_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'summary': '建立新任務',
    'description': '建立新的任務',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['title', 'type'],
                    'properties': {
                        'title': {'type': 'string', 'description': '任務標題'},
                        'description': {'type': 'string', 'description': '任務描述'},
                        'type': {'type': 'string', 'enum': ['education', 'tracking', 'assessment', 'appointment']},
                        'priority': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                        'patient_id': {'type': 'integer', 'description': '關聯病患 ID'},
                        'due_date': {'type': 'string', 'format': 'date-time', 'description': '截止日期'},
                        'start_date': {'type': 'string', 'format': 'date-time', 'description': '開始日期'}
                    }
                }
            }
        }
    },
    'responses': {
        '201': {
            'description': '任務建立成功',
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
                                    'title': {'type': 'string'},
                                    'status': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': '輸入資料錯誤'},
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def create_task():
    """建立新任務"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 驗證必要欄位
        if not data or not data.get('title') or not data.get('type'):
            return error_response("MISSING_FIELDS", "Title and type are required", 400)
        
        # 驗證任務類型
        valid_types = ['education', 'tracking', 'assessment', 'appointment']
        if data.get('type') not in valid_types:
            return error_response("INVALID_TYPE", f"Type must be one of: {', '.join(valid_types)}", 400)
        
        # 建立任務
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            type=data['type'],
            priority=data.get('priority', 3),
            assignee_id=current_user_id,
            patient_id=data.get('patient_id'),
            created_by=current_user_id
        )
        
        # 處理日期
        if data.get('due_date'):
            try:
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return error_response("INVALID_DATE", "Invalid due_date format", 400)
        
        if data.get('start_date'):
            try:
                task.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return error_response("INVALID_DATE", "Invalid start_date format", 400)
        
        db.session.add(task)
        db.session.commit()
        
        return success_response(data=task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating task: {e}")
        return internal_error_response("Failed to create task")


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得任務詳情',
    'description': '取得指定任務的詳細資訊',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '任務 ID'
        }
    ],
    'responses': {
        '200': {'description': '成功取得任務詳情'},
        '404': {'description': '任務不存在'},
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def get_task(task_id):
    """取得任務詳情"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter(
            Task.id == task_id,
            Task.assignee_id == current_user_id
        ).first()
        
        if not task:
            return error_response("TASK_NOT_FOUND", "Task not found", 404)
        
        task_dict = task.to_dict()
        # 加入病患資訊
        if task.patient:
            task_dict['patient_name'] = task.patient.display_name
            
        return success_response(data=task_dict)
        
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return internal_error_response("Failed to retrieve task")


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'summary': '更新任務',
    'description': '更新指定任務的資訊',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '任務 ID'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'type': {'type': 'string'},
                        'status': {'type': 'string'},
                        'priority': {'type': 'integer'},
                        'due_date': {'type': 'string', 'format': 'date-time'},
                        'start_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    },
    'responses': {
        '200': {'description': '任務更新成功'},
        '404': {'description': '任務不存在'},
        '400': {'description': '輸入資料錯誤'},
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def update_task(task_id):
    """更新任務"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response("NO_DATA", "No data provided", 400)
        
        task = Task.query.filter(
            Task.id == task_id,
            Task.assignee_id == current_user_id
        ).first()
        
        if not task:
            return error_response("TASK_NOT_FOUND", "Task not found", 404)
        
        # 更新欄位
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'type' in data:
            valid_types = ['education', 'tracking', 'assessment', 'appointment']
            if data['type'] not in valid_types:
                return error_response("INVALID_TYPE", f"Type must be one of: {', '.join(valid_types)}", 400)
            task.type = data['type']
        if 'status' in data:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if data['status'] not in valid_statuses:
                return error_response("INVALID_STATUS", f"Status must be one of: {', '.join(valid_statuses)}", 400)
            task.status = data['status']
            # 如果標記為完成，設定完成時間
            if data['status'] == 'completed' and not task.completed_at:
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = max(1, min(5, data['priority']))
        
        # 處理日期
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return error_response("INVALID_DATE", "Invalid due_date format", 400)
            else:
                task.due_date = None
        
        if 'start_date' in data:
            if data['start_date']:
                try:
                    task.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
                except ValueError:
                    return error_response("INVALID_DATE", "Invalid start_date format", 400)
            else:
                task.start_date = None
        
        db.session.commit()
        
        return success_response(data=task.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating task {task_id}: {e}")
        return internal_error_response("Failed to update task")


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'summary': '刪除任務',
    'description': '刪除指定任務',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '任務 ID'
        }
    ],
    'responses': {
        '200': {'description': '任務刪除成功'},
        '404': {'description': '任務不存在'},
        '401': {'description': '未授權'},
        '500': {'description': '伺服器錯誤'}
    }
})
def delete_task(task_id):
    """刪除任務"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter(
            Task.id == task_id,
            Task.assignee_id == current_user_id
        ).first()
        
        if not task:
            return error_response("TASK_NOT_FOUND", "Task not found", 404)
        
        db.session.delete(task)
        db.session.commit()
        
        return success_response(data={"message": "Task deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting task {task_id}: {e}")
        return internal_error_response("Failed to delete task")


@tasks_bp.route('/summary', methods=['GET'])
@jwt_required()
@swag_from({
    'summary': '取得任務摘要',
    'description': '取得當前用戶的任務統計摘要',
    'tags': ['Tasks'],
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '成功取得任務摘要',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'total_tasks': {'type': 'integer'},
                                    'pending_tasks': {'type': 'integer'},
                                    'in_progress_tasks': {'type': 'integer'},
                                    'completed_tasks': {'type': 'integer'},
                                    'overdue_tasks': {'type': 'integer'},
                                    'tasks_by_type': {'type': 'object'}
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
def get_tasks_summary():
    """取得任務摘要"""
    try:
        current_user_id = get_jwt_identity()
        
        # 基本統計
        total_tasks = Task.query.filter(Task.assignee_id == current_user_id).count()
        pending_tasks = Task.query.filter(
            Task.assignee_id == current_user_id,
            Task.status == 'pending'
        ).count()
        in_progress_tasks = Task.query.filter(
            Task.assignee_id == current_user_id,
            Task.status == 'in_progress'
        ).count()
        completed_tasks = Task.query.filter(
            Task.assignee_id == current_user_id,
            Task.status == 'completed'
        ).count()
        
        # 逾期任務
        now = datetime.utcnow()
        overdue_tasks = Task.query.filter(
            Task.assignee_id == current_user_id,
            Task.status.in_(['pending', 'in_progress']),
            Task.due_date < now
        ).count()
        
        # 按類型統計
        from sqlalchemy import func
        tasks_by_type = dict(
            db.session.query(Task.type, func.count(Task.id))
            .filter(Task.assignee_id == current_user_id)
            .group_by(Task.type)
            .all()
        )
        
        summary = {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'tasks_by_type': tasks_by_type
        }
        
        return success_response(data=summary)
        
    except Exception as e:
        logger.error(f"Error getting tasks summary: {e}")
        return internal_error_response("Failed to retrieve tasks summary")
