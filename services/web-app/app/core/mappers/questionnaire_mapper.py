"""
Questionnaire Mapper

Converts between SQLAlchemy questionnaire models and pure domain questionnaire objects.
"""

from typing import List
from ..domain.questionnaire import CATQuestionnaire, MMRCQuestionnaire
from ...models.models import QuestionnaireCAT as SQLCAT, QuestionnaireMMRC as SQLMMRC


class QuestionnaireMapper:
    """Maps between SQLAlchemy questionnaire models and domain objects"""

    @staticmethod
    def cat_to_domain(sql_cat: SQLCAT) -> CATQuestionnaire:
        """Convert SQLAlchemy CAT to domain CATQuestionnaire"""
        return CATQuestionnaire(
            record_id=sql_cat.id,
            patient_id=sql_cat.user_id,
            record_date=sql_cat.record_date,
            cough_score=sql_cat.cough_score,
            phlegm_score=sql_cat.phlegm_score,
            chest_score=sql_cat.chest_score,
            breath_score=sql_cat.breath_score,
            limit_score=sql_cat.limit_score,
            confidence_score=sql_cat.confidence_score,
            sleep_score=sql_cat.sleep_score,
            energy_score=sql_cat.energy_score,
            created_at=sql_cat.created_at
        )

    @staticmethod
    def cat_to_sql(domain_cat: CATQuestionnaire, existing_cat: SQLCAT = None) -> SQLCAT:
        """Convert domain CATQuestionnaire to SQLAlchemy CAT"""
        if existing_cat:
            cat = existing_cat
        else:
            cat = SQLCAT()

        cat.user_id = domain_cat.patient_id
        cat.record_date = domain_cat.record_date
        cat.cough_score = domain_cat.cough_score
        cat.phlegm_score = domain_cat.phlegm_score
        cat.chest_score = domain_cat.chest_score
        cat.breath_score = domain_cat.breath_score
        cat.limit_score = domain_cat.limit_score
        cat.confidence_score = domain_cat.confidence_score
        cat.sleep_score = domain_cat.sleep_score
        cat.energy_score = domain_cat.energy_score
        cat.total_score = domain_cat.total_score

        return cat

    @staticmethod
    def mmrc_to_domain(sql_mmrc: SQLMMRC) -> MMRCQuestionnaire:
        """Convert SQLAlchemy MMRC to domain MMRCQuestionnaire"""
        return MMRCQuestionnaire(
            record_id=sql_mmrc.id,
            patient_id=sql_mmrc.user_id,
            record_date=sql_mmrc.record_date,
            score=sql_mmrc.score,
            answer_text=sql_mmrc.answer_text,
            created_at=sql_mmrc.created_at
        )

    @staticmethod
    def mmrc_to_sql(domain_mmrc: MMRCQuestionnaire, existing_mmrc: SQLMMRC = None) -> SQLMMRC:
        """Convert domain MMRCQuestionnaire to SQLAlchemy MMRC"""
        if existing_mmrc:
            mmrc = existing_mmrc
        else:
            mmrc = SQLMMRC()

        mmrc.user_id = domain_mmrc.patient_id
        mmrc.record_date = domain_mmrc.record_date
        mmrc.score = domain_mmrc.score
        mmrc.answer_text = domain_mmrc.answer_text

        return mmrc

    @staticmethod
    def cat_list_to_domain(sql_cats: List[SQLCAT]) -> List[CATQuestionnaire]:
        """Convert list of SQLAlchemy CATs to domain CATQuestionnaires"""
        return [QuestionnaireMapper.cat_to_domain(cat) for cat in sql_cats]

    @staticmethod
    def mmrc_list_to_domain(sql_mmrcs: List[SQLMMRC]) -> List[MMRCQuestionnaire]:
        """Convert list of SQLAlchemy MMRCs to domain MMRCQuestionnaires"""
        return [QuestionnaireMapper.mmrc_to_domain(mmrc) for mmrc in sql_mmrcs]