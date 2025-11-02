"""
定期任務模組 - 負責刷新物化視圖和其他排程任務
"""
from datetime import datetime
from sqlalchemy import text
from .extensions import db
import logging

logger = logging.getLogger(__name__)


class ScheduledJobs:
    """排程任務管理類"""
    
    @staticmethod
    def refresh_materialized_views():
        """
        刷新所有物化視圖
        建議每 30 分鐘執行一次
        """
        try:
            with db.engine.connect() as conn:
                # 使用 CONCURRENTLY 選項避免鎖表
                conn.execute(text("""
                    REFRESH MATERIALIZED VIEW CONCURRENTLY v_patient_risk_assessment
                """))
                conn.execute(text("""
                    REFRESH MATERIALIZED VIEW CONCURRENTLY v_system_kpis
                """))
                conn.commit()
                
            logger.info(f"物化視圖刷新成功 - {datetime.now()}")
            return True
            
        except Exception as e:
            logger.error(f"物化視圖刷新失敗: {str(e)}")
            return False
    
    @staticmethod
    def analyze_tables():
        """
        分析資料表統計資訊，優化查詢計劃
        建議每天執行一次
        """
        try:
            with db.engine.connect() as conn:
                # 分析主要資料表
                tables = [
                    'users', 'tasks', 'alert_notifications',
                    'daily_metrics', 'questionnaire_cat', 'questionnaire_mmrc'
                ]
                
                for table in tables:
                    conn.execute(text(f"ANALYZE {table}"))
                conn.commit()
                
            logger.info(f"資料表分析完成 - {datetime.now()}")
            return True
            
        except Exception as e:
            logger.error(f"資料表分析失敗: {str(e)}")
            return False
    
    @staticmethod
    def cleanup_old_alerts(days=90):
        """
        清理舊的通報記錄
        
        Args:
            days: 保留天數，預設 90 天
        """
        try:
            from .models import AlertNotification
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 刪除已讀且超過保留期限的通報
            deleted_count = AlertNotification.query.filter(
                AlertNotification.is_read == True,
                AlertNotification.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"清理了 {deleted_count} 筆舊通報記錄")
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理通報失敗: {str(e)}")
            return 0


def run_noon_care_job():
    logger.info("[noon_care] 任務開始")
    try:
        # 這裡可加入實際中午關懷任務邏輯
        return True
    except Exception as e:
        logger.error(f"[noon_care] 任務失敗: {e}")
        return False


def run_survey_reminder_job():
    logger.info("[survey_reminder] 任務開始")
    try:
        # 這裡可加入問卷提醒任務邏輯（推播/通知）
        return True
    except Exception as e:
        logger.error(f"[survey_reminder] 任務失敗: {e}")
        return False


def run_evening_summary_job():
    logger.info("[evening_summary] 任務開始")
    try:
        # 晚間可同時刷新物化視圖，或彙總報表
        ScheduledJobs.refresh_materialized_views()
        return True
    except Exception as e:
        logger.error(f"[evening_summary] 任務失敗: {e}")
        return False


def init_scheduler(app):
    """
    初始化排程器
    
    Args:
        app: Flask 應用實例
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler()
    jobs = ScheduledJobs()
    
    # 每 30 分鐘刷新物化視圖
    scheduler.add_job(
        func=jobs.refresh_materialized_views,
        trigger=IntervalTrigger(minutes=30),
        id='refresh_views',
        name='刷新物化視圖',
        replace_existing=True
    )
    
    # 每天凌晨 2 點分析資料表
    scheduler.add_job(
        func=jobs.analyze_tables,
        trigger=CronTrigger(hour=2, minute=0),
        id='analyze_tables',
        name='分析資料表統計',
        replace_existing=True
    )
    
    # 每週日凌晨 3 點清理舊通報
    scheduler.add_job(
        func=lambda: jobs.cleanup_old_alerts(days=90),
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='cleanup_alerts',
        name='清理舊通報',
        replace_existing=True
    )
    
    scheduler.start()
    
    # 關閉應用時停止排程器
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("排程器初始化完成")
    return scheduler