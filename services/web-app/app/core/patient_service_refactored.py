"""
Refactored Patient Service

This service uses pure domain objects instead of SQLAlchemy models.
It demonstrates the separation of concerns as outlined in the refactoring plan.

Business logic has been moved into the domain objects themselves,
while this service orchestrates the workflow.
"""

from typing import List, Optional, Tuple, Dict, Any
from .patient_repository import PatientRepository
from .questionnaire_repository import QuestionnaireRepository
from .daily_metric_repository import DailyMetricRepository
from .mappers.patient_mapper import PatientMapper, UserMapper
from .mappers.questionnaire_mapper import QuestionnaireMapper
from .mappers.daily_metric_mapper import DailyMetricMapper
from .domain.patient import Patient, RiskLevel
from .domain.user import User as DomainUser
from .domain.questionnaire import CATQuestionnaire, MMRCQuestionnaire, QuestionnaireAnalyzer
from .domain.daily_metric import DailyMetric, MetricAnalyzer
from datetime import datetime, timedelta


class PatientService:
    """
    Refactored Patient Service using domain objects

    This service coordinates between repositories and domain objects,
    but delegates business logic to the domain objects themselves.
    """

    def __init__(self):
        self.patient_repository = PatientRepository()
        self.questionnaire_repository = QuestionnaireRepository()
        self.daily_metric_repository = DailyMetricRepository()

    def get_patients_by_therapist(self, therapist_id: int, **query_params) -> Tuple[Dict[str, Any], int]:
        """
        Get patients managed by a therapist with filtering and pagination

        Uses domain objects for business logic like risk calculation
        """
        # 1. Parameter validation
        error_response = self._validate_query_params(query_params)
        if error_response:
            return error_response

        processed_params = self._process_query_params(query_params)

        # 2. Fetch from repository
        try:
            paginated_data = self.patient_repository.find_all_by_therapist_id(
                therapist_id=therapist_id,
                page=processed_params['page'],
                per_page=processed_params['per_page'],
                sort_by=processed_params['sort_by'],
                order=processed_params['order']
            )
        except Exception as e:
            return {"error": {"code": "DB_ERROR", "message": "Database query failed"}}, 500

        # 3. Convert to domain objects and apply business logic
        patients = []
        for sql_user, sql_health_profile in paginated_data.items:
            # Convert to domain object
            patient = PatientMapper.to_domain(sql_user, sql_health_profile)

            # Get recent questionnaire scores for risk calculation
            recent_cat_scores = self._get_recent_cat_scores(patient.user_id)
            recent_mmrc_scores = self._get_recent_mmrc_scores(patient.user_id)

            # Calculate risk using domain logic
            risk_level = patient.calculate_risk_level(recent_cat_scores, recent_mmrc_scores)

            # Apply risk filter if specified
            if processed_params['risk'] and risk_level.value != processed_params['risk']:
                continue

            patients.append({
                "patient": patient,
                "risk_level": risk_level.value,
                "latest_cat_score": recent_cat_scores[0] if recent_cat_scores else None,
                "latest_mmrc_score": recent_mmrc_scores[0] if recent_mmrc_scores else None
            })

        # 4. Format response
        patient_list = [self._format_patient_summary(p) for p in patients]

        return self._build_pagination_response(
            patient_list, paginated_data, processed_params
        ), 200

    def get_patient_profile(self, patient_id: int) -> Optional[Tuple[Patient, DomainUser]]:
        """Get detailed patient profile using domain objects"""
        sql_user = self.patient_repository.find_user_by_id(patient_id)
        if not sql_user:
            return None

        # Convert to domain objects
        patient = PatientMapper.to_domain(sql_user)
        user = UserMapper.to_domain(sql_user)

        return patient, user

    def calculate_patient_kpis(self, patient_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Calculate patient KPIs using domain object business logic

        This demonstrates how business logic is now encapsulated in domain objects
        """
        # Get patient domain object
        sql_user = self.patient_repository.find_user_by_id(patient_id)
        if not sql_user:
            raise ValueError("Patient not found")

        patient = PatientMapper.to_domain(sql_user)

        # Get recent data
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get recent questionnaires
        recent_cats = self._get_recent_cat_questionnaires(patient_id, cutoff_date)
        recent_mmrcs = self._get_recent_mmrc_questionnaires(patient_id, cutoff_date)

        # Get recent daily metrics
        recent_metrics = self._get_recent_daily_metrics(patient_id, cutoff_date)

        # Calculate KPIs using domain object business logic
        cat_scores = [cat.total_score for cat in recent_cats]
        mmrc_scores = [mmrc.score for mmrc in recent_mmrcs]

        # Risk assessment using domain logic
        risk_level = patient.calculate_risk_level(cat_scores, mmrc_scores)

        # Adherence calculation using domain logic
        expected_entries = days
        actual_entries = len(recent_metrics)
        adherence_score = patient.calculate_adherence_score(expected_entries, actual_entries)

        # Metric analysis using domain logic
        weekly_summary = MetricAnalyzer.calculate_weekly_summary(recent_metrics)
        concerning_patterns = MetricAnalyzer.identify_concerning_patterns(recent_metrics)

        # Questionnaire trend analysis
        cat_trend = QuestionnaireAnalyzer.calculate_trend(cat_scores) if cat_scores else "stable"
        mmrc_trend = QuestionnaireAnalyzer.calculate_trend(mmrc_scores) if mmrc_scores else "stable"
        concerning_questionnaire_pattern = QuestionnaireAnalyzer.identify_concerning_pattern(cat_scores, mmrc_scores)

        # Check if follow-up needed using domain logic
        days_since_last_entry = self._calculate_days_since_last_entry(recent_metrics)
        needs_followup = patient.needs_followup(days_since_last_entry, risk_level)

        return {
            "patient_overview": {
                "user_id": patient.user_id,
                "full_name": patient.full_name,
                "risk_level": risk_level.value,
                "bmi": patient.health_profile.calculate_bmi() if patient.health_profile else None,
                "smoking_risk": patient.is_smoking_risk()
            },
            "adherence": {
                "overall_score": adherence_score,
                "expected_entries": expected_entries,
                "actual_entries": actual_entries,
                "weekly_summary": weekly_summary
            },
            "questionnaires": {
                "latest_cat_score": cat_scores[0] if cat_scores else None,
                "latest_mmrc_score": mmrc_scores[0] if mmrc_scores else None,
                "cat_trend": cat_trend,
                "mmrc_trend": mmrc_trend,
                "total_cat_entries": len(recent_cats),
                "total_mmrc_entries": len(recent_mmrcs)
            },
            "alerts": {
                "needs_followup": needs_followup,
                "days_since_last_entry": days_since_last_entry,
                "concerning_metric_patterns": concerning_patterns,
                "concerning_questionnaire_pattern": concerning_questionnaire_pattern
            }
        }

    def _get_recent_cat_scores(self, patient_id: int, limit: int = 5) -> List[int]:
        """Get recent CAT scores for risk calculation"""
        try:
            sql_cats = self.questionnaire_repository.get_recent_cat_records(patient_id, limit)
            return [cat.total_score for cat in sql_cats]
        except:
            return []

    def _get_recent_mmrc_scores(self, patient_id: int, limit: int = 5) -> List[int]:
        """Get recent MMRC scores for risk calculation"""
        try:
            sql_mmrcs = self.questionnaire_repository.get_recent_mmrc_records(patient_id, limit)
            return [mmrc.score for mmrc in sql_mmrcs]
        except:
            return []

    def _get_recent_cat_questionnaires(self, patient_id: int, cutoff_date: datetime) -> List[CATQuestionnaire]:
        """Get recent CAT questionnaires as domain objects"""
        sql_cats = self.questionnaire_repository.get_cat_since_date(patient_id, cutoff_date)
        return QuestionnaireMapper.cat_list_to_domain(sql_cats)

    def _get_recent_mmrc_questionnaires(self, patient_id: int, cutoff_date: datetime) -> List[MMRCQuestionnaire]:
        """Get recent MMRC questionnaires as domain objects"""
        sql_mmrcs = self.questionnaire_repository.get_mmrc_since_date(patient_id, cutoff_date)
        return QuestionnaireMapper.mmrc_list_to_domain(sql_mmrcs)

    def _get_recent_daily_metrics(self, patient_id: int, cutoff_date: datetime) -> List[DailyMetric]:
        """Get recent daily metrics as domain objects"""
        sql_metrics = self.daily_metric_repository.get_metrics_since_date(patient_id, cutoff_date)
        return DailyMetricMapper.list_to_domain(sql_metrics)

    def _calculate_days_since_last_entry(self, metrics: List[DailyMetric]) -> int:
        """Calculate days since last metric entry"""
        if not metrics:
            return 999  # Large number if no entries

        latest_entry = max(metrics, key=lambda m: m.created_at or datetime.min)
        if not latest_entry.created_at:
            return 999

        days_diff = (datetime.utcnow() - latest_entry.created_at).days
        return max(0, days_diff)

    def _validate_query_params(self, params: Dict[str, Any]) -> Optional[Tuple[Dict[str, Any], int]]:
        """Validate query parameters"""
        errors = []

        # Validate page
        page = params.get('page', 1)
        try:
            page = int(page)
            if page < 1:
                errors.append("Page must be >= 1")
        except (ValueError, TypeError):
            errors.append("Page must be a valid integer")

        # Validate per_page
        per_page = params.get('per_page', 20)
        try:
            per_page = int(per_page)
            if per_page < 1 or per_page > 100:
                errors.append("Per_page must be between 1 and 100")
        except (ValueError, TypeError):
            errors.append("Per_page must be a valid integer")

        # Validate risk
        risk = params.get('risk')
        if risk and risk not in ['low', 'medium', 'high']:
            errors.append("Risk must be one of: low, medium, high")

        if errors:
            return {"error": {"code": "INVALID_PARAMS", "message": "; ".join(errors)}}, 400

        return None

    def _process_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and set defaults for query parameters"""
        return {
            'page': int(params.get('page', 1)),
            'per_page': min(int(params.get('per_page', 20)), int(params.get('limit', 20))),
            'risk': params.get('risk'),
            'sort_by': params.get('sort_by', 'last_login'),
            'order': params.get('order', 'desc')
        }

    def _format_patient_summary(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format patient data for API response"""
        patient = patient_data['patient']
        return {
            "user_id": patient.user_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "full_name": patient.full_name,
            "gender": patient.gender.value if patient.gender else None,
            "last_login": patient.last_login.isoformat() if patient.last_login else None,
            "risk_level": patient_data['risk_level'],
            "last_cat_score": patient_data['latest_cat_score'],
            "last_mmrc_score": patient_data['latest_mmrc_score'],
            "bmi": patient.health_profile.calculate_bmi() if patient.health_profile else None,
            "smoking_risk": patient.is_smoking_risk()
        }

    def _build_pagination_response(self, data: List[Dict], paginated_data, params: Dict) -> Dict[str, Any]:
        """Build paginated response"""
        return {
            "data": data,
            "pagination": {
                "total_items": len(data) if params['risk'] else paginated_data.total,
                "total_pages": paginated_data.pages,
                "current_page": params['page'],
                "per_page": params['per_page'],
                "has_next": paginated_data.has_next,
                "has_prev": paginated_data.has_prev
            },
            "filters": {
                "risk": params['risk'],
                "sort_by": params['sort_by'],
                "order": params['order']
            }
        }