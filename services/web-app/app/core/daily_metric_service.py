# services/web-app/app/core/daily_metric_service.py
from .daily_metric_repository import DailyMetricRepository
from .user_repository import UserRepository
from datetime import datetime, date, timedelta

def _validate_metric_data(data):
    """
    Validates the data types for daily metric fields.
    Returns an error message string if validation fails, otherwise None.
    驗證每日指標字段的數據類型。如果驗證失敗，則返回錯誤消息字符串，否則返回 None。
    """
    expected_types = {
        'water_cc': int,
        'medication': bool,
        'exercise_min': int,
        'cigarettes': int
    }
    errors = []
    for field, expected_type in expected_types.items():
        if field in data and data[field] is not None:
            value = data[field]
            if not isinstance(value, expected_type):
                errors.append(f"'{field}' must be of type {expected_type.__name__}, but got {type(value).__name__}.")
            # Additional value checks
            if isinstance(value, int) and value < 0:
                errors.append(f"'{field}' cannot be negative.")
    
    return "; ".join(errors) if errors else None

class DailyMetricService:
    def __init__(self):
        self.metric_repo = DailyMetricRepository()
        self.user_repo = UserRepository()

    def create_daily_metric(self, patient_id, data):
        """
        處理創建每日度量的業務邏輯。驗證輸入數據，並檢查當前一天的度量是否已經存在。
        """
        validation_error = _validate_metric_data(data)
        if validation_error:
            return None, validation_error

        patient = self.user_repo.find_by_id(patient_id)
        if not patient or patient.is_staff:
            return None, "Patient not found."

        today = date.today()
        existing_metric = self.metric_repo.find_by_user_id_and_date(patient_id, today)
        if existing_metric:
            return None, "A daily metric for today already exists."

        new_metric = self.metric_repo.create_daily_metric(patient_id, data)
        return new_metric, None

    def get_daily_metrics(self, patient_id, start_date_str, end_date_str, page, per_page):
        """
        Handles the business logic for retrieving daily metrics.
        """
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return None, "Invalid start_date format. Please use YYYY-MM-DD."
        else:
            start_date = date.today() - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return None, "Invalid end_date format. Please use YYYY-MM-DD."
        else:
            end_date = date.today()

        if start_date > end_date:
            return None, "Start date cannot be after end date."

        patient = self.user_repo.find_by_id(patient_id)
        if not patient or patient.is_staff:
            return None, "Patient not found."

        paginated_metrics = self.metric_repo.get_metrics_by_user_id_and_date_range(
            patient_id, start_date, end_date, page, per_page
        )
        return paginated_metrics, None

    def update_daily_metric(self, patient_id, log_date_str, data):
        """
        Handles the business logic for updating a daily metric for a specific date.
        Validates input data before proceeding.
        """
        validation_error = _validate_metric_data(data)
        if validation_error:
            return None, validation_error
            
        try:
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        metric_to_update = self.metric_repo.find_by_user_id_and_date(patient_id, log_date)
        if not metric_to_update:
            return None, "Metric not found for the specified date."

        updated_metric = self.metric_repo.update_daily_metric(metric_to_update, data)
        return updated_metric, None
