import { useState } from "react";
import { TASK_STATUS, TASK_TYPES } from "../../../shared/config";
import dayjs from "dayjs";

const TaskList = ({ tasks, onTaskClick, onStatusChange, onDelete }) => {
  const [draggedTask, setDraggedTask] = useState(null);
  const [dragOverStatus, setDragOverStatus] = useState(null);

  const columns = [
    { key: "TODO", label: "待辦", color: "#D9D9D9" },
    { key: "IN_PROGRESS", label: "進行中", color: "#7CC6FF" },
    { key: "COMPLETED", label: "已完成", color: "#52C41A" },
  ];

  const getTasksByStatus = (status) => {
    return (Array.isArray(tasks) ? tasks : []).filter(
      (task) => task.status === status
    );
  };

  const handleDragStart = (e, task) => {
    setDraggedTask(task);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (e, status) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setDragOverStatus(status);
  };

  const handleDragLeave = () => {
    setDragOverStatus(null);
  };

  const handleDrop = (e, status) => {
    e.preventDefault();
    if (draggedTask && draggedTask.status !== status) {
      onStatusChange(draggedTask.id, status);
    }
    setDraggedTask(null);
    setDragOverStatus(null);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "HIGH":
        return "#E66A6A";
      case "MEDIUM":
        return "#FAAD14";
      case "LOW":
        return "#52C41A";
      default:
        return "#6B7280";
    }
  };

  return (
    <div className="task-list">
      <div className="kanban-container">
        {columns.map((column) => (
          <div
            key={column.key}
            className={`kanban-column ${
              dragOverStatus === column.key ? "drag-over" : ""
            }`}
            onDragOver={(e) => handleDragOver(e, column.key)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, column.key)}
          >
            <div className="column-header">
              <div className="column-title">
                <span
                  className="status-dot"
                  style={{ background: column.color }}
                />
                <span>{column.label}</span>
              </div>
              <span className="task-count">
                {getTasksByStatus(column.key).length}
              </span>
            </div>

            <div className="task-cards">
              {getTasksByStatus(column.key).map((task) => (
                <div
                  key={task.id}
                  className="task-card"
                  draggable
                  onDragStart={(e) => handleDragStart(e, task)}
                  onClick={() => onTaskClick(task)}
                >
                  <div className="task-header">
                    <span
                      className="task-type"
                      style={{
                        background: `${
                          TASK_TYPES[task.type]?.color || "#7CC6FF"
                        }20`,
                        color: TASK_TYPES[task.type]?.color || "#7CC6FF",
                      }}
                    >
                      {TASK_TYPES[task.type]?.label || task.type}
                    </span>
                    <div className="task-actions">
                      <button
                        className="action-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(task.id);
                        }}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <h4 className="task-title">{task.title}</h4>

                  {task.description && (
                    <p className="task-description">{task.description}</p>
                  )}

                  <div className="task-meta">
                    <div className="meta-item">
                      <span className="meta-icon">📅</span>
                      <span className="meta-text">
                        {dayjs(task.due_date).format("MM/DD")}
                      </span>
                    </div>

                    {task.patient_name && (
                      <div className="meta-item">
                        <span className="meta-icon">👤</span>
                        <span className="meta-text">{task.patient_name}</span>
                      </div>
                    )}

                    <div
                      className="priority-badge"
                      style={{
                        background: `${getPriorityColor(task.priority)}20`,
                        color: getPriorityColor(task.priority),
                      }}
                    >
                      {task.priority === "HIGH"
                        ? "高"
                        : task.priority === "MEDIUM"
                        ? "中"
                        : "低"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .task-list {
          padding: 16px;
        }

        .kanban-container {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
        }

        .kanban-column {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
          min-height: 500px;
          transition: all 200ms;
        }

        .kanban-column.drag-over {
          background: #eff6ff;
          box-shadow: 0 0 0 2px var(--primary);
        }

        .column-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .column-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          color: var(--text);
        }

        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .task-count {
          background: white;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          color: var(--muted);
        }

        .task-cards {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .task-card {
          background: white;
          border-radius: 8px;
          padding: 12px;
          cursor: move;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
          transition: all 200ms;
        }

        .task-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          transform: translateY(-2px);
        }

        .task-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .task-type {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
        }

        .task-actions {
          opacity: 0;
          transition: opacity 200ms;
        }

        .task-card:hover .task-actions {
          opacity: 1;
        }

        .action-btn {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 14px;
          opacity: 0.6;
        }

        .action-btn:hover {
          opacity: 1;
        }

        .task-title {
          font-size: 14px;
          font-weight: 500;
          color: var(--text);
          margin: 0 0 8px 0;
        }

        .task-description {
          font-size: 12px;
          color: var(--muted);
          line-height: 1.4;
          margin: 0 0 8px 0;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .task-meta {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .meta-icon {
          font-size: 12px;
        }

        .meta-text {
          font-size: 12px;
          color: var(--muted);
        }

        .priority-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
          margin-left: auto;
        }

        @media (max-width: 1024px) {
          .kanban-container {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskList;
