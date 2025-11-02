import { useState } from "react";
import HealthOverviewTab from "./HealthOverviewTab";
import UsageOverviewTab from "./UsageOverviewTab";

const OverviewPage = () => {
  const [activeTab, setActiveTab] = useState("health");

  const tabs = [
    {
      key: "health",
      label: "病患健康趨勢總覽",
      icon: "🩺",
      description: "病患健康指標與醫療數據分析",
    },
    {
      key: "usage",
      label: "病患使用應用趨勢",
      icon: "📱",
      description: "用戶登入、互動與功能使用統計",
    },
  ];

  return (
    <div className="overview-page">
      {/* 分頁標籤列 */}
      <div className="tab-navigation">
        <div className="tab-list">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={`tab-button ${activeTab === tab.key ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <div className="tab-content">
                <span className="tab-label">{tab.label}</span>
                <span className="tab-description">{tab.description}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 分頁內容 */}
      <div className="tab-content-area">
        {activeTab === "health" && <HealthOverviewTab />}
        {activeTab === "usage" && <UsageOverviewTab />}
      </div>

      <style jsx>{`
        .overview-page {
          padding: 0;
        }

        .tab-navigation {
          margin-bottom: 32px;
        }

        .tab-header {
          margin-bottom: 24px;
        }

        .page-title {
          font-size: 28px;
          font-weight: 700;
          color: var(--text);
          margin: 0 0 8px 0;
        }

        .page-subtitle {
          font-size: 16px;
          color: var(--muted);
          font-weight: 400;
          margin: 0;
        }

        .tab-list {
          display: flex;
          gap: 16px;
          background: white;
          border-radius: 16px;
          padding: 8px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .tab-button {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px 24px;
          background: transparent;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          transition: all 200ms;
          text-align: left;
        }

        .tab-button:hover {
          background: #f9fafb;
        }

        .tab-button.active {
          background: linear-gradient(135deg, #7cc6ff, #cba6ff);
          color: white;
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(124, 198, 255, 0.3);
        }

        .tab-icon {
          font-size: 32px;
          min-width: 32px;
        }

        .tab-content {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .tab-label {
          font-size: 18px;
          font-weight: 600;
          color: inherit;
        }

        .tab-description {
          font-size: 13px;
          opacity: 0.8;
          color: inherit;
        }

        .tab-content-area {
          min-height: 600px;
        }

        @media (max-width: 768px) {
          .tab-list {
            flex-direction: column;
          }

          .tab-button {
            gap: 12px;
            padding: 16px 20px;
          }

          .tab-icon {
            font-size: 24px;
            min-width: 24px;
          }

          .tab-label {
            font-size: 16px;
          }

          .tab-description {
            font-size: 12px;
          }

          .page-title {
            font-size: 24px;
          }

          .page-subtitle {
            font-size: 14px;
          }
        }
      `}</style>
    </div>
  );
};

export default OverviewPage;
