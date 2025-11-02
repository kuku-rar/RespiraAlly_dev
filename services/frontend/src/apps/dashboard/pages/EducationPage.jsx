// services/web-app/frontend/src/apps/dashboard/pages/EducationPage.jsx
/**
 * 衛教資源管理頁面
 * 使用 Milvus API 進行 CRUD 操作
 */
import { useState } from "react";
import {
  useEducationList,
  useEducationCategories,
  useCreateEducation,
  useUpdateEducation,
  useDeleteEducation,
  useBatchImportEducation,
  exportEducationToCSV,
} from "../../../shared/api/educationHooks";
import EduSearchBar from "../components/EduSearchBar";
import EduCategoryFilter from "../components/EduCategoryFilter";
import EduItemCard from "../components/EduItemCard";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";

const EducationPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [editingItem, setEditingItem] = useState(null);
  const [isImporting, setIsImporting] = useState(false);

  // API Hooks
  const {
    data: eduData = [],
    isLoading,
    error: loadError,
  } = useEducationList({
    category: selectedCategory,
    q: searchTerm,
    limit: 1000,
  });

  const { data: categories = [], isLoading: categoriesLoading } =
    useEducationCategories();

  const createMutation = useCreateEducation();
  const updateMutation = useUpdateEducation();
  const deleteMutation = useDeleteEducation();
  const batchImportMutation = useBatchImportEducation();

  // 顯示訊息
  const showMessage = (type, message) => {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 12px 24px;
      background: ${type === "error" ? "#ff4d4f" : "#52c41a"};
      color: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 1000;
      animation: slideDown 0.3s ease;
    `;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
  };

  // 新增項目
  const handleAdd = () => {
    const newItem = {
      id: `edu_new_${Date.now()}`,
      category: categories[0] || "一般",
      question: "",
      answer: "",
      keywords: "",
      notes: "",
      isNew: true,
    };
    setEditingItem(newItem);
  };

  // 儲存項目（新增或更新）
  const handleSave = async (item) => {
    try {
      // 準備資料（移除前端專用欄位）
      const dataToSave = {
        category: item.category || "",
        question: item.question || "",
        answer: item.answer || "",
        keywords: item.keywords || "",
        notes: item.notes || "",
      };

      if (item.isNew) {
        // 新增
        await createMutation.mutateAsync(dataToSave);
        showMessage("success", "新增成功！");
      } else {
        // 更新
        // 需要從 id 中提取數字 ID（如果 id 是 "edu_123" 格式）
        const numericId =
          typeof item.id === "string" && item.id.startsWith("edu_")
            ? parseInt(item.id.replace("edu_", ""))
            : item.id;

        await updateMutation.mutateAsync({
          id: numericId,
          data: dataToSave,
        });
        showMessage("success", "更新成功！");
      }

      setEditingItem(null);
    } catch (error) {
      console.error("儲存失敗:", error);
      showMessage("error", error.message || "儲存失敗，請重試");
    }
  };

  // 刪除項目
  const handleDelete = async (id) => {
    if (window.confirm("確定要刪除這個問答嗎？")) {
      try {
        // 提取數字 ID
        const numericId =
          typeof id === "string" && id.startsWith("edu_")
            ? parseInt(id.replace("edu_", ""))
            : id;

        await deleteMutation.mutateAsync(numericId);
        showMessage("success", "刪除成功！");
      } catch (error) {
        console.error("刪除失敗:", error);
        showMessage("error", error.message || "刪除失敗，請重試");
      }
    }
  };

  // 匯出 CSV
  const handleExport = () => {
    if (!eduData || eduData.length === 0) {
      showMessage("error", "沒有資料可以匯出");
      return;
    }

    try {
      exportEducationToCSV(eduData);
      showMessage("success", "匯出成功！");
    } catch (error) {
      console.error("匯出失敗:", error);
      showMessage("error", "匯出失敗，請重試");
    }
  };

  // 匯入 CSV/Excel
  const handleImport = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsImporting(true);
      try {
        const result = await batchImportMutation.mutateAsync(file);
        showMessage(
          "success",
          `匯入成功！共匯入 ${result.imported} 筆，失敗 ${result.failed} 筆`
        );
      } catch (error) {
        console.error("匯入失敗:", error);
        showMessage("error", error.message || "匯入失敗，請重試");
      } finally {
        setIsImporting(false);
        // 清空檔案輸入
        event.target.value = "";
      }
    }
  };

  // 載入中狀態
  if (isLoading) {
    return <LoadingSpinner fullScreen message="載入衛教資源..." />;
  }

  // 錯誤狀態
  if (loadError) {
    return (
      <div className="error-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <h3>載入失敗</h3>
          <p>{loadError.message || "無法載入衛教資源"}</p>
          <button
            className="btn btn-primary"
            onClick={() => window.location.reload()}
          >
            重新載入
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="education-page">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="header-left">
          <h2 className="page-title">衛教資源管理</h2>
          <p className="page-subtitle">
            共 {eduData.length} 筆問答資料
            {categoriesLoading ? " (載入類別中...)" : ""}
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={handleExport}
            disabled={!eduData || eduData.length === 0}
          >
            <span>📥</span> 匯出 CSV
          </button>
          <label
            className={`btn btn-secondary ${isImporting ? "disabled" : ""}`}
          >
            <span>📤</span> {isImporting ? "匯入中..." : "匯入 CSV"}
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleImport}
              disabled={isImporting}
              style={{ display: "none" }}
            />
          </label>
          <button className="btn btn-primary" onClick={handleAdd}>
            <span>➕</span> 新增問答
          </button>
        </div>
      </div>

      {/* 搜尋與篩選 */}
      <div className="filter-section">
        <EduSearchBar value={searchTerm} onChange={setSearchTerm} />
        <EduCategoryFilter
          categories={categories}
          selected={selectedCategory}
          onChange={setSelectedCategory}
        />
      </div>

      {/* 問答卡片列表 */}
      <div className="edu-grid">
        {editingItem && (
          <EduItemCard
            item={editingItem}
            isEditing={true}
            categories={categories}
            onSave={handleSave}
            onCancel={() => setEditingItem(null)}
            onDelete={() => handleDelete(editingItem.id)}
          />
        )}
        {eduData.map((item) => (
          <EduItemCard
            key={item.id}
            item={item}
            isEditing={editingItem?.id === item.id}
            categories={categories}
            onEdit={() => setEditingItem(item)}
            onSave={handleSave}
            onCancel={() => setEditingItem(null)}
            onDelete={() => handleDelete(item.id)}
          />
        ))}
      </div>

      {eduData.length === 0 && !editingItem && (
        <div className="empty-state">
          <span className="empty-icon">📚</span>
          <h3>沒有找到相關問答</h3>
          <p>
            {searchTerm || selectedCategory
              ? "請調整搜尋條件或新增問答"
              : "點擊「新增問答」開始建立衛教資源"}
          </p>
        </div>
      )}

      <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translate(-50%, -10px);
          }
          to {
            opacity: 1;
            transform: translate(-50%, 0);
          }
        }

        .education-page {
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
          gap: 12px;
        }

        .filter-section {
          margin-bottom: 24px;
        }

        .edu-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
          gap: 20px;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: var(--muted);
        }

        .empty-icon {
          font-size: 48px;
          display: block;
          margin-bottom: 16px;
          opacity: 0.3;
        }

        .empty-state h3 {
          font-size: 18px;
          font-weight: 500;
          margin-bottom: 8px;
        }

        .empty-state p {
          font-size: 14px;
        }

        .error-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 400px;
        }

        .error-message {
          text-align: center;
          padding: 40px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .error-icon {
          font-size: 48px;
          display: block;
          margin-bottom: 16px;
        }

        .error-message h3 {
          font-size: 20px;
          margin-bottom: 8px;
          color: var(--text);
        }

        .error-message p {
          color: var(--muted);
          margin-bottom: 20px;
        }

        .btn.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }

          .header-actions {
            flex-wrap: wrap;
          }

          .edu-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default EducationPage;
