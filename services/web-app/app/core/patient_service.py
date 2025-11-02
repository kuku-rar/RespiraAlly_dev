# services/web-app/app/core/patient_service.py
from .patient_repository import PatientRepository
from sqlalchemy import text
from ..extensions import db

class PatientService:
    def __init__(self):
        self.patient_repository = PatientRepository()

    def get_patients_by_therapist(self, therapist_id, page=1, per_page=None, limit=None, risk=None, sort_by='last_login', order='desc'):
        """
        獲取並格式化治療師管理的病患列表，包含參數驗證、篩選和分頁。
        - 新增參數驗證
        - 新增風險等級篩選
        - 新增最終資料格式化
        """
        # 1. 參數驗證與處理
        error_response = self._validate_and_prepare_params(page, per_page, limit, risk, sort_by, order)
        if error_response:
            return error_response

        page, per_page, limit, risk, sort_by, order = self._get_processed_params(page, per_page, limit, risk, sort_by, order)
        effective_per_page = limit if limit is not None else per_page

        # 2. 資料庫查詢
        try:
            paginated_data = self.patient_repository.find_all_by_therapist_id(
                therapist_id=therapist_id,
                page=page,
                per_page=effective_per_page,
                sort_by=sort_by,
                order=order
            )
        except Exception as e:
            # 在實際應用中，這裡應該記錄錯誤日誌
            print(f"Error fetching patients from repository: {e}")
            return {"error": {"code": "DB_ERROR", "message": "Database query failed"}}, 500

        # 3. 風險篩選與資料格式化
        patient_list = []
        all_items = paginated_data.items

        if risk:
            filtered_items = []
            for user, health_profile in all_items:
                risk_level = calculate_patient_risk(user.id)
                if risk_level == risk:
                    filtered_items.append((user, health_profile, risk_level))
            items_to_format = filtered_items
        else:
            items_to_format = [(user, hp, calculate_patient_risk(user.id)) for user, hp in all_items]

        for user, health_profile, calculated_risk in items_to_format:
            patient_info = {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "gender": user.gender,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "risk_level": calculated_risk,
                # TODO: 待問卷模型完成後，補上 last_cat_score 和 last_mmrc_score
                "last_cat_score": None,
                "last_mmrc_score": None
            }
            patient_list.append(patient_info)

        # 4. 準備回傳結果
        total_items = len(patient_list) if risk else paginated_data.total
        total_pages = (total_items + effective_per_page - 1) // effective_per_page if effective_per_page > 0 else 0

        response_data = {
            "data": patient_list,
            "pagination": {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "per_page": effective_per_page,
            },
            "filters": {
                "risk": risk,
                "limit": limit,
                "sort_by": sort_by,
                "order": order
            }
        }
        
        if not risk:
            response_data["pagination"]["has_next"] = paginated_data.has_next
            response_data["pagination"]["has_prev"] = paginated_data.has_prev
        else:
            response_data["pagination"]["has_next"] = (page * effective_per_page) < total_items
            response_data["pagination"]["has_prev"] = page > 1

        return response_data, 200

    def _validate_and_prepare_params(self, page, per_page, limit, risk, sort_by, order):
        errors = []
        # 驗證 page
        try:
            page = int(page)
            if page < 1:
                errors.append("Page must be a positive integer.")
        except (ValueError, TypeError):
            errors.append("Page must be an integer.")

        # 驗證 per_page
        if per_page is not None:
            try:
                per_page = int(per_page)
                if per_page < 1:
                    errors.append("Per page must be a positive integer.")
            except (ValueError, TypeError):
                errors.append("Per page must be an integer.")

        # 驗證 limit
        if limit is not None:
            try:
                limit = int(limit)
                if limit < 1:
                    errors.append("Limit must be a positive integer.")
            except (ValueError, TypeError):
                errors.append("Limit must be an integer.")

        # 驗證 risk
        if risk and risk.lower() not in ['high', 'medium', 'low']:
            errors.append("Invalid risk level. Must be 'high', 'medium', or 'low'.")

        # 驗證 sort_by
        allowed_sort_fields = ['created_at', 'last_login', 'first_name', 'last_name']
        if sort_by not in allowed_sort_fields:
            errors.append(f"Invalid sort_by field. Allowed fields are: {', '.join(allowed_sort_fields)}")

        # 驗證 order
        if order.lower() not in ['asc', 'desc']:
            errors.append("Invalid order value. Must be 'asc' or 'desc'.")

        if errors:
            return {"error": {"code": "VALIDATION_ERROR", "message": "Invalid query parameters", "details": errors}}, 400
        return None

    def _get_processed_params(self, page, per_page, limit, risk, sort_by, order):
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        limit = int(limit) if limit else None
        risk = risk.lower() if risk else None
        sort_by = sort_by if sort_by else 'last_login'
        order = order.lower() if order else 'desc'
        return page, per_page, limit, risk, sort_by, order

    def get_patient_profile(self, patient_id):
        """
        獲取單一病患的詳細檔案。
        """
        return self.patient_repository.find_profile_by_user_id(patient_id)

    def calculate_patient_kpis(self, patient_id, days=7):
        """
        計算個別病患的 KPI 指標
        """
        # ... (此處省略了 calculate_patient_kpis 的實現細節)
        pass



