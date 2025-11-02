# services/web-app/app/core/scheduler_service.py
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scheduled_task():
    """
    這是一個範例排程任務，每分鐘會被執行一次。
    在實際應用中，這裡可以放置需要定期執行的程式碼，
    例如：清理過期資料、傳送每日報告、同步外部資料等。
    """
    print("-------------------------------------------------")
    logger.info("排程任務執行中... 這條訊息每一分鐘會出現一次。")


# ====== 以下為實際排程任務（保留上方範例不移除） ======
from datetime import date
from flask import current_app
from .user_repository import UserRepository
from .daily_metric_repository import DailyMetricRepository
from .line_service import get_line_service


# ---- 共用輔助 ----
def _title_by_gender(gender: str) -> str:
    return "阿公" if (gender or "").lower() == "male" else "阿嬤"


def _display_name(user) -> str:
    # 盡量組合姓名，缺少時以「您」代替
    name = f"{(user.last_name or '')}{(user.first_name or '')}".strip()
    return name if name else "您"


def _liff_link(page: str = "daily_log") -> str:
    # 新專案後端統一使用 LIFF_CHANNEL_ID（前端常數為 LIFF_ID，本質為同一值）
    liff_id = current_app.config.get("LIFF_CHANNEL_ID") or ""
    return f"https://liff.line.me/{liff_id}?page={page}" if liff_id else ""


def _get_patients():
    return UserRepository().list_patients()


def _get_today_metric(user_id: int):
    repo = DailyMetricRepository()
    return repo.find_by_user_id_and_date(user_id, date.today())


def _is_metric_partial_or_missing(metric) -> bool:
    if not metric:
        return True
    fields = ["water_cc", "medication", "exercise_min", "cigarettes"]
    return any(getattr(metric, f) is None for f in fields)


def _make_evening_message(user, metric) -> str:
    title = _title_by_gender(getattr(user, "gender", None))
    name = _display_name(user)

    # 未填寫
    if not metric:
        link = _liff_link("daily_log")
        return (
            f"{title} {name}，晚安！\n\n"
            "今天的健康日誌您還沒有填寫喔！\n"
            f"如果還有時間，請幫忙填寫一下：\n{link}\n\n"
            "不過現在也晚了，如果太累的話，明天記得要填喔！\n\n"
            "祝您有個好夢！🌸"
        )

    # 已填寫，給建議
    tips = []
    try:
        if metric.water_cc is not None and metric.water_cc < 1200:
            tips.append("💧 今天喝水有點少，目標每天至少 1500cc。")
    except Exception:
        pass

    try:
        if metric.medication is not None and metric.medication is False:
            tips.append("💊 請按時服藥，維持穩定效果。")
    except Exception:
        pass

    try:
        if metric.exercise_min is not None and metric.exercise_min < 15:
            tips.append("🚶‍♂️ 可以嘗試多活動一下，目標 15-30 分鐘輕度運動。")
    except Exception:
        pass

    try:
        if metric.cigarettes is not None and metric.cigarettes > 0:
            tips.append("🚭 為健康著想，建議逐步減少吸菸。")
    except Exception:
        pass

    tips_text = "\n".join(tips) if tips else "您今天的健康狀況很不錯！"
    return (
        f"{title} {name}，晚安！\n\n"
        "感謝您今天完成了健康日誌！\n\n"
        f"{tips_text}\n\n"
        "請記得：\n"
        "🌙 早點休息，充足的睡眠對身體很重要\n"
        "💧 睡前可以喝一點溫開水\n\n"
        "祝您有個好夢！明天見！🌸"
    )


# ---- 排程任務（12:30、17:30、20:00） ----
def send_noon_care():
    """
    12:30 午間關懷提醒
    """
    line = get_line_service()
    count = 0
    for u in _get_patients():
        title = _title_by_gender(getattr(u, "gender", None))
        name = _display_name(u)
        msg = (
            f"{title} {name}，午安！\n\n"
            "希望您今天過得愉快！記得要：\n"
            "✅ 適時補充水分\n"
            "✅ 按時服藥\n"
            "✅ 適度活動身體\n"
            "✅ 保持愉快心情\n\n"
            "下午時間我們會再提醒您填寫今日健康日誌。"
        )
        try:
            line.push_text_message(u.id, msg)
            count += 1
        except Exception as e:
            logger.error(f"午間關懷推播失敗 user_id={u.id}: {e}")
    logger.info(f"午間關懷提醒已發送給 {count} 位用戶")


def send_survey_reminder():
    """
    17:30 問卷填寫提醒（以 daily_metrics 判斷是否未完成/部分）
    """
    line = get_line_service()
    link = _liff_link("daily_log")
    count = 0
    for u in _get_patients():
        metric = _get_today_metric(u.id)
        if _is_metric_partial_or_missing(metric):
            title = _title_by_gender(getattr(u, "gender", None))
            name = _display_name(u)
            msg = (
                f"{title} {name}，傍晚好！\n\n"
                "現在是填寫健康日誌的時間了，請花一點時間告訴我們您今天的狀況。\n\n"
                f"📋 連結：{link}\n\n"
                "謝謝您的配合！🌸"
            )
            try:
                line.push_text_message(u.id, msg)
                count += 1
            except Exception as e:
                logger.error(f"問卷提醒推播失敗 user_id={u.id}: {e}")
    logger.info(f"問卷填寫提醒已發送給 {count} 位用戶")


def send_evening_summary():
    """
    20:00 晚間總結與提醒（依當日紀錄產生個人化訊息）
    """
    line = get_line_service()
    count = 0
    for u in _get_patients():
        metric = _get_today_metric(u.id)
        msg = _make_evening_message(u, metric)
        try:
            line.push_text_message(u.id, msg)
            count += 1
        except Exception as e:
            logger.error(f"晚間總結推播失敗 user_id={u.id}: {e}")
    logger.info(f"晚間總結與提醒已發送給 {count} 位用戶")
