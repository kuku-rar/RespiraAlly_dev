import dayjs from "dayjs";

// 生成隨機數字
const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// Mock 任務資料
export const mockTasks = Array.from({ length: 30 }, (_, i) => ({
  id: `task_${i + 1}`,
  title: [
    "衛教：正確使用吸入器",
    "追蹤：用藥依從性評估",
    "評估：肺功能檢查",
    "回診：胸腔科門診",
    "衛教：呼吸運動指導",
    "追蹤：體重監測",
    "評估：CAT問卷填寫",
    "衛教：營養諮詢",
    "追蹤：症狀變化記錄",
    "評估：運動耐受度測試",
  ][i % 10],
  description: "任務詳細說明，包含執行步驟和注意事項...",
  type: ["EDUCATION", "TRACKING", "ASSESSMENT", "APPOINTMENT"][random(0, 3)],
  status: ["TODO", "IN_PROGRESS", "COMPLETED"][random(0, 2)],
  priority: ["LOW", "MEDIUM", "HIGH"][random(0, 2)],
  assignee_id: `staff_${random(1, 3)}`,
  assignee_name: ["王治療師", "李治療師", "張治療師"][random(0, 2)],
  patient_id: random(0, 1) ? `p${random(1, 20)}` : null,
  patient_name: random(0, 1)
    ? ["王小明", "李大華", "張美玲"][random(0, 2)]
    : null,
  due_date: dayjs().add(random(-7, 14), "day").format("YYYY-MM-DD"),
  start_date: dayjs().add(random(-7, 7), "day").format("YYYY-MM-DD"),
  completed_at:
    random(0, 1) && i % 3 === 0
      ? dayjs().subtract(random(1, 7), "day").toISOString()
      : null,
  created_by: "staff_001",
  created_at: dayjs().subtract(random(1, 30), "day").toISOString(),
  updated_at: dayjs().subtract(random(0, 7), "day").toISOString(),
}));
