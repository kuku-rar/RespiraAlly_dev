"""
Questionnaire Domain Models

Pure Python data classes representing questionnaires in our domain.
These classes contain the business logic for questionnaire scoring and validation.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class QuestionnaireType(Enum):
    CAT = "cat"
    MMRC = "mmrc"


@dataclass
class CATQuestionnaire:
    """COPD Assessment Test questionnaire domain object"""
    record_id: Optional[int] = None
    patient_id: int = 0
    record_date: Optional[date] = None
    cough_score: int = 0
    phlegm_score: int = 0
    chest_score: int = 0
    breath_score: int = 0
    limit_score: int = 0
    confidence_score: int = 0
    sleep_score: int = 0
    energy_score: int = 0
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate scores after initialization"""
        self.validate_scores()

    def validate_scores(self) -> None:
        """Validate that all scores are within valid range (0-5)"""
        scores = [
            self.cough_score, self.phlegm_score, self.chest_score, self.breath_score,
            self.limit_score, self.confidence_score, self.sleep_score, self.energy_score
        ]

        for score in scores:
            if not isinstance(score, int) or score < 0 or score > 5:
                raise ValueError(f"CAT scores must be integers between 0 and 5, got: {score}")

    @property
    def total_score(self) -> int:
        """Calculate total CAT score (sum of all individual scores)"""
        return (
            self.cough_score + self.phlegm_score + self.chest_score + self.breath_score +
            self.limit_score + self.confidence_score + self.sleep_score + self.energy_score
        )

    def get_severity_level(self) -> str:
        """
        Get CAT severity level based on total score

        CAT Severity Levels:
        - 0-10: Low impact
        - 11-20: Medium impact
        - 21-30: High impact
        - 31-40: Very high impact
        """
        total = self.total_score

        if total <= 10:
            return "low"
        elif total <= 20:
            return "medium"
        elif total <= 30:
            return "high"
        else:
            return "very_high"

    def is_improvement(self, previous_score: Optional[int]) -> Optional[bool]:
        """
        Check if this score shows improvement compared to previous score

        Returns:
            True if improved (lower score), False if worsened, None if no previous score
        """
        if previous_score is None:
            return None

        return self.total_score < previous_score

    def get_score_breakdown(self) -> dict:
        """Get detailed breakdown of all scores"""
        return {
            "cough": self.cough_score,
            "phlegm": self.phlegm_score,
            "chest": self.chest_score,
            "breath": self.breath_score,
            "limit": self.limit_score,
            "confidence": self.confidence_score,
            "sleep": self.sleep_score,
            "energy": self.energy_score,
            "total": self.total_score,
            "severity": self.get_severity_level()
        }

    def to_dict(self) -> dict:
        """Convert questionnaire to dictionary representation"""
        return {
            "record_id": self.record_id,
            "patient_id": self.patient_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "scores": self.get_score_breakdown(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class MMRCQuestionnaire:
    """Modified Medical Research Council Dyspnea Scale questionnaire domain object"""
    record_id: Optional[int] = None
    patient_id: int = 0
    record_date: Optional[date] = None
    score: int = 0
    answer_text: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate score after initialization"""
        self.validate_score()

    def validate_score(self) -> None:
        """Validate that score is within valid range (0-4)"""
        if not isinstance(self.score, int) or self.score < 0 or self.score > 4:
            raise ValueError(f"MMRC score must be an integer between 0 and 4, got: {self.score}")

    def get_severity_level(self) -> str:
        """
        Get MMRC severity level based on score

        MMRC Severity Levels:
        - 0-1: Mild
        - 2: Moderate
        - 3-4: Severe
        """
        if self.score <= 1:
            return "mild"
        elif self.score == 2:
            return "moderate"
        else:
            return "severe"

    def is_improvement(self, previous_score: Optional[int]) -> Optional[bool]:
        """
        Check if this score shows improvement compared to previous score

        For MMRC, lower scores are better (less dyspnea)

        Returns:
            True if improved (lower score), False if worsened, None if no previous score
        """
        if previous_score is None:
            return None

        return self.score < previous_score

    def get_standard_answer_text(self) -> str:
        """Get standardized answer text based on score"""
        standard_answers = {
            0: "我只有在劇烈運動時才會感到氣促",
            1: "我在平地快走或走上緩坡時會感到氣促",
            2: "由於氣促，我在平地上走路比同齡人慢，或者需要停下來喘氣",
            3: "我在平地上走大約100公尺或幾分鐘後必須停下來喘氣",
            4: "我氣促得太厲害，無法離開家，或者在穿衣或脫衣時會感到氣促"
        }
        return standard_answers.get(self.score, "")

    def to_dict(self) -> dict:
        """Convert questionnaire to dictionary representation"""
        return {
            "record_id": self.record_id,
            "patient_id": self.patient_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "score": self.score,
            "severity": self.get_severity_level(),
            "answer_text": self.answer_text or self.get_standard_answer_text(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class QuestionnaireAnalyzer:
    """Utility class for analyzing questionnaire trends and patterns"""

    @staticmethod
    def calculate_trend(scores: List[int]) -> str:
        """
        Calculate trend direction for a series of scores

        Returns:
            "improving" if generally decreasing (better for CAT/MMRC)
            "worsening" if generally increasing
            "stable" if no clear trend
        """
        if len(scores) < 2:
            return "stable"

        # Simple trend calculation: compare first half vs second half
        mid_point = len(scores) // 2
        first_half_avg = sum(scores[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)

        if second_half_avg < first_half_avg - 1:  # Improvement threshold
            return "improving"
        elif second_half_avg > first_half_avg + 1:  # Worsening threshold
            return "worsening"
        else:
            return "stable"

    @staticmethod
    def identify_concerning_pattern(cat_scores: List[int], mmrc_scores: List[int]) -> Optional[str]:
        """
        Identify concerning patterns in questionnaire scores

        Returns description of concerning pattern or None if no pattern detected
        """
        # Check for consistently high CAT scores
        if cat_scores and len([s for s in cat_scores[-3:] if s >= 20]) >= 2:
            return "consistently_high_cat_scores"

        # Check for increasing MMRC trend
        if len(mmrc_scores) >= 3:
            recent_mmrc = mmrc_scores[-3:]
            if all(recent_mmrc[i] <= recent_mmrc[i+1] for i in range(len(recent_mmrc)-1)):
                return "worsening_mmrc_trend"

        # Check for sudden deterioration
        if cat_scores and len(cat_scores) >= 2:
            if cat_scores[-1] - cat_scores[-2] >= 8:  # Significant jump in CAT score
                return "sudden_cat_deterioration"

        if mmrc_scores and len(mmrc_scores) >= 2:
            if mmrc_scores[-1] - mmrc_scores[-2] >= 2:  # Significant jump in MMRC score
                return "sudden_mmrc_deterioration"

        return None