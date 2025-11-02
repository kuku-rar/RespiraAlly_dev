# services/web-app/app/core/user_repository.py
from sqlalchemy import select
from ..models import User
from ..extensions import db


class UserRepository:
    def find_by_account(self, account):
        """根據帳號尋找使用者"""
        return db.session.scalars(select(User).filter_by(account=account)).first()

    def find_by_id(self, user_id):
        """根據 ID 尋找使用者"""
        return db.session.get(User, user_id)

    def find_by_email(self, email):
        """根據 Email 尋找使用者"""
        return db.session.scalars(select(User).filter_by(email=email)).first()

    def find_by_line_user_id(self, line_user_id):
        """根據 LINE User ID 尋找使用者"""
        return db.session.scalars(
            select(User).filter_by(line_user_id=line_user_id)
        ).first()

    def add(self, user):
        """新增使用者到 session"""
        db.session.add(user)

    def commit(self):
        """提交 session 變更"""
        db.session.commit()

    # ===== 新增：回傳所有病患（非工作人員） =====
    def list_patients(self):
        """
        回傳所有病患（非工作人員）
        """
        return db.session.scalars(select(User).filter_by(is_staff=False)).all()
