import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { CHART_COLORS } from "../../../shared/config";

const BehaviorAdherenceTrend = ({
  data = {},
  range = "month",
  height = 300,
}) => {
  const [viewMode, setViewMode] = useState("overall"); // "individual" 或 "overall"

  // 根據時間範圍獲取對應的日期格式
  const getDateFormat = (range) => {
    switch (range) {
      case "week":
        return (item) =>
          item.date?.replace("2025-", "").replace("2024-", "") ||
          item.day ||
          "";
      case "quarter":
        return (item) => {
          if (item.month) return `${item.month}月`;
          if (item.date) {
            const month = item.date.split("-")[1];
            return `${parseInt(month)}月`;
          }
          return item.week || "";
        };
      case "custom": // last30days
        return (item) =>
          item.date?.split("-").slice(1).join("/") || item.day || "";
      default: // month
        return (item) =>
          item.date?.replace("2025-", "").replace("2024-", "") ||
          item.week ||
          "";
    }
  };

  // 獲取時間範圍標籤
  const getTimeRangeLabel = (range) => {
    switch (range) {
      case "week":
        return "本週";
      case "quarter":
        return "本季";
      case "custom":
        return "最近30天";
      default:
        return "本月";
    }
  };

  // 處理數據結構 - 檢查是否為 adherence API 的回應格式
  let rawData = [];
  if (Array.isArray(data)) {
    // 如果是陣列（來自 trends.daily_trends）
    rawData = data;
  } else if (data.daily_trends && Array.isArray(data.daily_trends)) {
    // 如果是 trends API 回應格式
    rawData = data.daily_trends;
  } else if (data.distribution) {
    // 如果是 adherence API 回應格式，創建假數據以避免錯誤
    const { distribution } = data;
    const totalPatients = distribution.excellent + distribution.good + distribution.fair + distribution.poor;
    const excellentRate = totalPatients > 0 ? (distribution.excellent / totalPatients) : 0;
    
    rawData = [{
      date: new Date().toISOString().split('T')[0],
      med_rate: excellentRate,
      water_rate: excellentRate,
      exercise_rate: excellentRate,
      smoke_tracking_rate: excellentRate
    }];
  }

  // 格式化資料並轉換為百分比
  const formattedData = rawData.map((item) => {
    const 用藥 = Math.round((item.avg_medication || item.med_rate || 0) * 100);
    const 飲水 = Math.round((item.avg_water || item.water_rate || 0) * 100);
    const 運動 = Math.round((item.avg_exercise || item.exercise_rate || 0) * 100);
    const 戒菸追蹤 = Math.round((item.smoke_tracking_rate || 0) * 100);

    // 計算整體達標率（四項平均）
    const 整體達標率 = Math.round((用藥 + 飲水 + 運動 + 戒菸追蹤) / 4);

    const formatDate = getDateFormat(range);

    return {
      week: formatDate(item),
      用藥,
      飲水,
      運動,
      戒菸追蹤,
      整體達標率,
    };
  });

  const individualLines = [
    {
      key: "用藥",
      color: CHART_COLORS.medication,
      icon: "💊",
      title: "用藥達標率",
    },
    { key: "飲水", color: CHART_COLORS.water, icon: "💧", title: "飲水達標率" },
    {
      key: "運動",
      color: CHART_COLORS.exercise,
      icon: "🏃",
      title: "運動達標率",
    },
    {
      key: "戒菸追蹤",
      color: CHART_COLORS.cigarettes,
      icon: "🚭",
      title: "戒菸達標率",
    },
  ];

  const overallLines = [
    { key: "用藥", color: CHART_COLORS.medication },
    { key: "飲水", color: CHART_COLORS.water },
    { key: "運動", color: CHART_COLORS.exercise },
    { key: "戒菸追蹤", color: CHART_COLORS.cigarettes },
  ];

  return (
    <div className="behavior-adherence-container">
      {/* 視圖切換按鈕 */}
      <div className="view-controls">
        <div className="control-group">
          <button
            className={`control-btn ${viewMode === "overall" ? "active" : ""}`}
            onClick={() => setViewMode("overall")}
          >
            <span className="btn-icon">📈</span>
            整體趨勢
          </button>
          <button
            className={`control-btn ${
              viewMode === "individual" ? "active" : ""
            }`}
            onClick={() => setViewMode("individual")}
          >
            <span className="btn-icon">📊</span>
            分項趨勢
          </button>
        </div>

        {/* 當前模式說明 */}
        <div className="mode-description">
          {viewMode === "individual"
            ? `以四個獨立圖表分別顯示各項健康指標趨勢 (${getTimeRangeLabel(
                range
              )})`
            : `在單一圖表中顯示四項健康指標的整體趨勢對比 (${getTimeRangeLabel(
                range
              )})`}
        </div>
      </div>

      {/* 圖表區域 */}
      {viewMode === "overall" ? (
        // 整體趨勢：一張大圖表顯示四條趨勢線
        <ResponsiveContainer width="100%" height={height}>
          <LineChart
            data={formattedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="week" tick={{ fontSize: 12 }} stroke="#6B7280" />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
              tick={{ fontSize: 12 }}
              stroke="#6B7280"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #E5E7EB",
                borderRadius: "8px",
              }}
              formatter={(value) => `${value}%`}
            />
            <Legend wrapperStyle={{ paddingTop: "10px" }} iconType="line" />

            {overallLines.map((line) => (
              <Line
                key={line.key}
                type="monotone"
                dataKey={line.key}
                stroke={line.color}
                strokeWidth={2}
                dot={{ fill: line.color, r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        // 分項趨勢：四個獨立的小圖表
        <div className="individual-charts-grid">
          {individualLines.map((line) => (
            <div key={line.key} className="individual-chart-card">
              <div className="chart-header">
                <span className="chart-icon">{line.icon}</span>
                <h4 className="chart-title">{line.title}</h4>
                <span className="current-value" style={{ color: line.color }}>
                  {formattedData.length > 0
                    ? `${
                        formattedData[formattedData.length - 1]?.[line.key] || 0
                      }%`
                    : "0%"}
                </span>
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart
                  data={formattedData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis
                    dataKey="week"
                    tick={{ fontSize: 11 }}
                    stroke="#9ca3af"
                    height={30}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tickFormatter={(value) => `${value}%`}
                    tick={{ fontSize: 11 }}
                    stroke="#9ca3af"
                    width={40}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #E5E7EB",
                      borderRadius: "6px",
                      fontSize: "12px",
                    }}
                    formatter={(value) => [`${value}%`, line.title]}
                  />
                  <Line
                    type="monotone"
                    dataKey={line.key}
                    stroke={line.color}
                    strokeWidth={2}
                    dot={{ fill: line.color, r: 2 }}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .behavior-adherence-container {
          width: 100%;
        }

        .view-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding: 16px;
          background: #f9fafb;
          border-radius: 12px;
        }

        .control-group {
          display: flex;
          gap: 8px;
          background: white;
          padding: 4px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .control-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: transparent;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          transition: all 200ms;
          font-size: 14px;
          font-weight: 500;
          color: var(--text);
        }

        .control-btn:hover {
          background: #f3f4f6;
        }

        .control-btn.active {
          background: var(--primary);
          color: white;
        }

        .btn-icon {
          font-size: 16px;
        }

        .mode-description {
          font-size: 13px;
          color: var(--muted);
          font-style: italic;
        }

        /* 分項趨勢的四個獨立圖表網格 */
        .individual-charts-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .individual-chart-card {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
          border: 1px solid #e5e7eb;
          transition: all 200ms;
        }

        .individual-chart-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .chart-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }

        .chart-icon {
          font-size: 20px;
          margin-right: 8px;
        }

        .chart-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
          flex: 1;
        }

        .current-value {
          font-size: 18px;
          font-weight: 700;
        }

        @media (max-width: 768px) {
          .view-controls {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
          }

          .control-group {
            justify-content: center;
          }

          .mode-description {
            text-align: center;
          }

          .individual-charts-grid {
            grid-template-columns: 1fr;
            gap: 12px;
          }

          .chart-header {
            flex-wrap: wrap;
            gap: 8px;
          }

          .chart-title {
            font-size: 13px;
          }

          .current-value {
            font-size: 16px;
          }
        }

        @media (min-width: 1280px) {
          .individual-charts-grid {
            grid-template-columns: repeat(4, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default BehaviorAdherenceTrend;
