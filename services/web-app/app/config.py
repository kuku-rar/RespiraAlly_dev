# services/web-app/app/config.py
import os


class Config:
    """基礎設定"""

    SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_super_secret_jwt_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flasgger (Swagger) 設定
    SWAGGER = {
        "title": "Beloved Grandson API",
        "uiversion": 3,
        "version": "1.0.0",
        "description": "「Beloved Grandson」專案的後端 API 文件。",
        "termsOfService": "",
        "contact": {
            "name": "API Support",
            "email": "support@example.com",
        },
        "license": {
            "name": "MIT",
        },
        "securityDefinitions": {
            "bearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
            }
        },
        "specs_route": "/apidocs/",
    }

    # MinIO 設定
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() in ["true", "1", "t"]

    # LINE Bot 設定
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    # LIFF 設定：後端使用 LIFF_CHANNEL_ID（前端 liff.html 常數名為 LIFF_ID，值相同）
    LIFF_CHANNEL_ID = os.getenv("LIFF_CHANNEL_ID")

    # LINE Rich Menu 設定
    LINE_RICH_MENU_ID_GUEST = os.getenv("LINE_RICH_MENU_ID_GUEST")
    LINE_RICH_MENU_ID_MEMBER = os.getenv("LINE_RICH_MENU_ID_MEMBER")

    # APScheduler 設定
    SCHEDULER_JOBSTORES = {
        "default": {"type": "sqlalchemy", "url": os.getenv("DATABASE_URL")}
    }
    SCHEDULER_API_ENABLED = True
    # 使用 job defaults 以正確套用 misfire 與 coalesce 設定
    SCHEDULER_JOB_DEFAULTS = {
        "coalesce": True,
        "misfire_grace_time": 60,
        "max_instances": 1,
    }
    SCHEDULER_TIMEZONE = "Asia/Taipei"

    BASE_URL = os.getenv("BASE_URL")
    
    # Milvus 設定
    MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
    
    # OpenAI 設定（用於 embedding）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class DevelopmentConfig(Config):
    """開發環境設定"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = True  # 印出 SQL 語句，方便除錯


class ProductionConfig(Config):
    """生產環境設定"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class TestingConfig(Config):
    """測試環境設定"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 使用記憶體資料庫進行測試


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
