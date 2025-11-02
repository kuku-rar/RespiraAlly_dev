import { useState, useEffect } from "react";
import {
  useTasks,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
} from "../../../shared/api/taskHooks";
import TaskCalendar from "../components/TaskCalendar";
import TaskList from "../components/TaskList";
import TaskTable from "../components/TaskTable";
import TaskFormModal from "../components/TaskFormModal";
import TaskFilters from "../components/TaskFilters";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";
import dayjs from "dayjs";

const TherapistTasksPage = () => {
  const [viewMode, setViewMode] = useState(
    localStorage.getItem("tasks:view") || "calendar"
  );
  const [filters, setFilters] = useState({
    from: dayjs().startOf("month").format("YYYY-MM-DD"),
    to: dayjs().endOf("month").format("YYYY-MM-DD"),
    status: "",
    type: "",
    assigneeId: "",
    q: "",
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  // API hooks
  const { data: tasks = [], isLoading } = useTasks(filters);
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const deleteTaskMutation = useDeleteTask();

  // 儲存檢視模式偏好
  useEffect(() => {
    localStorage.setItem("tasks:view", viewMode);
  }, [viewMode]);

  // 處理任務建立/編輯
  const handleSaveTask = async (taskData) => {
    try {
      if (editingTask) {
        await updateTaskMutation.mutateAsync({
          id: editingTask.id,
          patch: taskData,
        });
      } else {
        await createTaskMutation.mutateAsync(taskData);
      }
      setIsModalOpen(false);
      setEditingTask(null);
    } catch (error) {
      console.error("儲存任務失敗:", error);
      alert("儲存失敗，請重試");
    }
  };

  // 處理任務刪除
  const handleDeleteTask = async (taskId) => {
    if (window.confirm("確定要刪除這個任務嗎？")) {
      try {
        await deleteTaskMutation.mutateAsync(taskId);
      } catch (error) {
        console.error("刪除任務失敗:", error);
        alert("刪除失敗，請重試");
      }
    }
  };

  // 處理任務狀態更新
  const handleStatusUpdate = async (taskId, newStatus) => {
    try {
      await updateTaskMutation.mutateAsync({
        id: taskId,
        patch: { status: newStatus },
      });
    } catch (error) {
      console.error("更新狀態失敗:", error);
    }
  };

  // 開啟編輯模式
  const handleEditTask = (task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  // 開啟新增模式
  const handleAddTask = () => {
    setEditingTask(null);
    setIsModalOpen(true);
  };

  if (isLoading) {
    return <LoadingSpinner fullScreen message="載入任務列表..." />;
  }

  return (
    <div className="tasks-page">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="header-left">
          <h2 className="page-title">任務管理</h2>
          <p className="page-subtitle">共 {tasks.length} 個任務</p>
        </div>
        <div className="header-actions">
          <div className="view-switcher">
            <button
              className={`view-btn ${viewMode === "calendar" ? "active" : ""}`}
              onClick={() => setViewMode("calendar")}
            >
              📅 日曆
            </button>
            <button
              className={`view-btn ${viewMode === "kanban" ? "active" : ""}`}
              onClick={() => setViewMode("kanban")}
            >
              📋 看板
            </button>
            <button
              className={`view-btn ${viewMode === "table" ? "active" : ""}`}
              onClick={() => setViewMode("table")}
            >
              📊 表格
            </button>
          </div>
          <button className="btn btn-primary" onClick={handleAddTask}>
            <span>➕</span> 新增任務
          </button>
        </div>
      </div>

      {/* 篩選器 */}
      <TaskFilters filters={filters} onChange={setFilters} />

      {/* 任務檢視 */}
      <div className="task-view">
        {viewMode === "calendar" && (
          <TaskCalendar
            tasks={tasks}
            onTaskClick={handleEditTask}
            onDateClick={(date) => {
              setEditingTask({
                due_date: date,
                start_date: date,
              });
              setIsModalOpen(true);
            }}
          />
        )}
        {viewMode === "kanban" && (
          <TaskList
            tasks={tasks}
            onTaskClick={handleEditTask}
            onStatusChange={handleStatusUpdate}
            onDelete={handleDeleteTask}
          />
        )}
        {viewMode === "table" && (
          <TaskTable
            tasks={tasks}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
            onStatusChange={handleStatusUpdate}
          />
        )}
      </div>

      {/* 任務表單 Modal */}
      {isModalOpen && (
        <TaskFormModal
          task={editingTask}
          onSave={handleSaveTask}
          onClose={() => {
            setIsModalOpen(false);
            setEditingTask(null);
          }}
        />
      )}

      <style jsx>{`
        .tasks-page {
          padding: 0;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .header-left {
          display: flex;
          align-items: baseline;
          gap: 16px;
        }

        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .page-subtitle {
          font-size: 14px;
          color: var(--muted);
        }

        .header-actions {
          display: flex;
          gap: 16px;
          align-items: center;
        }

        .view-switcher {
          display: flex;
          background: white;
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 4px;
        }

        .view-btn {
          padding: 6px 12px;
          border: none;
          background: transparent;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
          border-radius: 6px;
        }

        .view-btn:hover {
          background: #f9fafb;
        }

        .view-btn.active {
          background: var(--primary);
          color: white;
        }

        .task-view {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
          min-height: 600px;
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }

          .header-actions {
            width: 100%;
            justify-content: space-between;
          }

          .view-switcher {
            flex: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default TherapistTasksPage;
