import { useState, useEffect } from "react";
import dayjs from "dayjs";

const TimeRangeTabs = ({ onChange, defaultRange = "week" }) => {
  const [activeRange, setActiveRange] = useState(defaultRange);

  const ranges = [
    {
      key: "day",
      label: "日",
      icon: "📅",
      getValue: () => ({
        from: dayjs().format("YYYY-MM-DD"),
        to: dayjs().format("YYYY-MM-DD"),
        range: "day",
      }),
    },
    {
      key: "week",
      label: "週",
      icon: "📆",
      getValue: () => ({
        from: dayjs().startOf("week").format("YYYY-MM-DD"),
        to: dayjs().endOf("week").format("YYYY-MM-DD"),
        range: "week",
      }),
    },
    {
      key: "month",
      label: "月",
      icon: "📊",
      getValue: () => ({
        from: dayjs().startOf("month").format("YYYY-MM-DD"),
        to: dayjs().endOf("month").format("YYYY-MM-DD"),
        range: "month",
      }),
    },
    {
      key: "quarter",
      label: "季",
      icon: "📈",
      getValue: () => ({
        from: dayjs().startOf("quarter").format("YYYY-MM-DD"),
        to: dayjs().endOf("quarter").format("YYYY-MM-DD"),
        range: "quarter",
      }),
    },
    {
      key: "year",
      label: "年",
      icon: "📉",
      getValue: () => ({
        from: dayjs().startOf("year").format("YYYY-MM-DD"),
        to: dayjs().endOf("year").format("YYYY-MM-DD"),
        range: "year",
      }),
    },
  ];

  // 快速選擇預設
  const quickRanges = [
    {
      key: "last7days",
      label: "最近 7 天",
      getValue: () => ({
        from: dayjs().subtract(7, "day").format("YYYY-MM-DD"),
        to: dayjs().format("YYYY-MM-DD"),
        range: "custom",
      }),
    },
    {
      key: "last30days",
      label: "最近 30 天",
      getValue: () => ({
        from: dayjs().subtract(30, "day").format("YYYY-MM-DD"),
        to: dayjs().format("YYYY-MM-DD"),
        range: "custom",
      }),
    },
    {
      key: "last90days",
      label: "最近 90 天",
      getValue: () => ({
        from: dayjs().subtract(90, "day").format("YYYY-MM-DD"),
        to: dayjs().format("YYYY-MM-DD"),
        range: "custom",
      }),
    },
  ];

  useEffect(() => {
    // 初始化時觸發預設範圍
    const defaultRangeObj = ranges.find((r) => r.key === defaultRange);
    if (defaultRangeObj && onChange) {
      onChange(defaultRangeObj.getValue());
    }
  }, []);

  const handleRangeChange = (range) => {
    setActiveRange(range.key);
    if (onChange) {
      onChange(range.getValue());
    }
  };

  const handleQuickRange = (range) => {
    setActiveRange(range.key);
    if (onChange) {
      onChange(range.getValue());
    }
  };

  return (
    <div className="time-range-container">
      {/* 主要時間範圍標籤 */}
      <div className="range-tabs">
        {ranges.map((range) => (
          <button
            key={range.key}
            className={`range-tab ${activeRange === range.key ? "active" : ""}`}
            onClick={() => handleRangeChange(range)}
          >
            <span className="tab-icon">{range.icon}</span>
            <span className="tab-label">{range.label}</span>
          </button>
        ))}
      </div>

      {/* 快速選擇 */}
      <div className="quick-ranges">
        <span className="quick-label">快速選擇：</span>
        {quickRanges.map((range) => (
          <button
            key={range.key}
            className={`quick-btn ${activeRange === range.key ? "active" : ""}`}
            onClick={() => handleQuickRange(range)}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* 當前範圍顯示 */}
      <div className="current-range">
        <span className="range-display">
          {activeRange === "day" && `今天：${dayjs().format("MM/DD")}`}
          {activeRange === "week" &&
            `本週：${dayjs().startOf("week").format("MM/DD")} - ${dayjs()
              .endOf("week")
              .format("MM/DD")}`}
          {activeRange === "month" && `本月：${dayjs().format("YYYY年MM月")}`}
          {activeRange === "quarter" &&
            `本季：${dayjs().startOf("quarter").format("MM月")} - ${dayjs()
              .endOf("quarter")
              .format("MM月")}`}
          {activeRange === "year" && `今年：${dayjs().format("YYYY年")}`}
          {activeRange === "last7days" && "最近 7 天"}
          {activeRange === "last30days" && "最近 30 天"}
          {activeRange === "last90days" && "最近 90 天"}
        </span>
      </div>

      <style jsx>{`
        .time-range-container {
          background: white;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          margin-bottom: 20px;
        }

        .range-tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 12px;
        }

        .range-tab {
          flex: 1;
          padding: 10px 12px;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 200ms;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .range-tab:hover {
          background: #f3f4f6;
          border-color: var(--primary);
        }

        .range-tab.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .tab-icon {
          font-size: 20px;
        }

        .tab-label {
          font-size: 13px;
          font-weight: 500;
        }

        .quick-ranges {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 0;
          border-top: 1px solid #f3f4f6;
          border-bottom: 1px solid #f3f4f6;
          margin-bottom: 12px;
        }

        .quick-label {
          font-size: 13px;
          color: var(--muted);
          font-weight: 500;
        }

        .quick-btn {
          padding: 6px 12px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          font-size: 12px;
          cursor: pointer;
          transition: all 200ms;
        }

        .quick-btn:hover {
          background: #f9fafb;
          border-color: var(--primary);
        }

        .quick-btn.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .current-range {
          display: flex;
          justify-content: center;
        }

        .range-display {
          font-size: 14px;
          color: var(--text);
          font-weight: 500;
          padding: 8px 16px;
          background: #f9fafb;
          border-radius: 20px;
        }

        @media (max-width: 768px) {
          .range-tabs {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
          }

          .quick-ranges {
            flex-wrap: wrap;
          }

          .tab-icon {
            font-size: 16px;
          }

          .tab-label {
            font-size: 11px;
          }
        }
      `}</style>
    </div>
  );
};

export default TimeRangeTabs;
