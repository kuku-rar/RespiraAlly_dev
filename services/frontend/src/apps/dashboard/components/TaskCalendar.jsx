import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { TASK_TYPES, TASK_STATUS } from "../../../shared/config";

const TaskCalendar = ({ tasks = [], onTaskClick, onDateClick }) => {
  // 確保 tasks 是陣列，並提供安全的轉換
  const safeTasks = Array.isArray(tasks) ? tasks : [];
  
  // 轉換任務為日曆事件
  const events = safeTasks.map((task) => ({
    id: task.id,
    title: task.title,
    start: task.start_date || task.due_date,
    end: task.due_date,
    backgroundColor: TASK_TYPES[task.type]?.color || "#7CC6FF",
    borderColor: TASK_TYPES[task.type]?.color || "#7CC6FF",
    extendedProps: {
      task: task,
    },
  }));

  const handleEventClick = (info) => {
    onTaskClick(info.event.extendedProps.task);
  };

  const handleDateClick = (info) => {
    onDateClick(info.dateStr);
  };

  return (
    <div className="task-calendar">
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        locale="zh-tw"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,dayGridWeek",
        }}
        buttonText={{
          today: "今天",
          month: "月",
          week: "週",
        }}
        events={events}
        eventClick={handleEventClick}
        dateClick={handleDateClick}
        height="auto"
        dayMaxEvents={3}
        eventDisplay="block"
        eventTimeFormat={{
          hour: "2-digit",
          minute: "2-digit",
          meridiem: false,
        }}
      />

      <style jsx global>{`
        .task-calendar {
          padding: 16px;
        }

        .fc {
          font-family: "Noto Sans TC", sans-serif;
        }

        .fc-toolbar-title {
          font-size: 20px;
          font-weight: 600;
          color: var(--text);
        }

        .fc-button {
          background: white;
          border: 1px solid var(--border);
          color: var(--text);
          padding: 6px 12px;
          font-weight: 500;
        }

        .fc-button:hover {
          background: #f9fafb;
        }

        .fc-button-active {
          background: var(--primary) !important;
          color: white !important;
          border-color: var(--primary) !important;
        }

        .fc-event {
          border-radius: 6px;
          padding: 2px 4px;
          cursor: pointer;
          font-size: 13px;
        }

        .fc-event:hover {
          opacity: 0.8;
        }

        .fc-daygrid-day-number {
          color: var(--text);
          font-weight: 500;
        }

        .fc-col-header-cell-cushion {
          color: var(--muted);
          font-weight: 500;
        }

        .fc-daygrid-day.fc-day-today {
          background: rgba(124, 198, 255, 0.1);
        }

        .fc-more-link {
          color: var(--primary);
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default TaskCalendar;
