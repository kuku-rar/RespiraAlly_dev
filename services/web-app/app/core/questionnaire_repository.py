# services/web-app/app/core/questionnaire_repository.py
from sqlalchemy import select, extract
from ..models.models import QuestionnaireCAT, QuestionnaireMMRC
from ..extensions import db
from datetime import date


class QuestionnaireRepository:
    def find_cat_by_user_id_and_month(self, user_id: int, record_date: date) -> QuestionnaireCAT | None:
        """Finds a CAT record by user ID for a specific month and year."""
        stmt = select(QuestionnaireCAT).filter(
            QuestionnaireCAT.user_id == user_id,
            extract('year', QuestionnaireCAT.record_date) == record_date.year,
            extract('month', QuestionnaireCAT.record_date) == record_date.month
        )
        return db.session.scalars(stmt).first()

    def create_cat_record(self, user_id: int, data: dict, total_score: int) -> QuestionnaireCAT:
        """Creates a new CAT questionnaire record."""
        record = QuestionnaireCAT(
            user_id=user_id,
            record_date=date.fromisoformat(data['record_date']),
            cough_score=data['cough_score'],
            phlegm_score=data['phlegm_score'],
            chest_score=data['chest_score'],
            breath_score=data['breath_score'],
            limit_score=data['limit_score'],
            confidence_score=data['confidence_score'],
            sleep_score=data['sleep_score'],
            energy_score=data['energy_score'],
            total_score=total_score
        )
        db.session.add(record)
        db.session.commit()
        return record

    def update_cat_record(self, record: QuestionnaireCAT, data: dict, total_score: int) -> QuestionnaireCAT:
        """Updates an existing CAT record."""
        record.cough_score = data['cough_score']
        record.phlegm_score = data['phlegm_score']
        record.chest_score = data['chest_score']
        record.breath_score = data['breath_score']
        record.limit_score = data['limit_score']
        record.confidence_score = data['confidence_score']
        record.sleep_score = data['sleep_score']
        record.energy_score = data['energy_score']
        record.total_score = total_score
        db.session.commit()
        return record

    def create_mmrc_record(self, user_id: int, data: dict) -> QuestionnaireMMRC:
        """Creates a new MMRC questionnaire record."""
        record = QuestionnaireMMRC(
            user_id=user_id,
            record_date=date.fromisoformat(data['record_date']),
            score=data['score'],
            answer_text=data['answer_text']
        )
        db.session.add(record)
        db.session.commit()
        return record

    def find_mmrc_by_user_id_and_month(self, user_id: int, record_date: date) -> QuestionnaireMMRC | None:
        """Finds an MMRC record by user ID for a specific month and year."""
        stmt = select(QuestionnaireMMRC).filter(
            QuestionnaireMMRC.user_id == user_id,
            extract('year', QuestionnaireMMRC.record_date) == record_date.year,
            extract('month', QuestionnaireMMRC.record_date) == record_date.month
        )
        return db.session.scalars(stmt).first()

    def update_mmrc_record(self, record: QuestionnaireMMRC, data: dict) -> QuestionnaireMMRC:
        """Updates an existing MMRC record."""
        record.score = data['score']
        record.answer_text = data['answer_text']
        db.session.commit()
        return record

    def get_cat_records_by_user_id(self, user_id: int, page: int, per_page: int):
        """Retrieves paginated CAT records for a user."""
        stmt = select(QuestionnaireCAT).filter_by(user_id=user_id)\
            .order_by(QuestionnaireCAT.record_date.desc())
        return db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    def get_mmrc_records_by_user_id(self, user_id: int, page: int, per_page: int):
        """Retrieves paginated MMRC records for a user."""
        stmt = select(QuestionnaireMMRC).filter_by(user_id=user_id)\
            .order_by(QuestionnaireMMRC.record_date.desc())
        return db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    def find_cat_by_user_id_and_date(self, user_id: int, record_date: date) -> QuestionnaireCAT | None:
        """Finds a CAT record by user ID and a specific date."""
        stmt = select(QuestionnaireCAT).filter_by(user_id=user_id, record_date=record_date)
        return db.session.scalars(stmt).first()

    def find_mmrc_by_user_id_and_date(self, user_id: int, record_date: date) -> QuestionnaireMMRC | None:
        """Finds an MMRC record by user ID and a specific date."""
        stmt = select(QuestionnaireMMRC).filter_by(user_id=user_id, record_date=record_date)
        return db.session.scalars(stmt).first()
