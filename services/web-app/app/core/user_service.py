# services/web-app/app/core/user_service.py
from ..models import User, StaffDetail
from .user_repository import UserRepository

def create_user(data):
    """建立新使用者 (管理員專用)"""
    repo = UserRepository()
    
    account = data.get('account')
    password = data.get('password')
    is_staff = data.get('is_staff', False)
    is_admin = data.get('is_admin', False)
    email = data.get('email')

    if not account or not password:
        return None, "Account and password are required."

    if repo.find_by_account(account):
        return None, f"User with account '{account}' already exists."

    if email and repo.find_by_email(email):
        return None, f"User with email '{email}' already exists."

    new_user = User(
        account=account,
        is_staff=is_staff,
        is_admin=is_admin,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=email
    )
    new_user.set_password(password)

    # 如果是員工，則建立職稱詳情
    if is_staff and 'title' in data:
        staff_detail = StaffDetail(
            user=new_user,
            title=data.get('title')
        )

    repo.add(new_user)
    repo.commit()

    return new_user, None

def get_user_by_id(user_id):
    repo = UserRepository()
    return repo.find_by_id(user_id)
