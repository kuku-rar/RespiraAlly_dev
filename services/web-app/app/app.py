# services/web-app/app/app.py
import os
from flask import Flask, jsonify
from .config import config
from .extensions import db, migrate, swagger, jwt, socketio, scheduler
from .api.auth import auth_bp
from .api.patients import patients_bp
from .api.questionnaires import questionnaires_bp
from .api.uploads import uploads_bp
from .api.users import users_bp
from .api.daily_metrics import daily_metrics_bp
from .api.voice import bp as voice_bp  # Import voice API blueprint
from .api.education import education_bp  # Import education API blueprint
from .api.overview import overview_bp  # Import overview API blueprint
from .api.tasks import tasks_bp  # Import tasks API blueprint
from .api.alerts import alerts_bp  # Import alerts API blueprint
from .api.line_webhook import chat_bp  # Import LINE webhook API blueprint

# 🔒 Debug端點在開發環境導入
# 如果環境變量未設置，檢查 --debug 標誌（通過檢查是否在開發模式）
try:
    from .api.debug_test import debug_bp  # Import debug test blueprint
except ImportError:
    debug_bp = None

from .core.notification_service import start_notification_listener

# 從原本示範任務，改為引入實際排程任務（保留原檔案中的示範函式，不再註冊）
from .core.scheduler_service import scheduled_task
from .scheduled_jobs import (
    run_noon_care_job,
    run_survey_reminder_job,
    run_evening_summary_job,
)


def create_app(config_name="default"):
    """
    應用程式工廠函數。
    """
    app = Flask(__name__)

    # 1. 載入設定
    app.config.from_object(config[config_name])

    # 2. 初始化擴充套件
    db.init_app(app)
    migrate.init_app(app, db)
    swagger.init_app(app)
    jwt.init_app(app)

    # 初始化排程器（允許在排程執行緒或子流程中跳過，以避免重複啟動）
    # 以環境變數 SKIP_SCHEDULER_INIT=1 控制略過
    if config_name != "testing" and os.getenv("SKIP_SCHEDULER_INIT") != "1":
        scheduler.init_app(app)
        scheduler.start()

    socketio.init_app(app, async_mode="gevent", cors_allowed_origins="*")

    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(questionnaires_bp)
    app.register_blueprint(daily_metrics_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(voice_bp)  # Register the voice API blueprint
    app.register_blueprint(education_bp)  # Register the education API blueprint
    app.register_blueprint(overview_bp)  # Register the overview API blueprint
    app.register_blueprint(tasks_bp)  # Register the tasks API blueprint
    app.register_blueprint(alerts_bp)  # Register the alerts API blueprint
    app.register_blueprint(chat_bp)  # Register the LINE webhook API blueprint

    # 🔒 Debug端點註冊（在開發環境或 debug 模式下）
    if debug_bp is not None and (os.getenv('FLASK_ENV') == 'development' or app.debug or config_name == 'default'):
        app.register_blueprint(debug_bp)  # Register debug endpoints
        print(f"🐛 Debug endpoints registered at /api/v1/debug/*")
    else:
        print(f"⚠️ Debug endpoints not registered (production mode)")


    # 5. 添加 CORS 支援 (開發環境)
    @app.after_request
    def after_request_cors(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Request-Id')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.before_request
    def handle_preflight():
        from flask import request, make_response
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Request-Id")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            return response

    # 靜態檔案路由 - 服務 React 建置檔案
    @app.route('/static/<path:filename>')
    def serve_react_static(filename):
        from flask import send_from_directory
        return send_from_directory(app.static_folder, filename)

    # 根路由 - 健康檢查端點
    @app.route("/")
    def index():
        return jsonify({
            "status": "OK",
            "service": "RespiraAlly API",
            "version": "1.0",
            "endpoints": {
                "health": "/api/v1/debug/health",
                "api_docs": "/swagger"
            }
        })

    # SPA 路由支援 - 捕獲所有非 API 路由，重導向到 React 應用程式
    @app.route('/<path:path>')
    def catch_all(path):
        # 排除 API 路由和靜態資源
        if path.startswith('api/') or path.startswith('static/') or path.startswith('swagger/'):
            from flask import abort
            abort(404)

        # 檢查是否為靜態檔案（JS, CSS, 圖片等）
        if '.' in path.split('/')[-1]:
            try:
                from flask import send_from_directory
                return send_from_directory(app.static_folder, path)
            except:
                from flask import abort
                abort(404)

        # 所有其他路由都返回 React 應用程式
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'index.html')

    # WebSocket 事件處理
    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Client disconnected")

    # Start the background notification listener
    # We do this check to prevent the listener from starting during tests
    if config_name != "testing":
        start_notification_listener(app)

        # 在應用程式上下文中新增排程任務
        with app.app_context():
            # 確保只在主程序中新增/調整任務，避免開發伺服器重載時重複新增
            # 在生產環境 (如 Gunicorn) 中，這個環境變數不存在，但 get_job() / reschedule_job() 會確保唯一性
            if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
                # 允許以環境變數覆寫時間，便於臨時測試
                def get_time(env_h: str, env_m: str, default_h: int, default_m: int):
                    try:
                        h = int(os.getenv(env_h, default_h))
                        m = int(os.getenv(env_m, default_m))
                        return h, m
                    except Exception:
                        return default_h, default_m

                # 確保任務在 app_context 中執行，避免 current_app 取值錯誤
                def make_context_job(f):
                    def _job():
                        with app.app_context():
                            return f()

                    return _job

                def add_or_reschedule(
                    job_id: str, func_path: str, hour: int, minute: int
                ):
                    job = scheduler.get_job(job_id)
                    # 以文字引用可被 SQLAlchemy JobStore 序列化
                    if job:
                        scheduler.remove_job(job_id)
                    scheduler.add_job(
                        id=job_id,
                        func=func_path,
                        trigger="cron",
                        hour=hour,
                        minute=minute,
                        replace_existing=True,
                        misfire_grace_time=60,
                        max_instances=1,
                        coalesce=True,
                    )

                # 讀取三個任務時間（預設：12:30、17:30、20:00 台北時區）
                noon_h, noon_m = get_time("NOON_CARE_HOUR", "NOON_CARE_MINUTE", 12, 30)
                survey_h, survey_m = get_time(
                    "SURVEY_REMINDER_HOUR", "SURVEY_REMINDER_MINUTE", 17, 30
                )
                evening_h, evening_m = get_time(
                    "EVENING_SUMMARY_HOUR", "EVENING_SUMMARY_MINUTE", 20, 00
                )


                # 設定或重排程
                add_or_reschedule(
                    "noon_care", "app.scheduled_jobs:run_noon_care_job", noon_h, noon_m
                )
                add_or_reschedule(
                    "survey_reminder",
                    "app.scheduled_jobs:run_survey_reminder_job",
                    survey_h,
                    survey_m,
                )
                add_or_reschedule(
                    "evening_summary",
                    "app.scheduled_jobs:run_evening_summary_job",
                    evening_h,
                    evening_m,
                )
                # 注意：原本的每分鐘示範任務不再註冊，避免與實際任務混淆

    return app, socketio
