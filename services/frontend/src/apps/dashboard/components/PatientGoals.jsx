import React, { useMemo, useState } from "react";

// 個人化目標設定與追蹤元件 - 顯示病患目標與實際值（週/月/季）
const PatientGoals = ({ metrics }) => {
  const [timeUnit, setTimeUnit] = useState("week"); // week | month | quarter

  // 目標值（以週為基準），可由治療師調整
  const [targets, setTargets] = useState({
    water_week_cc: 14000,
    med_week_days: 7,
    exercise_week_min: 90,
    cigs_week_count: 0,
  });

  const factor = timeUnit === "week" ? 1 : timeUnit === "month" ? 4 : 13; // 4 週/月, 13 週/季
  const windowDays = timeUnit === "week" ? 7 : timeUnit === "month" ? 28 : 91;

  const recent = useMemo(
    () => metrics?.slice(-windowDays) || [],
    [metrics, windowDays]
  );

  // 適配實際 API 數據結構
  const actual = useMemo(() => {
    if (!recent || recent.length === 0) {
      return { water: 0, med: 0, exercise: 0, cigs: 0 };
    }

    const water = recent.reduce(
      (a, b) => a + (b.water_cc || b.water_ml || 0),
      0
    );
    const med = recent.reduce((a, b) => a + (b.medication_taken ? 1 : 0), 0);
    const exercise = recent.reduce(
      (a, b) => a + (b.exercise_minutes || b.exercise_min || 0),
      0
    );
    const cigs = recent.reduce((a, b) => a + (b.cigarettes || 0), 0);
    return { water, med, exercise, cigs };
  }, [recent]);

  const target = {
    water: targets.water_week_cc * factor,
    med: targets.med_week_days * factor,
    exercise: targets.exercise_week_min * factor,
    cigs: targets.cigs_week_count * factor,
  };

  const updateTarget = (key, value) => {
    setTargets((t) => ({ ...t, [key]: Number(value) }));
  };

  return (
    <div className="bg-white/70 backdrop-blur-md shadow rounded-xl p-6">
      {/* 標題與時間範圍選擇 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">個人化目標追蹤</h3>
        <select
          value={timeUnit}
          onChange={(e) => setTimeUnit(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="week">週</option>
          <option value="month">月</option>
          <option value="quarter">季</option>
        </select>
      </div>

      {/* 目標項目網格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <GoalItem
          label="喝水"
          unit="cc"
          actual={actual.water}
          target={target.water}
          control={
            <NumberInput
              value={targets.water_week_cc}
              onChange={(v) => updateTarget("water_week_cc", v)}
              suffix="/週"
            />
          }
        />
        <GoalItem
          label="吸藥"
          unit="天"
          actual={actual.med}
          target={target.med}
          control={
            <NumberInput
              value={targets.med_week_days}
              onChange={(v) => updateTarget("med_week_days", v)}
              suffix="/週"
            />
          }
        />
        <GoalItem
          label="運動"
          unit="分鐘"
          actual={actual.exercise}
          target={target.exercise}
          control={
            <NumberInput
              value={targets.exercise_week_min}
              onChange={(v) => updateTarget("exercise_week_min", v)}
              suffix="/週"
            />
          }
        />
        <GoalItem
          label="戒菸"
          unit="支"
          actual={actual.cigs}
          target={target.cigs}
          isReverse={true}
          control={
            <NumberInput
              value={targets.cigs_week_count}
              onChange={(v) => updateTarget("cigs_week_count", v)}
              suffix="/週"
            />
          }
        />
      </div>
    </div>
  );
};

// 單項目標卡片
const GoalItem = ({
  label,
  unit,
  actual,
  target,
  control,
  isReverse = false,
}) => {
  const pct =
    target > 0 ? Math.min(100, Math.round((actual / target) * 100)) : 0;

  // 戒菸項目：達標條件是實際值 <= 目標值
  const achievementPct = isReverse
    ? target === 0 && actual === 0
      ? 100
      : Math.max(0, 100 - Math.round((actual / Math.max(target, 1)) * 100))
    : pct;

  const isAchieved = isReverse ? actual <= target : pct >= 100;

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-100 hover:shadow-md transition-shadow">
      {/* 標題與控制項 */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600 font-medium">{label}</span>
        {control}
      </div>

      {/* 數值顯示 */}
      <div className="text-lg font-bold text-gray-800 mb-2">
        {actual} / {target} {unit}
      </div>

      {/* 達標率 */}
      <div className="flex items-center justify-between text-sm mb-3">
        <span className="text-gray-500">達標率</span>
        <span
          className={`font-semibold ${
            isAchieved ? "text-green-600" : "text-blue-600"
          }`}
        >
          {achievementPct}%
        </span>
      </div>

      {/* 進度條 */}
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            isAchieved ? "bg-green-500" : "bg-blue-400"
          }`}
          style={{ width: `${Math.min(100, achievementPct)}%` }}
        />
      </div>
    </div>
  );
};

// 數字輸入控制項
const NumberInput = ({ value, onChange, suffix }) => {
  return (
    <div className="flex items-center gap-1">
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
        min="0"
      />
      <span className="text-xs text-gray-500">{suffix}</span>
    </div>
  );
};

export default PatientGoals;
