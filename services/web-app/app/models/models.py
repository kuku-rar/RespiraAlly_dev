# services/web-app/app/models/models.py
from ..extensions import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_staff = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    last_login = db.Column(db.DateTime)
    line_user_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    health_profile = db.relationship('HealthProfile', backref='user', foreign_keys='HealthProfile.user_id', uselist=False, cascade="all, delete-orphan")
    staff_details = db.relationship('StaffDetail', backref='user', uselist=False, cascade="all, delete-orphan")
    daily_metrics = db.relationship('DailyMetric', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    mmrc_questionnaires = db.relationship('QuestionnaireMMRC', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    cat_questionnaires = db.relationship('QuestionnaireCAT', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    # Relationship for staff managing health profiles
    managed_profiles = db.relationship('HealthProfile', foreign_keys='HealthProfile.staff_id', back_populates='managing_staff', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "account": self.account,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_staff": self.is_staff,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class HealthProfile(db.Model):
    __tablename__ = 'health_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    smoke_status = db.Column(db.String(10)) # e.g., 'never', 'quit', 'current'
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    managing_staff = db.relationship('User', foreign_keys=[staff_id], back_populates='managed_profiles')

class StaffDetail(db.Model):
    __tablename__ = 'staff_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    title = db.Column(db.String(100)) # e.g., '呼吸治療師'

class DailyMetric(db.Model):
    __tablename__ = 'daily_metrics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    water_cc = db.Column(db.Integer)
    medication = db.Column(db.Boolean)
    exercise_min = db.Column(db.Integer)
    cigarettes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class QuestionnaireMMRC(db.Model):
    __tablename__ = 'questionnaire_mmrc'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.SmallInteger, nullable=False)
    answer_text = db.Column(db.Text)
    record_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class QuestionnaireCAT(db.Model):
    __tablename__ = 'questionnaire_cat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    cough_score = db.Column(db.SmallInteger, nullable=False)
    phlegm_score = db.Column(db.SmallInteger, nullable=False)
    chest_score = db.Column(db.SmallInteger, nullable=False)
    breath_score = db.Column(db.SmallInteger, nullable=False)
    limit_score = db.Column(db.SmallInteger, nullable=False)
    confidence_score = db.Column(db.SmallInteger, nullable=False)
    sleep_score = db.Column(db.SmallInteger, nullable=False)
    energy_score = db.Column(db.SmallInteger, nullable=False)
    total_score = db.Column(db.SmallInteger, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class UserAlert(db.Model):
    __tablename__ = 'user_alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship('User', backref=db.backref('alerts', lazy=True))
class Task(db.Model):
    """任務管理模型"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # 衛教/追蹤/評估/回診
    status = db.Column(db.String(50), default='pending')  # pending/in_progress/completed
    priority = db.Column(db.Integer, default=1)  # 1-5

    # 關聯 - 加入 ondelete 約束
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    # 時間
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 關係定義
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='related_tasks')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'assignee_id': self.assignee_id,
            'patient_id': self.patient_id,
            'created_by': self.created_by,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AlertNotification(db.Model):
    """AI 即時通報模型"""
    __tablename__ = 'alert_notifications'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    therapist_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    level = db.Column(db.String(20), nullable=False)  # info/warning/critical
    category = db.Column(db.String(50))  # adherence/health/system
    message = db.Column(db.Text, nullable=False)
    alert_metadata = db.Column(JSON)  # 附加資料（JSON 格式）
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 關係定義
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_alerts')
    therapist = db.relationship('User', foreign_keys=[therapist_id], backref='therapist_alerts')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'therapist_id': self.therapist_id,
            'level': self.level,
            'category': self.category,
            'message': self.message,
            'metadata': self.alert_metadata,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
