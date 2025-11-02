import { useState } from "react";
import { useLocation } from "react-router-dom";
import dayjs from "dayjs";
import quarterOfYear from "dayjs/plugin/quarterOfYear";

// 啟用季度插件
dayjs.extend(quarterOfYear);

const Header = ({ onToggleRightPane, onFiltersChange }) => {
  const location = useLocation();
  const [quickTimeRange, setQuickTimeRange] = useState("month");
  const [riskFilter, setRiskFilter] = useState("");

  // 根據路由決定標題
  const getPageTitle = () => {
    const path = location.pathname;
    if (path.includes("/overview")) return "病患整體趨勢總覽";
    if (path.includes("/cases")) return "病患個案管理";
    if (path.includes("/education")) return "衛教資源管理";
    if (path.includes("/tasks")) return "任務管理";
    return "Dashboard";
  };

  const showFilters =
    location.pathname.includes("/overview") ||
    location.pathname.includes("/cases");

  const handleRiskFilterChange = (value) => {
    setRiskFilter(value);
    if (onFiltersChange) {
      onFiltersChange({ riskFilter: value, quickTimeRange });
    }
  };

  const handleQuickTimeChange = (value) => {
    setQuickTimeRange(value);
    if (onFiltersChange) {
      onFiltersChange({ riskFilter, quickTimeRange: value });
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <h1 className="page-title">{getPageTitle()}</h1>

        {showFilters && (
          <div className="header-filters">
            {/* 快速時間範圍 */}
            <div className="filter-group">
              <label className="filter-label">時間範圍</label>
              <select
                className="select"
                value={quickTimeRange}
                onChange={(e) => handleQuickTimeChange(e.target.value)}
              >
                <option value="week">本週</option>
                <option value="month">本月</option>
                <option value="quarter">本季</option>
                <option value="last30days">最近30天</option>
              </select>
            </div>

            {/* 風險篩選 */}
            <div className="filter-group">
              <label className="filter-label">風險等級</label>
              <select
                className="select"
                value={riskFilter}
                onChange={(e) => handleRiskFilterChange(e.target.value)}
              >
                <option value="">全部風險</option>
                <option value="high">高風險</option>
                <option value="medium">中風險</option>
                <option value="low">低風險</option>
              </select>
            </div>
          </div>
        )}

        {/* 右側按鈕 */}
        <div className="header-actions">
          <button
            className="btn-icon"
            onClick={onToggleRightPane}
            aria-label="切換右側欄"
          >
            📋
          </button>
        </div>
      </div>

      <style jsx>{`
        .header {
          background: var(--bg-top);
          border-bottom: 1px solid var(--border);
          padding: 16px 24px;
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .header-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
        }

        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .header-filters {
          display: flex;
          align-items: center;
          gap: 24px;
          flex: 1;
          justify-content: center;
        }

        .filter-group {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .filter-label {
          font-size: 14px;
          color: var(--muted);
          font-weight: 500;
        }

        .select {
          padding: 6px 10px;
          font-size: 14px;
          min-width: 120px;
          border: 1px solid var(--border);
          border-radius: 6px;
          background: white;
          cursor: pointer;
        }

        .select:focus {
          outline: none;
          border-color: var(--primary);
        }

        .header-actions {
          display: flex;
          gap: 8px;
        }

        .btn-icon {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          border: 1px solid var(--border);
          background: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 200ms;
        }

        .btn-icon:hover {
          background: var(--primary);
          border-color: var(--primary);
          transform: translateY(-1px);
        }

        @media (max-width: 768px) {
          .header-content {
            flex-direction: column;
            align-items: flex-start;
          }

          .header-filters {
            width: 100%;
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </header>
  );
};

export default Header;
