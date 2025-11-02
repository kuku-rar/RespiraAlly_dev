# services/web-app/seed_data.py
import random
import string
import uuid
from datetime import date, timedelta
from faker import Faker
from tqdm import tqdm

from app.app import create_app
from app.extensions import db
from app.models.models import User, StaffDetail, HealthProfile, DailyMetric, QuestionnaireCAT, QuestionnaireMMRC

# --- 配置 ---
NUM_THERAPISTS = 5
NUM_PATIENTS = 50
DATA_MONTHS = 12 # 生成過去幾個月的資料

# --- 初始化 ---
fake = Faker('zh_TW')
app, socketio = create_app()

# --- 輔助函式 ---
def generate_random_password(length=12):
    """生成英數字混合的隨機密碼"""
    characters = string.ascii_letters + string.digits  # 包含大小寫字母和數字
    return ''.join(random.choice(characters) for _ in range(length))

def get_mmrc_answer(score):
    """根據 MMRC 分數回傳對應的文字描述"""
    answers = {
        0: "只有在激烈運動時，才會感到呼吸困難",
        1: "在平路快走或爬緩坡時，會感到呼吸短促",
        2: "在平路走路時，因為呼吸困難，走得比同齡者慢，或需要停下來休息",
        3: "走平路約一百公尺或走幾分鐘後，會因呼吸困難而需要停下來休息",
        4: "因為嚴重呼吸困難而無法外出，或在穿脫衣物時感到呼吸困難"
    }
    return answers.get(score, "")

def clear_data():
    """清除所有相關表格的資料"""
    print("開始清除舊資料...")
    with app.app_context():
        # 依次刪除有外鍵關聯的資料
        db.session.query(QuestionnaireCAT).delete()
        db.session.query(QuestionnaireMMRC).delete()
        db.session.query(DailyMetric).delete()
        db.session.query(HealthProfile).delete()
        db.session.query(StaffDetail).delete()
        db.session.query(User).delete()
        db.session.commit()
    print("舊資料清除完畢。")

def create_admin_and_therapists(num_therapists):
    """建立管理員和治療師"""
    print(f"建立 1 位管理員及 {num_therapists} 位治療師...")
    users_to_create = []

    # 1. 建立管理員
    admin_user = User(
        account='admin',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_admin=True
    )
    admin_user.set_password('admin')
    users_to_create.append(admin_user)

    # 2. 建立治療師
    for i in range(num_therapists):
        first_name = fake.first_name()
        last_name = fake.last_name()
        therapist = User(
            account=f'therapist_{i+1:02d}',
            first_name=first_name,
            last_name=last_name,
            email=fake.email(),
            is_staff=True,
            is_admin=False
        )
        therapist.set_password('password')
        therapist.staff_details = StaffDetail(title='呼吸治療師')
        users_to_create.append(therapist)

    db.session.bulk_save_objects(users_to_create)
    db.session.commit()
    return User.query.filter_by(is_staff=True, is_admin=False).all()

def create_patients(num_patients, therapists):
    """建立病患並隨機指派治療師"""
    print(f"建立 {num_patients} 位病患...")
    patients_to_create = []
    for i in tqdm(range(num_patients), desc="建立病患"):
        first_name = fake.first_name()
        last_name = fake.last_name()
        patient = User(
            account=f'patient_{i+1:03d}',
            line_user_id=f'U{uuid.uuid4().hex}',
            first_name=first_name,
            last_name=last_name,
            gender=random.choice(['male', 'female', 'other']),
            email=fake.email(),
            phone=fake.phone_number()
        )
        # 病患使用隨機生成的英數字混合12位密碼
        patient.set_password(generate_random_password())

        assigned_therapist = random.choice(therapists)
        patient.health_profile = HealthProfile(
            height_cm=random.randint(150, 190),
            weight_kg=random.randint(50, 100),
            smoke_status=random.choice(['never', 'quit', 'current']),
            staff_id=assigned_therapist.id
        )
        patients_to_create.append(patient)

    db.session.add_all(patients_to_create)
    db.session.commit()
    return User.query.filter_by(is_staff=False, is_admin=False).all()

def generate_historical_data(patients, months):
    """為病患生成過去數個月的健康日誌和問卷"""
    print(f"為 {len(patients)} 位病患生成過去 {months} 個月的歷史資料...")

    today = date.today()
    metrics_to_create = []
    cat_records_to_create = []
    mmrc_records_to_create = []

    for patient in tqdm(patients, desc="生成歷史資料"):
        db.session.refresh(patient) # 強制重新載入關聯資料
        # 1. 生成每日健康日誌
        for day_delta in range(months * 30):
            log_date = today - timedelta(days=day_delta)
            metric = DailyMetric(
                user_id=patient.id,
                water_cc=random.randint(1500, 3000),
                medication=random.choice([True, False]),
                exercise_min=random.randint(0, 60),
                cigarettes=random.randint(0, 20) if patient.health_profile.smoke_status == 'current' else 0,
                created_at=log_date
            )
            metrics_to_create.append(metric)

        # 2. 生成每月問卷
        for month_delta in range(months):
            # 確保月份和年份正確回推
            year = today.year
            month = today.month - month_delta
            while month <= 0:
                month += 12
                year -= 1

            record_date = date(year, month, random.randint(1, 28))

            # CAT
            scores = {f: random.randint(0, 5) for f in ['cough', 'phlegm', 'chest', 'breath', 'limit', 'confidence', 'sleep', 'energy']}
            total_score = sum(scores.values())
            cat_record = QuestionnaireCAT(
                user_id=patient.id, record_date=record_date, total_score=total_score,
                cough_score=scores['cough'], phlegm_score=scores['phlegm'], chest_score=scores['chest'],
                breath_score=scores['breath'], limit_score=scores['limit'], confidence_score=scores['confidence'],
                sleep_score=scores['sleep'], energy_score=scores['energy']
            )
            cat_records_to_create.append(cat_record)

            # MMRC
            mmrc_score = random.randint(0, 4)
            mmrc_record = QuestionnaireMMRC(
                user_id=patient.id,
                record_date=record_date,
                score=mmrc_score,
                answer_text=get_mmrc_answer(mmrc_score)
            )
            mmrc_records_to_create.append(mmrc_record)

    print("開始批量儲存歷史資料...")
    db.session.bulk_save_objects(metrics_to_create)
    db.session.bulk_save_objects(cat_records_to_create)
    db.session.bulk_save_objects(mmrc_records_to_create)
    db.session.commit()
    print("歷史資料儲存完畢。")


def seed_data():
    """主函式，執行所有資料生成步驟"""
    with app.app_context():
        clear_data()
        therapists = create_admin_and_therapists(NUM_THERAPISTS)
        patients = create_patients(NUM_PATIENTS, therapists)
        generate_historical_data(patients, DATA_MONTHS)
    print("="*20)
    print("測試資料集建立完成！")
    print(f"總共建立了 {len(therapists)} 位治療師, {len(patients)} 位病患。")
    print(f"每位病患包含過去 {DATA_MONTHS} 個月的日誌與問卷。")
    print("="*20)

if __name__ == '__main__':
    seed_data()
