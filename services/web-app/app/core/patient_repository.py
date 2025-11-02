# services/web-app/app/core/patient_repository.py
from ..models import User, HealthProfile
from ..extensions import db

class PatientRepository:
    def find_all_by_therapist_id(self, therapist_id, page, per_page, sort_by, order):
        """
        根據治療師 ID 查詢其管理的所有病患。
        支援分頁和排序。
        """
        # 基礎查詢：找到所有 staff_id 為指定治療師 ID 的健康檔案，並與使用者資料表關聯
        query = db.session.query(User, HealthProfile).join(
            HealthProfile, User.id == HealthProfile.user_id
        ).filter(HealthProfile.staff_id == therapist_id)

        # 排序邏輯
        if hasattr(User, sort_by):
            sort_column = getattr(User, sort_by)
            if order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # 預設按建立時間排序
        else:
            query = query.order_by(User.created_at.desc())

        # 分頁
        paginated_result = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_result

    def find_profile_by_user_id(self, user_id):
        """
        根據使用者 ID 查詢其詳細的使用者和健康檔案。
        """
        return db.session.query(User, HealthProfile).join(
            HealthProfile, User.id == HealthProfile.user_id
        ).filter(User.id == user_id).first()
