# services/web-app/app/core/questionnaire_service.py
from .questionnaire_repository import QuestionnaireRepository
from .user_repository import UserRepository
from datetime import date, datetime

class QuestionnaireService:
    def __init__(self):
        self.questionnaire_repo = QuestionnaireRepository()
        self.user_repo = UserRepository()

    def _validate_and_get_patient(self, patient_id: int):
        patient = self.user_repo.find_by_id(patient_id)
        if not patient or patient.is_staff:
            return None
        return patient

    def _calculate_cat_score(self, data: dict) -> int:
        score_fields = [
            'cough_score', 'phlegm_score', 'chest_score', 'breath_score',
            'limit_score', 'confidence_score', 'sleep_score', 'energy_score'
        ]
        return sum(data.get(field, 0) for field in score_fields)

    def submit_cat_questionnaire(self, patient_id: int, data: dict):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."

        # --- START: ADDED VALIDATION ---
        score_fields = [
            'cough_score', 'phlegm_score', 'chest_score', 'breath_score',
            'limit_score', 'confidence_score', 'sleep_score', 'energy_score'
        ]
        for field in score_fields:
            score = data.get(field)
            if not isinstance(score, int) or not (0 <= score <= 5):
                return None, f"Invalid score for {field}. Must be an integer between 0 and 5."
        # --- END: ADDED VALIDATION ---

        try:
            record_date = date.fromisoformat(data['record_date'])
        except (ValueError, KeyError):
            return None, "Invalid or missing record_date."
        if self.questionnaire_repo.find_cat_by_user_id_and_month(patient_id, record_date):
            return None, f"A CAT record for {record_date.year}-{record_date.month} already exists."
        total_score = self._calculate_cat_score(data)
        new_record = self.questionnaire_repo.create_cat_record(patient_id, data, total_score)
        return new_record, None

    def update_cat_questionnaire(self, patient_id: int, year: int, month: int, data: dict):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."

        record_to_find = date(year, month, 1)
        record_to_update = self.questionnaire_repo.find_cat_by_user_id_and_month(patient_id, record_to_find)

        if not record_to_update:
            return None, f"No CAT record found for {year}-{month} to update."

        total_score = self._calculate_cat_score(data)
        data['record_date'] = record_to_update.record_date.isoformat()
        updated_record = self.questionnaire_repo.update_cat_record(record_to_update, data, total_score)
        return updated_record, None

    def get_cat_history(self, patient_id: int, page: int, per_page: int):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."
        return self.questionnaire_repo.get_cat_records_by_user_id(patient_id, page, per_page), None

    def submit_mmrc_questionnaire(self, patient_id: int, data: dict):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."

        # --- START: ADDED VALIDATION ---
        score = data.get('score')
        if not isinstance(score, int) or not (0 <= score <= 4):
            return None, "Invalid score. Must be an integer between 0 and 4."
        # --- END: ADDED VALIDATION ---

        try:
            record_date = date.fromisoformat(data['record_date'])
        except (ValueError, KeyError):
            return None, "Invalid or missing record_date."
        if self.questionnaire_repo.find_mmrc_by_user_id_and_month(patient_id, record_date):
            return None, f"An MMRC record for {record_date.year}-{record_date.month} already exists."
        new_record = self.questionnaire_repo.create_mmrc_record(patient_id, data)
        return new_record, None

    def update_mmrc_questionnaire(self, patient_id: int, year: int, month: int, data: dict):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."

        record_to_find = date(year, month, 1)
        record_to_update = self.questionnaire_repo.find_mmrc_by_user_id_and_month(patient_id, record_to_find)

        if not record_to_update:
            return None, f"No MMRC record found for {year}-{month} to update."

        data['record_date'] = record_to_update.record_date.isoformat()
        updated_record = self.questionnaire_repo.update_mmrc_record(record_to_update, data)
        return updated_record, None

    def get_mmrc_history(self, patient_id: int, page: int, per_page: int):
        if not self._validate_and_get_patient(patient_id):
            return None, "Patient not found."
        return self.questionnaire_repo.get_mmrc_records_by_user_id(patient_id, page, per_page), None
