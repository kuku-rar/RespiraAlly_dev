import { TASK_TYPES } from "../../../shared/config";
import dayjs from "dayjs";

const TaskFilters = ({ filters, onChange }) => {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  const handleReset = () => {
    onChange({
      from: dayjs().startOf("month").format("YYYY-MM-DD"),
      to: dayjs().endOf("month").format("YYYY-MM-DD"),
      status: "",
      type: "",
      assigneeId: "",
      q: "",
    });
  };

  return (
    <div className="task-filters">
      <div className="filter-row">
        {/* 日期範圍 */}
        <div className="filter-group">
          <label className="filter-label">日期範圍</label>
          <div className="date-range">
            <input
              type="date"
              className="filter-input"
              value={filters.from}
              onChange={(e) => handleChange("from", e.target.value)}
            />
            <span className="date-separator">至</span>
            <input
              type="date"
              className="filter-input"
              value={filters.to}
              onChange={(e) => handleChange("to", e.target.value)}
            />
          </div>
        </div>

        {/* 狀態篩選 */}
        <div className="filter-group">
          <label className="filter-label">狀態</label>
          <select
            className="filter-select"
            value={filters.status}
            onChange={(e) => handleChange("status", e.target.value)}
          >
            <option value="">全部狀態</option>
            <option value="TODO">待辦</option>
            <option value="IN_PROGRESS">進行中</option>
            <option value="COMPLETED">已完成</option>
          </select>
        </div>

        {/* 類型篩選 */}
        <div className="filter-group">
          <label className="filter-label">類型</label>
          <select
            className="filter-select"
            value={filters.type}
            onChange={(e) => handleChange("type", e.target.value)}
          >
            <option value="">全部類型</option>
            {Object.entries(TASK_TYPES).map(([key, value]) => (
              <option key={key} value={key}>
                {value.label}
              </option>
            ))}
          </select>
        </div>

        {/* 關鍵字搜尋 */}
        <div className="filter-group flex-grow">
          <label className="filter-label">搜尋</label>
          <input
            type="text"
            className="filter-input"
            placeholder="搜尋任務名稱..."
            value={filters.q}
            onChange={(e) => handleChange("q", e.target.value)}
          />
        </div>

        {/* 重置按鈕 */}
        <div className="filter-group">
          <label className="filter-label">&nbsp;</label>
          <button className="reset-btn" onClick={handleReset}>
            重置篩選
          </button>
        </div>
      </div>

      <style jsx>{`
        .task-filters {
          background: white;
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .filter-row {
          display: flex;
          gap: 16px;
          align-items: flex-end;
          flex-wrap: wrap;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .filter-group.flex-grow {
          flex: 1;
          min-width: 200px;
        }

        .filter-label {
          font-size: 12px;
          font-weight: 500;
          color: var(--muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .date-range {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .date-separator {
          color: var(--muted);
          font-size: 14px;
        }

        .filter-input,
        .filter-select {
          padding: 8px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          background: white;
          transition: all 200ms;
        }

        .filter-input:focus,
        .filter-select:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(124, 198, 255, 0.1);
        }

        .reset-btn {
          padding: 8px 16px;
          background: #f3f4f6;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
          white-space: nowrap;
        }

        .reset-btn:hover {
          background: #e5e7eb;
        }

        @media (max-width: 768px) {
          .filter-row {
            flex-direction: column;
          }

          .filter-group {
            width: 100%;
          }

          .date-range {
            flex-direction: column;
            align-items: stretch;
          }

          .date-separator {
            text-align: center;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskFilters;
