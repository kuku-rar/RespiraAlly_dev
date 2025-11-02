import { useState, useEffect, useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { useGlobalFilters } from "../contexts/GlobalFiltersContext";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";
import dayjs from "dayjs";

const UsageOverviewTab = () => {
  const { globalFilters } = useGlobalFilters();
  const [isLoading, setIsLoading] = useState(true);

  // 模擬載入延遲
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  // 根據時間範圍生成模擬數據
  const usageData = useMemo(() => {
    const days = globalFilters.quickTimeRange === "week" ? 7 : 30;
    return Array.from({ length: days }, (_, i) => ({
      date: dayjs()
        .subtract(days - 1 - i, "day")
        .format("MM/DD"),
      dailyLogins: Math.floor(Math.random() * 50) + 20,
      voiceChats: Math.floor(Math.random() * 30) + 10,
      healthRecords: Math.floor(Math.random() * 40) + 15,
      questionnaires: Math.floor(Math.random() * 25) + 5,
      sessionDuration: Math.floor(Math.random() * 45) + 15, // minutes
    }));
  }, [globalFilters.quickTimeRange]);

  // 功能使用分布數據
  const featureUsageData = [
    { name: "語音對話", value: 35, color: "#7CC6FF" },
    { name: "健康記錄", value: 28, color: "#52C41A" },
    { name: "問卷填寫", value: 20, color: "#FAAD14" },
    { name: "衛教資源", value: 12, color: "#CBA6FF" },
    { name: "其他功能", value: 5, color: "#F56C6C" },
  ];

  // 用戶活躍度數據
  const activityData = [
    { activity: "每日登入", current: 142, target: 150, percentage: 95 },
    { activity: "健康追蹤", current: 128, target: 140, percentage: 91 },
    { activity: "語音互動", current: 96, target: 120, percentage: 80 },
    { activity: "問卷完成", current: 74, target: 100, percentage: 74 },
  ];

  // 使用時段分析數據
  const hourlyUsageData = Array.from({ length: 24 }, (_, i) => {
    let usage;
    if (i >= 6 && i <= 9) usage = Math.random() * 30 + 40; // 早晨高峰
    else if (i >= 12 && i <= 14) usage = Math.random() * 25 + 35; // 午間
    else if (i >= 19 && i <= 22) usage = Math.random() * 40 + 50; // 晚間高峰
    else usage = Math.random() * 15 + 5; // 其他時段

    return {
      hour: `${i.toString().padStart(2, "0")}:00`,
      usage: Math.floor(usage),
    };
  });

  if (isLoading) {
    return <LoadingSpinner fullScreen message="載入使用數據..." />;
  }

  return (
    <div className="usage-overview-tab">
      {/* 使用統計 KPI */}
      <section className="kpi-section">
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">👥</span>
              <span className="kpi-label">活躍用戶</span>
            </div>
            <div className="kpi-value">142</div>
            <div className="kpi-trend positive">+8.2%</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">📱</span>
              <span className="kpi-label">平均會話時長</span>
            </div>
            <div className="kpi-value">28分鐘</div>
            <div className="kpi-trend positive">+12.5%</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">💬</span>
              <span className="kpi-label">語音互動次數</span>
            </div>
            <div className="kpi-value">1,247</div>
            <div className="kpi-trend positive">+15.8%</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">📝</span>
              <span className="kpi-label">問卷完成率</span>
            </div>
            <div className="kpi-value">74%</div>
            <div className="kpi-trend negative">-3.2%</div>
          </div>
        </div>
      </section>

      {/* 圖表區 - 第一排 */}
      <section className="charts-row">
        <div className="chart-card">
          <h3 className="chart-title">每日使用趨勢</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="dailyLogins"
                stroke="#7CC6FF"
                strokeWidth={2}
                name="每日登入"
              />
              <Line
                type="monotone"
                dataKey="voiceChats"
                stroke="#52C41A"
                strokeWidth={2}
                name="語音對話"
              />
              <Line
                type="monotone"
                dataKey="healthRecords"
                stroke="#FAAD14"
                strokeWidth={2}
                name="健康記錄"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">功能使用分布</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={featureUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {featureUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* 圖表區 - 第二排 */}
      <section className="charts-row">
        <div className="chart-card">
          <h3 className="chart-title">用戶活躍度達成情況</h3>
          <div className="activity-list">
            {activityData.map((item, index) => (
              <div key={index} className="activity-item">
                <div className="activity-info">
                  <span className="activity-name">{item.activity}</span>
                  <span className="activity-stats">
                    {item.current} / {item.target}
                  </span>
                </div>
                <div className="activity-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${item.percentage}%`,
                        backgroundColor:
                          item.percentage >= 90
                            ? "#52C41A"
                            : item.percentage >= 70
                            ? "#FAAD14"
                            : "#F56C6C",
                      }}
                    />
                  </div>
                  <span className="progress-percentage">
                    {item.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">24小時使用熱力圖</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={hourlyUsageData}>
              <defs>
                <linearGradient id="usageGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7CC6FF" stopOpacity={0.6} />
                  <stop offset="100%" stopColor="#7CC6FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={2} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value) => [`${value}人`, "使用人數"]}
                labelFormatter={(label) => `時間: ${label}`}
              />
              <Area
                type="monotone"
                dataKey="usage"
                stroke="#7CC6FF"
                strokeWidth={2}
                fill="url(#usageGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* 詳細使用統計 */}
      <section className="section">
        <div className="chart-card full-width">
          <h3 className="chart-title">應用功能使用詳細統計</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="voiceChats" fill="#7CC6FF" name="語音對話" />
              <Bar dataKey="healthRecords" fill="#52C41A" name="健康記錄" />
              <Bar dataKey="questionnaires" fill="#FAAD14" name="問卷填寫" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <style jsx>{`
        .usage-overview-tab {
          padding: 0;
        }

        .section {
          margin-bottom: 24px;
        }

        .kpi-section {
          margin-bottom: 32px;
        }

        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }

        .kpi-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
          transition: all 200ms;
        }

        .kpi-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .kpi-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
        }

        .kpi-icon {
          font-size: 24px;
        }

        .kpi-label {
          font-size: 14px;
          color: var(--muted);
          font-weight: 500;
        }

        .kpi-value {
          font-size: 32px;
          font-weight: 700;
          color: var(--text);
          margin-bottom: 8px;
        }

        .kpi-trend {
          font-size: 14px;
          font-weight: 500;
        }

        .kpi-trend.positive {
          color: #52c41a;
        }

        .kpi-trend.negative {
          color: #f56c6c;
        }

        .kpi-trend::before {
          content: "↗";
          margin-right: 4px;
        }

        .kpi-trend.negative::before {
          content: "↘";
        }

        .charts-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          margin-bottom: 24px;
        }

        .chart-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .chart-card.full-width {
          grid-column: 1 / -1;
        }

        .chart-title {
          font-size: 18px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 16px;
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .activity-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: #f9fafb;
          border-radius: 12px;
        }

        .activity-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .activity-name {
          font-weight: 500;
          color: var(--text);
        }

        .activity-stats {
          font-size: 12px;
          color: var(--muted);
        }

        .activity-progress {
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 120px;
        }

        .progress-bar {
          flex: 1;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 300ms ease;
        }

        .progress-percentage {
          font-size: 12px;
          font-weight: 500;
          color: var(--text);
          min-width: 40px;
          text-align: right;
        }

        @media (max-width: 1024px) {
          .charts-row {
            grid-template-columns: 1fr;
          }

          .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 768px) {
          .kpi-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default UsageOverviewTab;
