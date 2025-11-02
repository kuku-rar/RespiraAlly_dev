# services/web-app/app/core/daily_metric_repository.py
from sqlalchemy import select
from ..models.models import DailyMetric
from ..extensions import db
from datetime import datetime, date, timezone

class DailyMetricRepository:
    def find_by_user_id_and_date(self, user_id: int, record_date: date):
        """Finds a daily metric by user ID and a specific date."""
        start_of_day = datetime.combine(record_date, datetime.min.time())
        end_of_day = datetime.combine(record_date, datetime.max.time())
        
        stmt = select(DailyMetric).filter(
            DailyMetric.user_id == user_id,
            DailyMetric.created_at >= start_of_day,
            DailyMetric.created_at <= end_of_day
        )
        return db.session.scalars(stmt).first()

    def create_daily_metric(self, user_id, data):
        """
        Creates a new daily metric record in the database.

        Args:
            user_id (int): The ID of the user (patient).
            data (dict): A dictionary containing the metric data.

        Returns:
            DailyMetric: The newly created DailyMetric object.
        """
        daily_metric = DailyMetric(
            user_id=user_id,
            water_cc=data.get('water_cc'),
            medication=data.get('medication'),
            exercise_min=data.get('exercise_min'),
            cigarettes=data.get('cigarettes')
        )
        db.session.add(daily_metric)
        db.session.commit()
        return daily_metric

    def get_metrics_by_user_id_and_date_range(self, user_id, start_date, end_date, page, per_page):
        """
        Retrieves paginated daily metrics for a user within a specific date range.

        Args:
            user_id (int): The ID of the user.
            start_date (date): The start of the date range.
            end_date (date): The end of the date range.
            page (int): The page number for pagination.
            per_page (int): The number of items per page.

        Returns:
            Pagination: A Flask-SQLAlchemy Pagination object.
        """
        start_of_day = datetime.combine(start_date, datetime.min.time())
        end_of_day = datetime.combine(end_date, datetime.max.time())
        
        stmt = select(DailyMetric).filter(
            DailyMetric.user_id == user_id,
            DailyMetric.created_at >= start_of_day,
            DailyMetric.created_at <= end_of_day
        ).order_by(DailyMetric.created_at.desc())

        return db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    def update_daily_metric(self, metric, data):
        """Updates an existing daily metric record."""
        metric.water_cc = data.get('water_cc', metric.water_cc)
        metric.medication = data.get('medication', metric.medication)
        metric.exercise_min = data.get('exercise_min', metric.exercise_min)
        metric.cigarettes = data.get('cigarettes', metric.cigarettes)
        metric.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return metric

