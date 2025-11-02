import { useState } from "react";

const EduItemCard = ({
  item,
  isEditing,
  categories = [], // 從父組件傳入類別列表
  onEdit,
  onSave,
  onCancel,
  onDelete,
}) => {
  const [editData, setEditData] = useState(item);

  const handleSave = () => {
    if (!editData.question || !editData.answer) {
      alert("問題和答案都是必填欄位");
      return;
    }
    onSave(editData);
  };

  if (isEditing) {
    return (
      <div className="edu-card editing">
        <div className="card-header">
          <select
            className="category-select"
            value={editData.category}
            onChange={(e) =>
              setEditData({ ...editData, category: e.target.value })
            }
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div className="card-body">
          <textarea
            className="edit-input"
            placeholder="輸入問題..."
            value={editData.question}
            onChange={(e) =>
              setEditData({ ...editData, question: e.target.value })
            }
            rows="2"
          />
          <textarea
            className="edit-input"
            placeholder="輸入答案..."
            value={editData.answer}
            onChange={(e) =>
              setEditData({ ...editData, answer: e.target.value })
            }
            rows="4"
          />

          <input
            className="edit-input"
            placeholder="關鍵詞（選填，以逗號分隔）..."
            value={editData.keywords || ""}
            onChange={(e) =>
              setEditData({ ...editData, keywords: e.target.value })
            }
          />

          <textarea
            className="edit-input"
            placeholder="注意事項或補充說明（選填）..."
            value={editData.notes || ""}
            onChange={(e) =>
              setEditData({ ...editData, notes: e.target.value })
            }
            rows="2"
          />
        </div>

        <div className="card-footer">
          <button className="btn-save" onClick={handleSave}>
            儲存
          </button>
          <button className="btn-cancel" onClick={onCancel}>
            取消
          </button>
          {!item.isNew && (
            <button className="btn-delete" onClick={onDelete}>
              刪除
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="edu-card">
      <div className="card-header">
        <span className="category-badge">{item.category}</span>
        <button className="edit-btn" onClick={onEdit}>
          ✏️
        </button>
      </div>

      <div className="card-body">
        <h4 className="question">Q: {item.question}</h4>
        <p className="answer">A: {item.answer}</p>
        {item.keywords && (
          <div className="meta-info">
            <span className="meta-label">關鍵詞：</span>
            <span className="meta-value">{item.keywords}</span>
          </div>
        )}
        {item.notes && (
          <div className="meta-info">
            <span className="meta-label">備註：</span>
            <span className="meta-value">{item.notes}</span>
          </div>
        )}
      </div>

      <style jsx>{`
        .edu-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          transition: all 200ms;
        }

        .edu-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .edu-card.editing {
          box-shadow: 0 0 0 2px var(--primary);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .category-badge {
          padding: 4px 12px;
          background: #eef6ff;
          color: #2563eb;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .edit-btn {
          background: none;
          border: none;
          font-size: 16px;
          cursor: pointer;
          opacity: 0.6;
          transition: opacity 200ms;
        }

        .edit-btn:hover {
          opacity: 1;
        }

        .category-select {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
        }

        .card-body {
          margin-bottom: 16px;
        }

        .question {
          font-size: 15px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 12px 0;
          line-height: 1.4;
        }

        .answer {
          font-size: 14px;
          color: var(--text);
          line-height: 1.6;
          margin: 0 0 8px 0;
        }

        .meta-info {
          margin-top: 8px;
          font-size: 12px;
          color: var(--muted);
        }

        .meta-label {
          font-weight: 500;
          margin-right: 4px;
        }

        .meta-value {
          color: var(--text);
        }

        .edit-input {
          width: 100%;
          padding: 10px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          resize: vertical;
          margin-bottom: 12px;
        }

        .edit-input:focus {
          outline: none;
          border-color: var(--primary);
        }

        .card-footer {
          display: flex;
          gap: 8px;
        }

        .btn-save,
        .btn-cancel,
        .btn-delete {
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 14px;
          cursor: pointer;
          transition: all 200ms;
          border: none;
        }

        .btn-save {
          background: var(--primary);
          color: white;
        }

        .btn-save:hover {
          background: #5cb8ff;
        }

        .btn-cancel {
          background: #f3f4f6;
          color: var(--text);
        }

        .btn-cancel:hover {
          background: #e5e7eb;
        }

        .btn-delete {
          background: #fee2e2;
          color: #dc2626;
        }

        .btn-delete:hover {
          background: #fecaca;
        }
      `}</style>
    </div>
  );
};

export default EduItemCard;
