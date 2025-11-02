"""
Patient Domain Model

Pure Python data class representing a Patient in our domain.
This class knows nothing about databases or HTTP - it only contains
the essential data and business logic for a Patient.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class SmokeStatus(Enum):
    NEVER = "never"
    FORMER = "former"
    CURRENT = "current"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class HealthProfile:
    """Patient's health profile information"""
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    smoke_status: Optional[SmokeStatus] = None
    updated_at: Optional[datetime] = None

    def calculate_bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight are available"""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m * height_m), 1)
        return None

    def get_bmi_category(self) -> Optional[str]:
        """Get BMI category based on calculated BMI"""
        bmi = self.calculate_bmi()
        if bmi is None:
            return None

        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"


@dataclass
class Patient:
    """Core Patient domain object"""
    user_id: int
    first_name: str
    last_name: str
    gender: Optional[Gender] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    line_user_id: Optional[str] = None
    health_profile: Optional[HealthProfile] = None
    therapist_id: Optional[int] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        return f"{self.last_name}{self.first_name}"

    def calculate_risk_level(self, recent_cat_scores: List[int], recent_mmrc_scores: List[int]) -> RiskLevel:
        """
        Calculate patient's current risk level based on recent questionnaire scores

        Business Logic for Risk Assessment:
        - HIGH: Latest CAT score ≥ 20 OR latest MMRC score ≥ 3
        - MEDIUM: Latest CAT score 10-19 OR latest MMRC score 2
        - LOW: Latest CAT score < 10 AND latest MMRC score ≤ 1
        """
        latest_cat = recent_cat_scores[0] if recent_cat_scores else None
        latest_mmrc = recent_mmrc_scores[0] if recent_mmrc_scores else None

        # High risk conditions
        if latest_cat is not None and latest_cat >= 20:
            return RiskLevel.HIGH
        if latest_mmrc is not None and latest_mmrc >= 3:
            return RiskLevel.HIGH

        # Medium risk conditions
        if latest_cat is not None and 10 <= latest_cat < 20:
            return RiskLevel.MEDIUM
        if latest_mmrc is not None and latest_mmrc == 2:
            return RiskLevel.MEDIUM

        # Low risk (default if no high/medium risk factors)
        return RiskLevel.LOW

    def is_smoking_risk(self) -> bool:
        """Check if patient has smoking-related risk"""
        if not self.health_profile:
            return False
        return self.health_profile.smoke_status == SmokeStatus.CURRENT

    def calculate_adherence_score(self, total_expected_entries: int, actual_entries: int) -> float:
        """
        Calculate patient adherence score as percentage

        Args:
            total_expected_entries: Number of expected daily metric entries
            actual_entries: Number of actual entries submitted

        Returns:
            Adherence score as percentage (0.0 to 100.0)
        """
        if total_expected_entries == 0:
            return 100.0

        return min(100.0, (actual_entries / total_expected_entries) * 100)

    def needs_followup(self, days_since_last_entry: int, risk_level: RiskLevel) -> bool:
        """
        Determine if patient needs follow-up based on inactivity and risk level

        Business Rules:
        - HIGH risk: Follow-up if no entry for ≥ 2 days
        - MEDIUM risk: Follow-up if no entry for ≥ 3 days
        - LOW risk: Follow-up if no entry for ≥ 5 days
        """
        thresholds = {
            RiskLevel.HIGH: 2,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 5
        }

        return days_since_last_entry >= thresholds[risk_level]

    def to_dict(self) -> dict:
        """Convert patient to dictionary representation"""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "gender": self.gender.value if self.gender else None,
            "email": self.email,
            "phone": self.phone,
            "line_user_id": self.line_user_id,
            "health_profile": {
                "height_cm": self.health_profile.height_cm if self.health_profile else None,
                "weight_kg": self.health_profile.weight_kg if self.health_profile else None,
                "smoke_status": self.health_profile.smoke_status.value if self.health_profile and self.health_profile.smoke_status else None,
                "bmi": self.health_profile.calculate_bmi() if self.health_profile else None,
                "bmi_category": self.health_profile.get_bmi_category() if self.health_profile else None,
                "updated_at": self.health_profile.updated_at.isoformat() if self.health_profile and self.health_profile.updated_at else None
            } if self.health_profile else None,
            "therapist_id": self.therapist_id,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }