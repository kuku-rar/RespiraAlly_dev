import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

const BehaviorOverviewTrends = ({ data, range = "month" }) => {
  // 計算達標率趨勢數據
  const achievementTrends = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];

    // 目標值設定（根據時間範圍調整）
    const getTargets = () => {
      switch (range) {
        case "week":
          return {
            water_target: 14000, // 週喝水量 (cc)
            med_target: 7, // 週用藥天數
            exercise_target: 90, // 週運動分鐘
            cigs_target: 0, // 週抽菸數（越少越好）
          };
        case "month":
          return {
            water_target: 60000, // 月喝水量
            med_target: 30, // 月用藥天數
            exercise_target: 390, // 月運動分鐘
            cigs_target: 0,
          };
        default:
          return {
            water_target: 2000, // 日喝水量
            med_target: 1, // 日用藥
            exercise_target: 30, // 日運動分鐘
            cigs_target: 0,
          };
      }
    };

    const targets = getTargets();

    return data.map((item) => {
      // 計算各項指標的達標率
      const waterRate =
        item.water_cc && targets.water_target > 0
          ? Math.min(
              100,
              Math.round((item.water_cc / targets.water_target) * 100)
            )
          : 0;

      const exerciseRate =
        item.exercise_minutes && targets.exercise_target > 0
          ? Math.min(
              100,
              Math.round(
                (item.exercise_minutes / targets.exercise_target) * 100
              )
            )
          : 0;

      const medicationRate =
        item.medication_taken !== undefined
          ? item.medication_taken
            ? 100
            : 0
          : Math.round((item.med_rate || 0) * 100);

      // 抽菸指標：數值越低越好
      const cigaretteRate =
        item.cigarettes !== undefined
          ? Math.max(0, Math.min(100, 100 - (item.cigarettes / 10) * 100))
          : 100;

      return {
        ...item,
        date_label:
          item.date?.replace("2025-", "").replace("2024-", "") ||
          item.week ||
          item.month ||
          "",
        water_achievement: waterRate,
        exercise_achievement: exerciseRate,
        medication_achievement: medicationRate,
        cigarette_achievement: cigaretteRate,
        overall_achievement: Math.round(
          (waterRate + exerciseRate + medicationRate + cigaretteRate) / 4
        ),
      };
    });
  }, [data, range]);

  return (
    <div className="behavior-overview-container">
      <div className="metrics-grid">
        <MiniAreaChart
          title="喝水達標率"
          dataKey="water_achievement"
          data={achievementTrends}
          color="#22c55e"
          suffix="%"
          icon="💧"
        />
        <MiniAreaChart
          title="運動達標率"
          dataKey="exercise_achievement"
          data={achievementTrends}
          color="#06b6d4"
          suffix="%"
          icon="🏃"
        />
        <MiniAreaChart
          title="用藥達標率"
          dataKey="medication_achievement"
          data={achievementTrends}
          color="#3b82f6"
          suffix="%"
          icon="💊"
        />
        <MiniAreaChart
          title="戒菸達標率"
          dataKey="cigarette_achievement"
          data={achievementTrends}
          color="#a78bfa"
          suffix="%"
          icon="🚭"
        />
      </div>

      {/* 整體達標率概覽 */}
      <div className="overall-achievement-section">
        <h4 className="section-title">整體達標率趨勢</h4>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={achievementTrends}>
              <defs>
                <linearGradient id="overallGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.6} />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#eef2ff" vertical={false} />
              <XAxis
                dataKey="date_label"
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                stroke="#6b7280"
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value) => [`${value}%`, "整體達標率"]}
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #E5E7EB",
                  borderRadius: "8px",
                }}
              />
              <Area
                type="monotone"
                dataKey="overall_achievement"
                stroke="#7c3aed"
                strokeWidth={2}
                fill="url(#overallGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <style jsx>{`
        .behavior-overview-container {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
          margin-bottom: 24px;
        }

        .overall-achievement-section {
          padding-top: 20px;
          border-top: 1px solid #e5e7eb;
        }

        .section-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 16px;
        }

        .chart-container {
          height: 200px;
        }

        @media (max-width: 768px) {
          .metrics-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (min-width: 1280px) {
          .metrics-grid {
            grid-template-columns: repeat(4, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

// 小面積圖元件
const MiniAreaChart = ({
  title,
  dataKey,
  data,
  color = "#16a34a",
  suffix = "",
  icon = "📊",
}) => {
  return (
    <div className="mini-chart-card">
      <div className="chart-header">
        <span className="chart-icon">{icon}</span>
        <div className="chart-info">
          <span className="chart-title">{title}</span>
          {data.length > 0 && (
            <span className="current-value" style={{ color }}>
              {data[data.length - 1]?.[dataKey] || 0}
              {suffix}
            </span>
          )}
        </div>
      </div>
      <div className="mini-chart">
        <ResponsiveContainer width="100%" height={100}>
          <AreaChart
            data={data}
            margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
          >
            <defs>
              <linearGradient
                id={`grad-${dataKey}`}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              stroke="#f3f4f6"
              strokeDasharray="3 3"
              vertical={false}
            />
            <XAxis dataKey="date_label" hide />
            <YAxis hide domain={suffix === "%" ? [0, 100] : undefined} />
            <Tooltip
              formatter={(v) => `${v}${suffix}`}
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #E5E7EB",
                borderRadius: "6px",
                fontSize: "12px",
              }}
            />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              fill={`url(#grad-${dataKey})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <style jsx>{`
        .mini-chart-card {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
          transition: all 200ms;
        }

        .mini-chart-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .chart-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .chart-icon {
          font-size: 24px;
        }

        .chart-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .chart-title {
          font-size: 13px;
          color: var(--muted);
          font-weight: 500;
        }

        .current-value {
          font-size: 20px;
          font-weight: 700;
        }

        .mini-chart {
          height: 100px;
        }
      `}</style>
    </div>
  );
};

export default BehaviorOverviewTrends;
