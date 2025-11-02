import { useState, useEffect } from "react";
import { TASK_TYPES } from "../../../shared/config";
import dayjs from "dayjs";

const TaskFormModal = ({ task, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    type: "EDUCATION",
    priority: "MEDIUM",
    assignee_id: "",
    patient_id: "",
    due_date: dayjs().format("YYYY-MM-DD"),
    start_date: dayjs().format("YYYY-MM-DD"),
    ...task,
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (task) {
      setFormData(prevData => ({ ...prevData, ...task }));
    }
  }, [task]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    // 清除錯誤
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title) newErrors.title = "任務名稱為必填";
    if (!formData.due_date) newErrors.due_date = "截止日期為必填";
    if (formData.start_date > formData.due_date) {
      newErrors.start_date = "開始日期不能晚於截止日期";
    }
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    onSave(formData);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{task ? "編輯任務" : "新增任務"}</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-body">
            {/* 任務名稱 */}
            <div className="form-group">
              <label className="form-label required">任務名稱</label>
              <input
                type="text"
                name="title"
                className={`form-input ${errors.title ? "error" : ""}`}
                value={formData.title}
                onChange={handleChange}
                placeholder="輸入任務名稱"
              />
              {errors.title && (
                <span className="error-message">{errors.title}</span>
              )}
            </div>

            {/* 任務描述 */}
            <div className="form-group">
              <label className="form-label">任務描述</label>
              <textarea
                name="description"
                className="form-textarea"
                value={formData.description}
                onChange={handleChange}
                placeholder="輸入任務詳細描述"
                rows="3"
              />
            </div>

            {/* 類型與優先級 */}
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">任務類型</label>
                <select
                  name="type"
                  className="form-select"
                  value={formData.type}
                  onChange={handleChange}
                >
                  {Object.entries(TASK_TYPES).map(([key, value]) => (
                    <option key={key} value={key}>
                      {value.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">優先級</label>
                <select
                  name="priority"
                  className="form-select"
                  value={formData.priority}
                  onChange={handleChange}
                >
                  <option value="LOW">低</option>
                  <option value="MEDIUM">中</option>
                  <option value="HIGH">高</option>
                </select>
              </div>
            </div>

            {/* 日期 */}
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">開始日期</label>
                <input
                  type="date"
                  name="start_date"
                  className={`form-input ${errors.start_date ? "error" : ""}`}
                  value={formData.start_date}
                  onChange={handleChange}
                />
                {errors.start_date && (
                  <span className="error-message">{errors.start_date}</span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label required">截止日期</label>
                <input
                  type="date"
                  name="due_date"
                  className={`form-input ${errors.due_date ? "error" : ""}`}
                  value={formData.due_date}
                  onChange={handleChange}
                />
                {errors.due_date && (
                  <span className="error-message">{errors.due_date}</span>
                )}
              </div>
            </div>

            {/* 負責人與病患 */}
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">負責治療師</label>
                <input
                  type="text"
                  name="assignee_id"
                  className="form-input"
                  value={formData.assignee_id}
                  onChange={handleChange}
                  placeholder="選擇負責人"
                />
              </div>

              <div className="form-group">
                <label className="form-label">相關病患</label>
                <input
                  type="text"
                  name="patient_id"
                  className="form-input"
                  value={formData.patient_id}
                  onChange={handleChange}
                  placeholder="選擇病患（選填）"
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-cancel" onClick={onClose}>
              取消
            </button>
            <button type="submit" className="btn-submit">
              {task ? "更新" : "建立"}
            </button>
          </div>
        </form>
      </div>

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #e5e7eb;
        }

        .modal-header h2 {
          font-size: 20px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          color: var(--muted);
          cursor: pointer;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          transition: all 200ms;
        }

        .close-btn:hover {
          background: #f3f4f6;
          color: var(--text);
        }

        .form-body {
          padding: 20px;
          overflow-y: auto;
          flex: 1;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }

        .form-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text);
          margin-bottom: 6px;
        }

        .form-label.required::after {
          content: " *";
          color: var(--danger);
        }

        .form-input,
        .form-select,
        .form-textarea {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          transition: all 200ms;
        }

        .form-input:focus,
        .form-select:focus,
        .form-textarea:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(124, 198, 255, 0.1);
        }

        .form-input.error,
        .form-select.error,
        .form-textarea.error {
          border-color: var(--danger);
        }

        .form-textarea {
          resize: vertical;
        }

        .error-message {
          display: block;
          font-size: 12px;
          color: var(--danger);
          margin-top: 4px;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding: 20px;
          border-top: 1px solid #e5e7eb;
        }

        .btn-cancel,
        .btn-submit {
          padding: 10px 20px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 200ms;
          border: none;
        }

        .btn-cancel {
          background: #f3f4f6;
          color: var(--text);
        }

        .btn-cancel:hover {
          background: #e5e7eb;
        }

        .btn-submit {
          background: var(--primary);
          color: white;
        }

        .btn-submit:hover {
          background: #5cb8ff;
        }

        @media (max-width: 640px) {
          .modal-content {
            width: 100%;
            height: 100%;
            max-height: 100%;
            border-radius: 0;
          }

          .form-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskFormModal;
