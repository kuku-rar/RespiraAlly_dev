# services/web-app/app/core/auth_service.py
from ..models import User, HealthProfile
from .user_repository import UserRepository
import uuid

def login_user(account, password):
    """
    驗證使用者登入。
    :param account: 使用者帳號
    :param password: 使用者密碼
    :return: User 物件或 None
    """
    repo = UserRepository()
    user = repo.find_by_account(account)
    if user and user.check_password(password):
        return user
    return None

def login_line_user(line_user_id):
    """
    處理 LINE 使用者登入。
    :param line_user_id: 從 LINE 平台獲取的 User ID
    :return: User 物件或 None
    """
    if not line_user_id:
        return None
    repo = UserRepository()
    return repo.find_by_line_user_id(line_user_id)

def register_line_user(data):
    """
    註冊新的 LINE 使用者，並建立健康檔案。
    :param data: 包含註冊資訊的字典
    :return: (User, None) 或 (None, "錯誤訊息")
    """
    line_user_id = data.get('lineUserId')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not line_user_id or not first_name or not last_name:
        return None, "lineUserId, first_name, and last_name are required."

    repo = UserRepository()
    if repo.find_by_line_user_id(line_user_id):
        return None, "This LINE account is already registered."

    new_account = f"line_user_{uuid.uuid4().hex[:12]}"
    
    new_user = User(
        account=new_account,
        line_user_id=line_user_id,
        first_name=first_name,
        last_name=last_name,
        gender=data.get('gender'),
        phone=data.get('phone'),
        is_staff=False,
        is_admin=False
    )
    new_user.set_password(str(uuid.uuid4()))

    # 同時建立健康檔案
    health_profile = HealthProfile(
        user=new_user, # 直接關聯 User 物件
        height_cm=data.get('height_cm'),
        weight_kg=data.get('weight_kg'),
        smoke_status=data.get('smoke_status')
    )

    repo.add(new_user)
    # health_profile 會因為 cascade 自動加入 session
    repo.commit()

    return new_user, None

