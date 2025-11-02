"""
Daily Metric Mapper

Converts between SQLAlchemy DailyMetric models and pure domain DailyMetric objects.
"""

from typing import List
from ..domain.daily_metric import DailyMetric
from ...models.models import DailyMetric as SQLDailyMetric


class DailyMetricMapper:
    """Maps between SQLAlchemy DailyMetric models and domain objects"""

    @staticmethod
    def to_domain(sql_metric: SQLDailyMetric) -> DailyMetric:
        """Convert SQLAlchemy DailyMetric to domain DailyMetric"""
        return DailyMetric(
            log_id=sql_metric.id,
            patient_id=sql_metric.user_id,
            water_cc=sql_metric.water_cc,
            medication=sql_metric.medication,
            exercise_min=sql_metric.exercise_min,
            cigarettes=sql_metric.cigarettes,
            log_date=sql_metric.created_at.date() if sql_metric.created_at else None,
            created_at=sql_metric.created_at
        )

    @staticmethod
    def to_sql(domain_metric: DailyMetric, existing_metric: SQLDailyMetric = None) -> SQLDailyMetric:
        """Convert domain DailyMetric to SQLAlchemy DailyMetric"""
        if existing_metric:
            metric = existing_metric
        else:
            metric = SQLDailyMetric()

        metric.user_id = domain_metric.patient_id
        metric.water_cc = domain_metric.water_cc
        metric.medication = domain_metric.medication
        metric.exercise_min = domain_metric.exercise_min
        metric.cigarettes = domain_metric.cigarettes

        return metric

    @staticmethod
    def list_to_domain(sql_metrics: List[SQLDailyMetric]) -> List[DailyMetric]:
        """Convert list of SQLAlchemy DailyMetrics to domain DailyMetrics"""
        return [DailyMetricMapper.to_domain(metric) for metric in sql_metrics]