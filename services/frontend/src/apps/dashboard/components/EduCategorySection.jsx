import React from "react";
import EduItemCard from "./EduItemCard";

// 衛教資源分類展示元件 - 按類別組織顯示衛教內容
const EduCategorySection = ({
  category,
  items,
  onUpdateItem,
  onDeleteItem,
  isExpanded = true,
  onToggleExpand,
}) => {
  return (
    <div className="edu-category-section">
      {/* 分類標題 */}
      <div
        className="category-header"
        onClick={onToggleExpand}
        style={{ cursor: onToggleExpand ? "pointer" : "default" }}
      >
        <div className="category-title">
          {onToggleExpand && (
            <span className="expand-icon">{isExpanded ? "📖" : "📕"}</span>
          )}
          <h3>{category}</h3>
        </div>
        <span className="item-count">{items?.length || 0} 篇</span>
      </div>

      {/* 分類內容 */}
      {isExpanded && (
        <div className="category-content">
          {!items || items.length === 0 ? (
            <div className="empty-category">
              <span className="empty-icon">📝</span>
              <p>此分類暫無問答內容</p>
            </div>
          ) : (
            <div className="items-grid">
              {items.map((item, index) => (
                <EduItemCard
                  key={`${category}-${item.id || index}`}
                  item={item}
                  onEdit={() => onUpdateItem?.(item)}
                  onDelete={() => onDeleteItem?.(item)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .edu-category-section {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          margin-bottom: 16px;
          overflow: hidden;
        }

        .category-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          background: linear-gradient(135deg, #f8fafc, #e2e8f0);
          border-bottom: 1px solid #e5e7eb;
          transition: background-color 200ms;
        }

        .category-header:hover {
          background: linear-gradient(135deg, #f1f5f9, #d6dee7);
        }

        .category-title {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .category-title h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #374151;
        }

        .expand-icon {
          font-size: 18px;
          transition: transform 200ms;
        }

        .item-count {
          background: #3b82f6;
          color: white;
          font-size: 12px;
          font-weight: 500;
          padding: 4px 8px;
          border-radius: 12px;
          min-width: 40px;
          text-align: center;
        }

        .category-content {
          padding: 16px;
        }

        .empty-category {
          text-align: center;
          padding: 32px;
          color: #6b7280;
        }

        .empty-category .empty-icon {
          font-size: 24px;
          margin-bottom: 8px;
          display: block;
        }

        .empty-category p {
          margin: 0;
          font-size: 14px;
        }

        .items-grid {
          display: grid;
          gap: 12px;
        }

        @media (max-width: 768px) {
          .category-header {
            padding: 12px 16px;
          }

          .category-title h3 {
            font-size: 14px;
          }

          .category-content {
            padding: 12px;
          }

          .empty-category {
            padding: 24px;
          }
        }
      `}</style>
    </div>
  );
};

export default EduCategorySection;
