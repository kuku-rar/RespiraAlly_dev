# services/web-app/app/core/overview_service.py
"""
總覽服務，提供 Dashboard 的統計數據和趨勢分析
"""
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from sqlalchemy import func, and_, or_
from ..models import User, HealthProfile, DailyMetric, QuestionnaireCAT, QuestionnaireMMRC
from ..extensions import db
import logging

logger = logging.getLogger(__name__)


class OverviewService:
    """
    處理總覽頁面相關的業務邏輯
    包括 KPI、趨勢、依從性分析等
    """
    
    def __init__(self):
        self.logger = logger
    
    def get_kpis(self, therapist_id: int) -> Dict[str, Any]:
        """
        取得治療師的關鍵績效指標
        
        Args:
            therapist_id: 治療師 ID
            
        Returns:
            KPI 數據字典
        """
        try:
            # 總病患數
            total_patients = db.session.query(func.count(HealthProfile.id))\
                .filter(HealthProfile.staff_id == therapist_id).scalar() or 0
            
            # 高風險病患數（CAT > 20 或 mMRC >= 2）
            high_risk_query = db.session.query(func.count(func.distinct(User.id)))\
                .join(HealthProfile, User.id == HealthProfile.user_id)\
                .filter(HealthProfile.staff_id == therapist_id)
            
            # 最新 CAT 分數 > 20 的病患
            latest_cat_subquery = db.session.query(
                QuestionnaireCAT.user_id,
                func.max(QuestionnaireCAT.created_at).label('latest')
            ).group_by(QuestionnaireCAT.user_id).subquery()
            
            high_risk_cat = db.session.query(func.count(func.distinct(QuestionnaireCAT.user_id)))\
                .join(
                    latest_cat_subquery,
                    and_(
                        QuestionnaireCAT.user_id == latest_cat_subquery.c.user_id,
                        QuestionnaireCAT.created_at == latest_cat_subquery.c.latest
                    )
                )\
                .join(HealthProfile, QuestionnaireCAT.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    QuestionnaireCAT.total_score > 20
                ).scalar() or 0
            
            # 最新 mMRC >= 2 的病患
            latest_mmrc_subquery = db.session.query(
                QuestionnaireMMRC.user_id,
                func.max(QuestionnaireMMRC.created_at).label('latest')
            ).group_by(QuestionnaireMMRC.user_id).subquery()
            
            high_risk_mmrc = db.session.query(func.count(func.distinct(QuestionnaireMMRC.user_id)))\
                .join(
                    latest_mmrc_subquery,
                    and_(
                        QuestionnaireMMRC.user_id == latest_mmrc_subquery.c.user_id,
                        QuestionnaireMMRC.created_at == latest_mmrc_subquery.c.latest
                    )
                )\
                .join(HealthProfile, QuestionnaireMMRC.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    QuestionnaireMMRC.score >= 2
                ).scalar() or 0
            
            high_risk_patients = max(high_risk_cat, high_risk_mmrc)
            
            # 平均依從率（過去 7 天）
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            adherence_data = db.session.query(
                func.avg(DailyMetric.medication.cast(db.Integer).cast(db.Float)).label('med_adherence')
            ).join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                DailyMetric.created_at >= seven_days_ago
            ).first()
            
            avg_adherence = 0
            if adherence_data and adherence_data.med_adherence:
                avg_adherence = round(float(adherence_data.med_adherence) * 100, 1)
            
            # 今日活躍用戶數
            today = date.today()
            active_today = db.session.query(func.count(func.distinct(DailyMetric.user_id)))\
                .join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    func.date(DailyMetric.created_at) == today
                ).scalar() or 0
            
            # 低依從性病患數（< 60%）
            low_adherence_subquery = db.session.query(
                DailyMetric.user_id,
                func.avg(DailyMetric.medication.cast(db.Integer).cast(db.Float)).label('avg_med')
            ).join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                DailyMetric.created_at >= seven_days_ago
            )\
            .group_by(DailyMetric.user_id)\
            .having(func.avg(DailyMetric.medication.cast(db.Integer).cast(db.Float)) < 0.6)\
            .subquery()
            
            low_adherence_patients = db.session.query(func.count(low_adherence_subquery.c.user_id)).scalar() or 0
            
            return {
                "total_patients": total_patients,
                "high_risk_patients": high_risk_patients,
                "average_adherence": avg_adherence,
                "active_today": active_today,
                "low_adherence_patients": low_adherence_patients,
                "improvement_rate": self._calculate_improvement_rate(therapist_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting KPIs: {e}")
            raise
    
    def get_trends(self, therapist_id: int, days: int = 30) -> Dict[str, Any]:
        """
        取得趨勢數據
        
        Args:
            therapist_id: 治療師 ID
            days: 天數範圍
            
        Returns:
            趨勢數據
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # CAT 分數趨勢
            cat_trends = db.session.query(
                func.date(QuestionnaireCAT.created_at).label('date'),
                func.avg(QuestionnaireCAT.total_score).label('avg_score'),
                func.count(QuestionnaireCAT.id).label('count')
            ).join(HealthProfile, QuestionnaireCAT.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                QuestionnaireCAT.created_at >= start_date
            )\
            .group_by(func.date(QuestionnaireCAT.created_at))\
            .order_by(func.date(QuestionnaireCAT.created_at)).all()
            
            # mMRC 分數趨勢
            mmrc_trends = db.session.query(
                func.date(QuestionnaireMMRC.created_at).label('date'),
                func.avg(QuestionnaireMMRC.score).label('avg_score'),
                func.count(QuestionnaireMMRC.id).label('count')
            ).join(HealthProfile, QuestionnaireMMRC.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                QuestionnaireMMRC.created_at >= start_date
            )\
            .group_by(func.date(QuestionnaireMMRC.created_at))\
            .order_by(func.date(QuestionnaireMMRC.created_at)).all()
            
            # 每日健康指標趨勢
            daily_trends = db.session.query(
                func.date(DailyMetric.created_at).label('date'),
                func.avg(DailyMetric.water_cc).label('avg_water'),
                func.avg(DailyMetric.exercise_min).label('avg_exercise'),
                func.avg(DailyMetric.medication.cast(db.Integer).cast(db.Float)).label('avg_medication'),
                func.count(func.distinct(DailyMetric.user_id)).label('active_users')
            ).join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                DailyMetric.created_at >= start_date
            )\
            .group_by(func.date(DailyMetric.created_at))\
            .order_by(func.date(DailyMetric.created_at)).all()
            
            return {
                "cat_trends": [
                    {
                        "date": str(t.date),
                        "avg_score": round(float(t.avg_score), 1) if t.avg_score else 0,
                        "count": t.count
                    } for t in cat_trends
                ],
                "mmrc_trends": [
                    {
                        "date": str(t.date),
                        "avg_score": round(float(t.avg_score), 1) if t.avg_score else 0,
                        "count": t.count
                    } for t in mmrc_trends
                ],
                "daily_trends": [
                    {
                        "date": str(t.date),
                        "avg_water": round(float(t.avg_water), 0) if t.avg_water else 0,
                        "avg_exercise": round(float(t.avg_exercise), 0) if t.avg_exercise else 0,
                        "avg_medication": round(float(t.avg_medication) * 100, 1) if t.avg_medication else 0,
                        "active_users": t.active_users
                    } for t in daily_trends
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting trends: {e}")
            raise
    
    def get_adherence_analysis(self, therapist_id: int) -> Dict[str, Any]:
        """
        取得依從性分析
        
        Args:
            therapist_id: 治療師 ID
            
        Returns:
            依從性分析數據
        """
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            # 依從性分布
            adherence_data = db.session.query(
                DailyMetric.user_id,
                func.avg(DailyMetric.medication.cast(db.Integer).cast(db.Float)).label('adherence_rate')
            ).join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                DailyMetric.created_at >= seven_days_ago
            )\
            .group_by(DailyMetric.user_id).all()
            
            # 分類統計
            excellent = 0  # >= 90%
            good = 0       # 70-89%
            fair = 0       # 50-69%
            poor = 0       # < 50%
            
            patient_adherence = []
            for data in adherence_data:
                rate = float(data.adherence_rate) * 100 if data.adherence_rate else 0
                
                if rate >= 90:
                    excellent += 1
                elif rate >= 70:
                    good += 1
                elif rate >= 50:
                    fair += 1
                else:
                    poor += 1
                
                # 取得病患資訊
                user = User.query.get(data.user_id)
                if user:
                    patient_adherence.append({
                        "patient_id": user.id,
                        "patient_name": f"{user.first_name} {user.last_name}".strip(),
                        "adherence_rate": round(rate, 1)
                    })
            
            # 排序：依從性由低到高
            patient_adherence.sort(key=lambda x: x['adherence_rate'])
            
            return {
                "distribution": {
                    "excellent": excellent,
                    "good": good,
                    "fair": fair,
                    "poor": poor
                },
                "low_adherence_patients": patient_adherence[:10],  # 最低的 10 個
                "total_patients": len(adherence_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting adherence analysis: {e}")
            raise
    
    def get_usage_statistics(self, therapist_id: int) -> Dict[str, Any]:
        """
        取得應用使用統計
        
        Args:
            therapist_id: 治療師 ID
            
        Returns:
            使用統計數據
        """
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # 功能使用統計（過去 7 天）
            cat_usage = db.session.query(func.count(QuestionnaireCAT.id))\
                .join(HealthProfile, QuestionnaireCAT.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    QuestionnaireCAT.created_at >= seven_days_ago
                ).scalar() or 0
            
            mmrc_usage = db.session.query(func.count(QuestionnaireMMRC.id))\
                .join(HealthProfile, QuestionnaireMMRC.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    QuestionnaireMMRC.created_at >= seven_days_ago
                ).scalar() or 0
            
            daily_metric_usage = db.session.query(func.count(DailyMetric.id))\
                .join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
                .filter(
                    HealthProfile.staff_id == therapist_id,
                    DailyMetric.created_at >= seven_days_ago
                ).scalar() or 0
            
            # 每日活躍用戶趨勢（過去 30 天）
            daily_active_users = db.session.query(
                func.date(DailyMetric.created_at).label('date'),
                func.count(func.distinct(DailyMetric.user_id)).label('active_users')
            ).join(HealthProfile, DailyMetric.user_id == HealthProfile.user_id)\
            .filter(
                HealthProfile.staff_id == therapist_id,
                DailyMetric.created_at >= thirty_days_ago
            )\
            .group_by(func.date(DailyMetric.created_at))\
            .order_by(func.date(DailyMetric.created_at)).all()
            
            # 功能完成率
            total_patients = db.session.query(func.count(HealthProfile.id))\
                .filter(HealthProfile.staff_id == therapist_id).scalar() or 1
            
            cat_completion_rate = (cat_usage / (total_patients * 7)) * 100 if total_patients > 0 else 0
            mmrc_completion_rate = (mmrc_usage / (total_patients * 7)) * 100 if total_patients > 0 else 0
            daily_completion_rate = (daily_metric_usage / (total_patients * 7)) * 100 if total_patients > 0 else 0
            
            return {
                "feature_usage": {
                    "cat_questionnaire": cat_usage,
                    "mmrc_questionnaire": mmrc_usage,
                    "daily_metrics": daily_metric_usage
                },
                "completion_rates": {
                    "cat": round(min(cat_completion_rate, 100), 1),
                    "mmrc": round(min(mmrc_completion_rate, 100), 1),
                    "daily": round(min(daily_completion_rate, 100), 1)
                },
                "daily_active_users": [
                    {
                        "date": str(d.date),
                        "active_users": d.active_users
                    } for d in daily_active_users
                ],
                "total_patients": total_patients
            }
            
        except Exception as e:
            self.logger.error(f"Error getting usage statistics: {e}")
            raise
    
    def _calculate_improvement_rate(self, therapist_id: int) -> float:
        """
        計算病患改善率
        比較最近兩次 CAT 評估的改善情況
        
        Args:
            therapist_id: 治療師 ID
            
        Returns:
            改善率百分比
        """
        try:
            # 取得每個病患的最近兩次 CAT 評估
            patients = db.session.query(HealthProfile.user_id)\
                .filter(HealthProfile.staff_id == therapist_id).all()
            
            improved_count = 0
            total_with_two_assessments = 0
            
            for patient in patients:
                recent_cats = db.session.query(QuestionnaireCAT)\
                    .filter(QuestionnaireCAT.user_id == patient.user_id)\
                    .order_by(QuestionnaireCAT.created_at.desc())\
                    .limit(2).all()
                
                if len(recent_cats) >= 2:
                    total_with_two_assessments += 1
                    # 如果最新的分數比之前的低，表示改善
                    if recent_cats[0].total_score < recent_cats[1].total_score:
                        improved_count += 1
            
            if total_with_two_assessments > 0:
                return round((improved_count / total_with_two_assessments) * 100, 1)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement rate: {e}")
            return 0.0


# 單例模式
_overview_service = None

def get_overview_service() -> OverviewService:
    """取得 OverviewService 單例"""
    global _overview_service
    if _overview_service is None:
        _overview_service = OverviewService()
    return _overview_service
