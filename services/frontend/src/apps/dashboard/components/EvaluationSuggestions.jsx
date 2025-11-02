const EvaluationSuggestions = ({ kpis, profile }) => {
  // 根據 KPI 生成建議
  const generateSuggestions = () => {
    const suggestions = [];

    // CAT 分數建議
    if (kpis?.cat_latest >= 20) {
      suggestions.push({
        type: "danger",
        icon: "⚠️",
        title: "CAT 分數偏高",
        content: "建議安排門診評估，考慮調整用藥或增加肺復健頻率。",
      });
    } else if (kpis?.cat_latest >= 10) {
      suggestions.push({
        type: "warning",
        icon: "📊",
        title: "CAT 分數需關注",
        content: "症狀有輕微影響，建議持續追蹤並加強衛教。",
      });
    }

    // mMRC 建議
    if (kpis?.mmrc_latest >= 2) {
      suggestions.push({
        type: "danger",
        icon: "🫁",
        title: "呼吸困難程度增加",
        content: "日常活動受限明顯，建議評估氧氣治療需求。",
      });
    }

    // 依從性建議
    if (kpis?.adherence_7d < 0.6) {
      suggestions.push({
        type: "danger",
        icon: "💊",
        title: "用藥依從性不佳",
        content: "近7日用藥依從率低於60%，建議加強用藥指導與提醒。",
      });
    } else if (kpis?.adherence_7d < 0.8) {
      suggestions.push({
        type: "warning",
        icon: "💊",
        title: "用藥依從性待改善",
        content: "建議了解用藥障礙，提供個別化衛教。",
      });
    }

    // 回報頻率建議
    if (kpis?.last_report_days > 7) {
      suggestions.push({
        type: "warning",
        icon: "📅",
        title: "超過一週未回報",
        content: "建議主動聯繫病患，了解健康狀況。",
      });
    }

    // 如果都很好
    if (suggestions.length === 0) {
      suggestions.push({
        type: "success",
        icon: "✅",
        title: "狀況良好",
        content: "各項指標表現良好，請持續保持。",
      });
    }

    return suggestions;
  };

  const suggestions = generateSuggestions();

  const getTypeStyles = (type) => {
    switch (type) {
      case "danger":
        return { bg: "#FEE2E2", border: "#E66A6A", icon: "#DC2626" };
      case "warning":
        return { bg: "#FEF3C7", border: "#FAAD14", icon: "#D97706" };
      case "success":
        return { bg: "#F0FDF4", border: "#52C41A", icon: "#16A34A" };
      default:
        return { bg: "#F9FAFB", border: "#E5E7EB", icon: "#6B7280" };
    }
  };

  return (
    <div className="suggestions-card">
      <h3 className="card-title">智慧評估建議</h3>
      <div className="suggestions-list">
        {suggestions.map((suggestion, index) => {
          const styles = getTypeStyles(suggestion.type);
          return (
            <div
              key={index}
              className="suggestion-item"
              style={{
                background: styles.bg,
                borderLeft: `4px solid ${styles.border}`,
              }}
            >
              <div className="suggestion-header">
                <span
                  className="suggestion-icon"
                  style={{ color: styles.icon }}
                >
                  {suggestion.icon}
                </span>
                <span className="suggestion-title">{suggestion.title}</span>
              </div>
              <p className="suggestion-content">{suggestion.content}</p>
            </div>
          );
        })}
      </div>

      {/* 行動建議 */}
      <div className="action-section">
        <h4 className="section-title">建議行動</h4>
        <div className="action-buttons">
          <button className="action-btn primary">
            <span>📞</span> 聯繫病患
          </button>
          <button className="action-btn">
            <span>📝</span> 建立任務
          </button>
          <button className="action-btn">
            <span>📊</span> 產生報告
          </button>
        </div>
      </div>

      <style jsx>{`
        .suggestions-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .card-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 16px 0;
        }

        .suggestions-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 20px;
        }

        .suggestion-item {
          padding: 12px;
          border-radius: 8px;
        }

        .suggestion-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 6px;
        }

        .suggestion-icon {
          font-size: 18px;
        }

        .suggestion-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--text);
        }

        .suggestion-content {
          font-size: 13px;
          color: var(--text);
          line-height: 1.5;
          margin: 0;
          padding-left: 26px;
        }

        .action-section {
          padding-top: 16px;
          border-top: 1px solid #f3f4f6;
        }

        .section-title {
          font-size: 13px;
          font-weight: 600;
          color: var(--muted);
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .action-buttons {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid var(--border);
          border-radius: 8px;
          background: white;
          font-size: 13px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
        }

        .action-btn:hover {
          background: #f9fafb;
          transform: translateY(-1px);
        }

        .action-btn.primary {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .action-btn.primary:hover {
          background: #5cb8ff;
        }

        .action-btn span {
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default EvaluationSuggestions;
