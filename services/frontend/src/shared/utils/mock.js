// Mock 資料生成器
import dayjs from 'dayjs'

// 生成隨機數字
const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min

// 生成隨機布林值
const randomBool = (probability = 0.5) => Math.random() < probability

// Mock 病患資料
export const mockPatients = Array.from({ length: 20 }, (_, i) => ({
  id: `p${i + 1}`,
  name: ['王小明', '李大華', '張美玲', '陳志強', '林淑芬', '黃建國', '劉秀英', '楊志偉', '許雅婷', '吳明德'][i % 10],
  age: random(55, 85),
  gender: i % 2 === 0 ? 'M' : 'F',
  phone: `09${random(10000000, 99999999)}`,
  cat_score: random(0, 40),
  mmrc_score: random(0, 4),
  risk_level: ['high', 'medium', 'low'][random(0, 2)],
  adherence_rate: random(40, 100) / 100,
  last_visit: dayjs().subtract(random(1, 30), 'day').format('YYYY-MM-DD'),
  created_at: dayjs().subtract(random(30, 365), 'day').format('YYYY-MM-DD'),
}))

// Mock 總覽 KPI
export const mockKpis = {
  patients_total: 123,
  high_risk_pct: 0.27,
  low_adherence_pct: 0.31,
  cat_avg: 13.2,
  mmrc_avg: 1.4,
}

// Mock 趨勢資料
export const mockTrends = Array.from({ length: 6 }, (_, i) => ({
  date: dayjs().subtract(5 - i, 'month').format('YYYY-MM-01'),
  cat_avg: 12 + random(-2, 3) + i * 0.2,
  mmrc_avg: 1.3 + random(-3, 3) * 0.1,
}))

// Mock 依從性資料
export const mockAdherence = Array.from({ length: 8 }, (_, i) => ({
  date: dayjs().subtract(7 - i, 'week').format('YYYY-[W]ww'),
  med_rate: (75 + random(-10, 15)) / 100,
  water_rate: (70 + random(-15, 20)) / 100,
  exercise_rate: (65 + random(-20, 25)) / 100,
  smoke_tracking_rate: (85 + random(-5, 10)) / 100,
}))

// Mock 每日健康指標
export const mockDailyMetrics = (patientId, days = 30) => 
  Array.from({ length: days }, (_, i) => ({
    id: `dm_${patientId}_${i}`,
    patient_id: patientId,
    date: dayjs().subtract(days - 1 - i, 'day').format('YYYY-MM-DD'),
    water_cc: random(800, 2500),
    medication_taken: randomBool(0.8),
    exercise_minutes: random(0, 60),
    cigarettes: random(0, 10),
    weight_kg: 65 + random(-5, 5),
    systolic_bp: random(110, 140),
    diastolic_bp: random(70, 90),
    heart_rate: random(60, 90),
    spo2: random(92, 99),
    notes: randomBool(0.2) ? '今天感覺呼吸較順暢' : null,
  }))

// Mock CAT 歷史
export const mockCatHistory = (patientId, count = 12) =>
  Array.from({ length: count }, (_, i) => ({
    id: `cat_${patientId}_${i}`,
    patient_id: patientId,
    date: dayjs().subtract(count - 1 - i, 'month').format('YYYY-MM-DD'),
    score: random(8, 25),
    cough: random(0, 5),
    phlegm: random(0, 5),
    chest: random(0, 5),
    breathlessness: random(0, 5),
    activities: random(0, 5),
    confidence: random(0, 5),
    sleep: random(0, 5),
    energy: random(0, 5),
  }))

// Mock mMRC 歷史
export const mockMmrcHistory = (patientId, count = 12) =>
  Array.from({ length: count }, (_, i) => ({
    id: `mmrc_${patientId}_${i}`,
    patient_id: patientId,
    date: dayjs().subtract(count - 1 - i, 'month').format('YYYY-MM-DD'),
    score: random(0, 4),
    description: [
      '只有在費力運動時才會感到呼吸困難',
      '在平地快走或走小斜坡時會感到呼吸困難',
      '由於呼吸困難，平地行走時比同年齡的人慢或需要停下來休息',
      '在平地行走100公尺或幾分鐘後需要停下來喘氣',
      '因呼吸困難無法離開家門，或在穿脫衣服時會感到呼吸困難',
    ][random(0, 4)],
  }))

