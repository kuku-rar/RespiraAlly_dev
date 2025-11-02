"""
Daily Metric Domain Model

Pure Python data class representing daily health metrics in our domain.
Contains business logic for metric validation and analysis.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum


class AdherenceLevel(Enum):
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # <50%


@dataclass
class DailyMetric:
    """Daily health metric domain object"""
    log_id: Optional[int] = None
    patient_id: int = 0
    water_cc: Optional[int] = None
    medication: Optional[bool] = None
    exercise_min: Optional[int] = None
    cigarettes: Optional[int] = None
    log_date: Optional[date] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate metrics after initialization"""
        self.validate_metrics()

    def validate_metrics(self) -> None:
        """Validate that metrics are within reasonable ranges"""
        if self.water_cc is not None:
            if not isinstance(self.water_cc, int) or self.water_cc < 0 or self.water_cc > 10000:
                raise ValueError(f"Water intake must be between 0-10000cc, got: {self.water_cc}")

        if self.exercise_min is not None:
            if not isinstance(self.exercise_min, int) or self.exercise_min < 0 or self.exercise_min > 1440:
                raise ValueError(f"Exercise minutes must be between 0-1440 minutes, got: {self.exercise_min}")

        if self.cigarettes is not None:
            if not isinstance(self.cigarettes, int) or self.cigarettes < 0 or self.cigarettes > 200:
                raise ValueError(f"Cigarettes must be between 0-200, got: {self.cigarettes}")

    def is_hydration_adequate(self) -> Optional[bool]:
        """
        Check if daily water intake is adequate

        Adequate hydration: ≥ 1500cc per day for COPD patients
        """
        if self.water_cc is None:
            return None
        return self.water_cc >= 1500

    def is_exercise_target_met(self) -> Optional[bool]:
        """
        Check if daily exercise target is met

        Target: ≥ 30 minutes of exercise per day
        """
        if self.exercise_min is None:
            return None
        return self.exercise_min >= 30

    def is_medication_compliant(self) -> Optional[bool]:
        """Check if medication was taken as prescribed"""
        return self.medication

    def has_smoking_incident(self) -> bool:
        """Check if patient smoked any cigarettes"""
        return self.cigarettes is not None and self.cigarettes > 0

    def calculate_daily_score(self) -> float:
        """
        Calculate overall daily health score (0-100)

        Scoring:
        - Medication compliance: 40 points
        - Adequate hydration: 30 points
        - Exercise target met: 20 points
        - No smoking: 10 points
        """
        score = 0.0
        total_possible = 0

        # Medication compliance (40 points)
        if self.medication is not None:
            total_possible += 40
            if self.medication:
                score += 40

        # Hydration (30 points)
        if self.water_cc is not None:
            total_possible += 30
            if self.is_hydration_adequate():
                score += 30

        # Exercise (20 points)
        if self.exercise_min is not None:
            total_possible += 20
            if self.is_exercise_target_met():
                score += 20

        # No smoking (10 points)
        if self.cigarettes is not None:
            total_possible += 10
            if not self.has_smoking_incident():
                score += 10

        # Return percentage score
        if total_possible == 0:
            return 0.0

        return (score / total_possible) * 100

    def get_health_alerts(self) -> List[str]:
        """Get list of health alerts based on the daily metrics"""
        alerts = []

        if self.medication is not None and not self.medication:
            alerts.append("medication_missed")

        if self.water_cc is not None and not self.is_hydration_adequate():
            alerts.append("low_hydration")

        if self.cigarettes is not None and self.cigarettes > 0:
            if self.cigarettes > 10:
                alerts.append("heavy_smoking")
            else:
                alerts.append("smoking_incident")

        if self.exercise_min is not None and self.exercise_min == 0:
            alerts.append("no_exercise")

        return alerts

    def to_dict(self) -> dict:
        """Convert metric to dictionary representation"""
        return {
            "log_id": self.log_id,
            "patient_id": self.patient_id,
            "log_date": self.log_date.isoformat() if self.log_date else None,
            "metrics": {
                "water_cc": self.water_cc,
                "medication": self.medication,
                "exercise_min": self.exercise_min,
                "cigarettes": self.cigarettes
            },
            "analysis": {
                "daily_score": self.calculate_daily_score(),
                "hydration_adequate": self.is_hydration_adequate(),
                "exercise_target_met": self.is_exercise_target_met(),
                "medication_compliant": self.is_medication_compliant(),
                "smoking_incident": self.has_smoking_incident(),
                "health_alerts": self.get_health_alerts()
            },
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MetricAnalyzer:
    """Utility class for analyzing daily metric trends and patterns"""

    @staticmethod
    def calculate_adherence_rate(metrics: List[DailyMetric], metric_type: str) -> float:
        """
        Calculate adherence rate for a specific metric type

        Args:
            metrics: List of daily metrics
            metric_type: 'medication', 'hydration', or 'exercise'

        Returns:
            Adherence rate as percentage (0.0-100.0)
        """
        if not metrics:
            return 0.0

        compliant_days = 0
        total_days = 0

        for metric in metrics:
            if metric_type == "medication" and metric.medication is not None:
                total_days += 1
                if metric.medication:
                    compliant_days += 1
            elif metric_type == "hydration" and metric.water_cc is not None:
                total_days += 1
                if metric.is_hydration_adequate():
                    compliant_days += 1
            elif metric_type == "exercise" and metric.exercise_min is not None:
                total_days += 1
                if metric.is_exercise_target_met():
                    compliant_days += 1

        if total_days == 0:
            return 0.0

        return (compliant_days / total_days) * 100

    @staticmethod
    def get_adherence_level(adherence_rate: float) -> AdherenceLevel:
        """Convert adherence rate to categorical level"""
        if adherence_rate >= 90:
            return AdherenceLevel.EXCELLENT
        elif adherence_rate >= 70:
            return AdherenceLevel.GOOD
        elif adherence_rate >= 50:
            return AdherenceLevel.FAIR
        else:
            return AdherenceLevel.POOR

    @staticmethod
    def calculate_weekly_summary(metrics: List[DailyMetric]) -> Dict:
        """Calculate summary statistics for a week of metrics"""
        if not metrics:
            return {}

        # Calculate averages
        water_values = [m.water_cc for m in metrics if m.water_cc is not None]
        exercise_values = [m.exercise_min for m in metrics if m.exercise_min is not None]
        cigarette_values = [m.cigarettes for m in metrics if m.cigarettes is not None]

        # Calculate adherence rates
        medication_adherence = MetricAnalyzer.calculate_adherence_rate(metrics, "medication")
        hydration_adherence = MetricAnalyzer.calculate_adherence_rate(metrics, "hydration")
        exercise_adherence = MetricAnalyzer.calculate_adherence_rate(metrics, "exercise")

        # Calculate daily scores
        daily_scores = [m.calculate_daily_score() for m in metrics]
        avg_daily_score = sum(daily_scores) / len(daily_scores) if daily_scores else 0

        return {
            "period": "weekly",
            "total_days": len(metrics),
            "averages": {
                "water_cc": sum(water_values) / len(water_values) if water_values else None,
                "exercise_min": sum(exercise_values) / len(exercise_values) if exercise_values else None,
                "cigarettes": sum(cigarette_values) / len(cigarette_values) if cigarette_values else None,
                "daily_score": avg_daily_score
            },
            "adherence": {
                "medication": {
                    "rate": medication_adherence,
                    "level": MetricAnalyzer.get_adherence_level(medication_adherence).value
                },
                "hydration": {
                    "rate": hydration_adherence,
                    "level": MetricAnalyzer.get_adherence_level(hydration_adherence).value
                },
                "exercise": {
                    "rate": exercise_adherence,
                    "level": MetricAnalyzer.get_adherence_level(exercise_adherence).value
                }
            },
            "smoking": {
                "days_with_smoking": len([m for m in metrics if m.has_smoking_incident()]),
                "total_cigarettes": sum(cigarette_values) if cigarette_values else 0
            }
        }

    @staticmethod
    def identify_concerning_patterns(metrics: List[DailyMetric]) -> List[str]:
        """Identify concerning patterns in daily metrics"""
        concerns = []

        # Check for consecutive medication non-compliance
        medication_streak = 0
        for metric in reversed(metrics[-7:]):  # Check last 7 days
            if metric.medication is not None:
                if not metric.medication:
                    medication_streak += 1
                else:
                    break

        if medication_streak >= 3:
            concerns.append("consecutive_medication_non_compliance")

        # Check for increasing smoking trend
        if len(metrics) >= 7:
            recent_smoking = sum(m.cigarettes for m in metrics[-7:] if m.cigarettes is not None)
            previous_smoking = sum(m.cigarettes for m in metrics[-14:-7] if m.cigarettes is not None)

            if recent_smoking > previous_smoking * 1.5:  # 50% increase
                concerns.append("increasing_smoking_trend")

        # Check for consistently low exercise
        recent_exercise = [m.exercise_min for m in metrics[-5:] if m.exercise_min is not None]
        if len(recent_exercise) >= 3 and all(e < 15 for e in recent_exercise):
            concerns.append("consistently_low_exercise")

        return concerns