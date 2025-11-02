import { TASK_STATUS, TASK_TYPES } from "../../../shared/config";
import dayjs from "dayjs";

const TaskTable = ({ tasks, onEdit, onDelete, onStatusChange }) => {
  const getStatusColor = (status) => {
    return TASK_STATUS[status]?.color || "#6B7280";
  };

  const getTypeColor = (type) => {
    return TASK_TYPES[type]?.color || "#7CC6FF";
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case "HIGH":
        return { label: "高", color: "#E66A6A" };
      case "MEDIUM":
        return { label: "中", color: "#FAAD14" };
      case "LOW":
        return { label: "低", color: "#52C41A" };
      default:
        return { label: "-", color: "#6B7280" };
    }
  };

  return (
    <div className="task-table">
      <table>
        <thead>
          <tr>
            <th>任務名稱</th>
            <th>類型</th>
            <th>狀態</th>
            <th>優先級</th>
            <th>負責人</th>
            <th>病患</th>
            <th>截止日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 ? (
            <tr>
              <td colSpan="8" className="empty-row">
                <div className="empty-state">
                  <span className="empty-icon">📋</span>
                  <p>沒有任務</p>
                </div>
              </td>
            </tr>
          ) : (
            tasks.map((task) => {
              const priority = getPriorityLabel(task.priority);
              return (
                <tr key={task.id}>
                  <td>
                    <div className="task-name">{task.title}</div>
                  </td>
                  <td>
                    <span
                      className="type-badge"
                      style={{
                        background: `${getTypeColor(task.type)}20`,
                        color: getTypeColor(task.type),
                      }}
                    >
                      {TASK_TYPES[task.type]?.label || task.type}
                    </span>
                  </td>
                  <td>
                    <select
                      className="status-select"
                      value={task.status}
                      onChange={(e) => onStatusChange(task.id, e.target.value)}
                      style={{
                        color: getStatusColor(task.status),
                        borderColor: getStatusColor(task.status),
                      }}
                    >
                      <option value="TODO">待辦</option>
                      <option value="IN_PROGRESS">進行中</option>
                      <option value="COMPLETED">已完成</option>
                    </select>
                  </td>
                  <td>
                    <span
                      className="priority-badge"
                      style={{
                        background: `${priority.color}20`,
                        color: priority.color,
                      }}
                    >
                      {priority.label}
                    </span>
                  </td>
                  <td>
                    <span className="assignee">
                      {task.assignee_name || "-"}
                    </span>
                  </td>
                  <td>
                    <span className="patient">{task.patient_name || "-"}</span>
                  </td>
                  <td>
                    <span className="due-date">
                      {dayjs(task.due_date).format("YYYY/MM/DD")}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button
                        className="action-btn edit"
                        onClick={() => onEdit(task)}
                        title="編輯"
                      >
                        ✏️
                      </button>
                      <button
                        className="action-btn delete"
                        onClick={() => onDelete(task.id)}
                        title="刪除"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>

      <style jsx>{`
        .task-table {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          background: #f9fafb;
          padding: 12px;
          text-align: left;
          font-size: 14px;
          font-weight: 600;
          color: var(--text);
          border-bottom: 2px solid #e5e7eb;
          white-space: nowrap;
        }

        td {
          padding: 12px;
          border-bottom: 1px solid #f3f4f6;
          font-size: 14px;
        }

        tr:hover {
          background: #f9fafb;
        }

        .empty-row {
          text-align: center;
          padding: 40px;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          color: var(--muted);
        }

        .empty-icon {
          font-size: 32px;
          opacity: 0.3;
        }

        .task-name {
          font-weight: 500;
          color: var(--text);
        }

        .type-badge,
        .priority-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-select {
          padding: 4px 8px;
          border: 1px solid;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
          background: white;
          cursor: pointer;
        }

        .assignee,
        .patient {
          color: var(--text);
        }

        .due-date {
          color: var(--muted);
          font-size: 13px;
        }

        .actions {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 16px;
          opacity: 0.6;
          transition: opacity 200ms;
        }

        .action-btn:hover {
          opacity: 1;
        }

        @media (max-width: 768px) {
          th,
          td {
            padding: 8px;
            font-size: 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskTable;