// Mock 個案詳細資料
export const mockPatientProfile = (id) => ({
  id,
  user_id: `u_${id}`,
  name: '王小明',
  gender: 'M',
  birth_date: '1955-03-15',
  phone: '0912345678',
  email: 'patient@example.com',
  address: '台北市大安區信義路四段1號',
  emergency_contact: '王大明',
  emergency_phone: '0923456789',
  medical_record_number: 'MRN123456',
  diagnosis: 'COPD GOLD stage II',
  diagnosis_date: '2020-05-20',
  medications: [
    { name: 'Spiriva', dosage: '18mcg', frequency: '每日一次' },
    { name: 'Symbicort', dosage: '160/4.5mcg', frequency: '每日兩次' },
  ],
  allergies: ['Penicillin'],
  comorbidities: ['高血壓', '糖尿病'],
  smoking_history: '已戒菸，曾抽菸30年',
  staff_id: 'staff_001',
  created_at: '2020-05-20T10:00:00Z',
  updated_at: '2024-01-15T14:30:00Z',
})

// Mock 任務資料
export const mockTasks = Array.from({ length: 30 }, (_, i) => ({
  id: `task_${i + 1}`,
  title: [
    '衛教：正確使用吸入器',
    '追蹤：用藥依從性評估',
    '評估：肺功能檢查',
    '回診：胸腔科門診',
    '衛教：呼吸運動指導',
    '追蹤：體重監測',
    '評估：CAT問卷填寫',
    '衛教：營養諮詢',
  ][i % 8],
  description: '任務詳細說明...',
  type: ['EDUCATION', 'TRACKING', 'ASSESSMENT', 'APPOINTMENT'][random(0, 3)],
  status: ['TODO', 'IN_PROGRESS', 'COMPLETED'][random(0, 2)],
  priority: ['LOW', 'MEDIUM', 'HIGH'][random(0, 2)],
  assignee_id: `staff_${random(1, 3)}`,
  patient_id: random(0, 1) ? `p${random(1, 20)}` : null,
  due_date: dayjs().add(random(-7, 14), 'day').format('YYYY-MM-DD'),
  start_date: dayjs().add(random(-7, 7), 'day').format('YYYY-MM-DD'),
  completed_at: randomBool(0.3) ? dayjs().subtract(random(1, 7), 'day').toISOString() : null,
  created_by: 'staff_001',
  created_at: dayjs().subtract(random(1, 30), 'day').toISOString(),
  updated_at: dayjs().subtract(random(0, 7), 'day').toISOString(),
}))

// Mock 衛教資源 (從 CSV 轉換)
export const mockEducationData = `類別,問題,回答
疾病認識與病因,什麼是COPD？,COPD（慢性阻塞性肺病）是一種慢性呼吸道疾病，主要特徵是持續的呼吸道症狀和氣流受限。
疾病認識與病因,COPD的主要原因是什麼？,吸菸是最主要的原因，約佔90%。其他原因包括空氣污染、職業粉塵暴露、遺傳因素等。
症狀與評估,COPD的常見症狀有哪些？,慢性咳嗽、咳痰、呼吸困難、胸悶、活動後喘息、疲勞等。
症狀與評估,什麼是CAT評估？,CAT（COPD評估測試）是評估COPD對生活品質影響的問卷，總分40分，分數越高表示影響越大。
診斷與檢查,如何診斷COPD？,主要透過肺功能檢查（肺量計），FEV1/FVC < 0.7即可診斷。還需配合病史、症狀、影像檢查等。
藥物與吸入治療,COPD常用藥物有哪些？,支氣管擴張劑（如Spiriva、Onbrez）、吸入性類固醇、複方製劑（如Symbicort）等。
藥物與吸入治療,如何正確使用吸入器？,1.打開吸入器 2.深呼氣 3.含住吸嘴 4.深吸氣同時按壓 5.憋氣10秒 6.緩慢呼氣。
急性惡化與就醫,什麼情況需要緊急就醫？,呼吸極度困難、嘴唇發紫、意識不清、胸痛、高燒不退、痰液變膿性等。
疫苗與預防,COPD患者需要打哪些疫苗？,每年流感疫苗、肺炎鏈球菌疫苗（建議每5年一次）、COVID-19疫苗。
氧氣治療與設備,什麼時候需要氧氣治療？,血氧飽和度持續低於88%或PaO2 < 55mmHg時，需要長期氧氣治療。
生活照護與復健,COPD患者如何運動？,建議進行呼吸運動、步行訓練、上肢運動等，每週3-5次，每次20-30分鐘。
生活照護與復健,飲食要注意什麼？,少量多餐、高蛋白質、避免產氣食物、補充足夠水分、避免過鹹食物。
社會資源與補助,有哪些社會資源可以申請？,重大傷病卡、身心障礙證明、居家照護、喘息服務等，可向社工諮詢。`
