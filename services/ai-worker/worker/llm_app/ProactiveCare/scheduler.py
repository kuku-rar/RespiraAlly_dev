import os

import pytz
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from .tasks import check_and_trigger_dynamic_care, patrol_silent_users, cleanup_expired_sessions

load_dotenv()
TAIPEI_TZ = pytz.timezone("Asia/Taipei")

redis_jobstore = RedisJobStore(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=1,
)

scheduler = BackgroundScheduler(jobstores={"default": redis_jobstore}, timezone=pytz.utc)

def initialize_scheduler():
    """
    初始化並新增所有排程任務。
    此函式應在應用程式啟動時被呼叫一次。
    """
    # 檢查任務是否已存在，避免重複新增
    if not scheduler.get_job("session_cleanup_job"):
        scheduler.add_job(
            cleanup_expired_sessions,
            trigger="interval",
            minutes=5,
            id="session_cleanup_job",
            name="清理過期的使用者 Session",
            replace_existing=True,
        )
        print("✅ [Scheduler] Session 清理任務已新增。")

    if not scheduler.get_job("dynamic_care_trigger"):
        scheduler.add_job(
            check_and_trigger_dynamic_care,
            trigger="interval",
            minutes=30,
            id="dynamic_care_trigger",
            name="檢查 24 小時閒置使用者",
            replace_existing=True,
        )
        print("✅ [Scheduler] 動態關懷任務已新增。")
        
    if not scheduler.get_job("weekly_patrol_job"):
        scheduler.add_job(
            patrol_silent_users,
            trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="weekly_patrol_job",
            name="巡檢長期沉默使用者",
            replace_existing=True,
        )
        print("✅ [Scheduler] 每週巡檢任務已新增。")

    print("🚀 主動關懷與 Session 清理排程服務已準備就緒...")
    scheduler.print_jobs()

def main():
    initialize_scheduler()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("🛑 排程服務已停止。")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