def calculate_patient_risk(user_id):
    """
    計算病患的風險等級。
    
    Args:
        user_id: 病患ID
        
    Returns:
        str: 'high', 'medium', 或 'low'
    """
    try:
        # 使用 Flask-SQLAlchemy 的 session 方式
        result = db.session.execute(text("""
            SELECT 
                COALESCE(MAX(cat.total_score), 0) as cat_score,
                COALESCE(MAX(mmrc.score), 0) as mmrc_score
            FROM users u
            LEFT JOIN questionnaire_cat cat ON u.id = cat.user_id
            LEFT JOIN questionnaire_mmrc mmrc ON u.id = mmrc.user_id
            WHERE u.id = :user_id
            GROUP BY u.id
        """), {"user_id": user_id})
        
        row = result.fetchone()
        if row:
            cat_score = row[0] or 0
            mmrc_score = row[1] or 0
            
            # 風險等級判斷
            if cat_score >= 20 or mmrc_score >= 3:
                return 'high'
            elif cat_score >= 10 or mmrc_score >= 2:
                return 'medium'
            else:
                return 'low'
        
        return 'low'  # 預設低風險
        
    except Exception as e:
        print(f"計算風險等級失敗: {e}")
        return 'low'

def calculate_patient_kpis(patient_id, days=7):
    """
    計算個別病患的 KPI 指標
    
    Args:
        patient_id: 病患ID
        days: 計算天數範圍（默認7天）
        
    Returns:
        dict: 包含各種 KPI 指標的字典
    """
    try:
        from ..core.questionnaire_service import QuestionnaireService
        from ..core.daily_metric_service import DailyMetricService
        from datetime import datetime, timedelta
        
        # 服務實例
        q_service = QuestionnaireService()
        dm_service = DailyMetricService()
        
        # 計算日期範圍
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 1. 獲取最新問卷分數
        cat_history, _ = q_service.get_cat_history(patient_id, page=1, per_page=1)
        mmrc_history, _ = q_service.get_mmrc_history(patient_id, page=1, per_page=1)
        
        latest_cat = cat_history.items[0].total_score if cat_history and cat_history.items else 0
        latest_mmrc = mmrc_history.items[0].score if mmrc_history and mmrc_history.items else 0
        
        # 2. 獲取指定天數的每日記錄
        daily_metrics, _ = dm_service.get_daily_metrics(
            patient_id,
            start_date.isoformat(),
            end_date.isoformat(),
            page=1,
            per_page=days
        )
        
        metrics_list = daily_metrics.items if daily_metrics else []
        
        # 3. 計算依從性相關指標
        total_days = len(metrics_list)
        medication_taken_count = sum(1 for m in metrics_list if m.medication)
        adherence_rate = medication_taken_count / max(total_days, 1)
        
        # 報告率（實際記錄天數 / 總天數）
        report_rate = total_days / days
        
        # 完成度（基於多個指標的複合分數）
        completion_score = 0
        if metrics_list:
            # 計算各項指標的完整性
            water_records = sum(1 for m in metrics_list if m.water_cc and m.water_cc > 0)
            exercise_records = sum(1 for m in metrics_list if m.exercise_min and m.exercise_min > 0)
            completion_score = (water_records + exercise_records + medication_taken_count) / (3 * max(total_days, 1))
        
        # 最後記錄天數
        last_record_date = max([m.created_at.date() for m in metrics_list]) if metrics_list else None
        last_report_days = (end_date - last_record_date).days if last_record_date else 999
        
        return {
            "cat_latest": latest_cat,
            "mmrc_latest": latest_mmrc,
            "adherence_7d": round(adherence_rate, 3),
            "report_rate_7d": round(report_rate, 3),
            "completion_7d": round(completion_score, 3),
            "last_report_days": last_report_days,
            "risk_level": calculate_patient_risk(patient_id),
            "metrics_summary": {
                "total_records": total_days,
                "medication_taken_days": medication_taken_count,
                "avg_water_cc": round(sum(m.water_cc for m in metrics_list if m.water_cc) / max(total_days, 1), 0) if total_days > 0 else 0,
                "avg_exercise_min": round(sum(m.exercise_min for m in metrics_list if m.exercise_min) / max(total_days, 1), 0) if total_days > 0 else 0,
                "total_cigarettes": sum(m.cigarettes for m in metrics_list if m.cigarettes) if total_days > 0 else 0
            }
        }
        
    except Exception as e:
        import logging
        logging.error(f"Error calculating patient KPIs for patient {patient_id}: {e}", exc_info=True)
        # 返回安全的默認值
        return {
            "cat_latest": 0,
            "mmrc_latest": 0,
            "adherence_7d": 0.0,
            "report_rate_7d": 0.0,
            "completion_7d": 0.0,
            "last_report_days": 999,
            "risk_level": "low",
            "metrics_summary": {
                "total_records": 0,
                "medication_taken_days": 0,
                "avg_water_cc": 0,
                "avg_exercise_min": 0,
                "total_cigarettes": 0
            }
        }

def get_patient_profile(patient_id):
    """
    獲取單一病患的詳細檔案。
    """
    repo = PatientRepository()
    return repo.find_profile_by_user_id(patient_id)
