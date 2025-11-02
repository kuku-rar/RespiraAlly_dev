# services/web-app/app/extensions.py
"""
This module initializes Flask extensions.
To avoid circular imports, extensions are initialized here
and then imported into the application factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_socketio import SocketIO
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
swagger = Swagger()
socketio = SocketIO()
scheduler = APScheduler()
