import { useState } from "react";
import { useLocation } from "react-router-dom";
import { usePatients, useAlerts } from "../../../shared/api/hooks";
import { RISK_LEVELS } from "../../../shared/config";

const RightPane = ({ collapsed, onToggle }) => {
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState("");

  // 取得高風險病患
  const { data: patients = [], isLoading } = usePatients({
    risk: "high",
    limit: 10,
  });

  // 取得 AI 通報 - 修復資料格式
  const { data: alertsResponse } = useAlerts();
  const alerts = alertsResponse?.data || [];

  // 過濾病患
  const filteredPatients = patients.filter((p) =>
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 根據路由決定顯示內容
  const showPatientList = location.pathname.includes("/cases");
  const showAlerts = true; // 總是顯示通報

  return (
    <aside className={`right-pane ${collapsed ? "collapsed" : ""}`}>
      {/* 收合/展開按鈕 */}
      <div className="pane-header">
        {!collapsed && <h2 className="pane-main-title">輔助資訊</h2>}
        <button
          className="pane-toggle"
          onClick={onToggle}
          aria-label={collapsed ? "展開右側欄" : "收合右側欄"}
        >
          {collapsed ? "←" : "→"}
        </button>
      </div>

      {/* 主要內容 - 只在未收合時顯示 */}
      {!collapsed && (
        <>
          {/* 病患搜尋 (個案管理頁) */}
          {showPatientList && (
            <div className="pane-section">
              <h3 className="pane-title">快速搜尋</h3>
              <div className="search-box">
                <input
                  type="text"
                  className="input"
                  placeholder="搜尋病患姓名..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* 高風險病患列表 */}
          <div className="pane-section">
            <h3 className="pane-title">
              <span className="title-icon">⚠️</span>
              高風險病患
            </h3>
            {isLoading ? (
              <div className="loading">載入中...</div>
            ) : (
              <ul className="patient-list">
                {filteredPatients.slice(0, 5).map((patient) => (
                  <li key={patient.id} className="patient-item">
                    <div className="patient-info">
                      <div className="patient-name">{patient.name}</div>
                      <div className="patient-meta">
                        CAT: {patient.cat_score} | mMRC: {patient.mmrc_score}
                      </div>
                    </div>
                    <span className="risk-badge high">高風險</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* 低依從性病患 */}
          <div className="pane-section">
            <h3 className="pane-title">
              <span className="title-icon">📉</span>
              低依從性病患
            </h3>
            <ul className="patient-list">
              {patients
                .filter((p) => p.adherence_rate < 0.6)
                .slice(0, 5)
                .map((patient) => (
                  <li key={patient.id} className="patient-item">
                    <div className="patient-info">
                      <div className="patient-name">{patient.name}</div>
                      <div className="patient-meta">
                        依從率: {Math.round(patient.adherence_rate * 100)}%
                      </div>
                    </div>
                    <span className="risk-badge warning">需關注</span>
                  </li>
                ))}
            </ul>
          </div>

          {/* AI 即時通報 */}
          {showAlerts && (
            <div className="pane-section">
              <h3 className="pane-title">
                <span className="title-icon">🤖</span>
                AI 即時通報
              </h3>
              <div className="alerts-container">
                {alerts.length === 0 ? (
                  <div className="empty-state">
                    <span className="empty-icon">🔔</span>
                    <p>目前無新通報</p>
                  </div>
                ) : (
                  <ul className="alert-list">
                    {alerts.map((alert) => (
                      <li
                        key={alert.id}
                        className={`alert-item ${alert.level}`}
                      >
                        <div className="alert-time">
                          {new Date(alert.created_at || alert.ts).toLocaleTimeString("zh-TW", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </div>
                        <div className="alert-message">{alert.message}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </>
      )}

      <style jsx>{`
        .right-pane {
          position: fixed;
          top: 0;
          right: 0;
          width: 280px;
          height: 100vh;
          background: white;
          border-left: 1px solid var(--border);
          padding: 20px;
          overflow-y: auto;
          transition: width 200ms ease;
          z-index: 90;
        }

        .right-pane.collapsed {
          width: 60px;
          padding: 10px;
        }

        .pane-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid var(--border);
        }

        .pane-main-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .pane-toggle {
          background: white;
          border: 1px solid var(--border);
          border-radius: 6px;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 200ms;
          font-size: 14px;
        }

        .pane-toggle:hover {
          background: var(--primary);
          color: white;
        }

        .collapsed .pane-toggle {
          width: 40px;
          height: 40px;
          font-size: 16px;
          margin: 0 auto;
        }

        .pane-section {
          margin-bottom: 24px;
        }

        .pane-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .title-icon {
          font-size: 18px;
        }

        .search-box {
          margin-bottom: 16px;
        }

        .patient-list {
          list-style: none;
        }

        .patient-item {
          padding: 12px;
          background: #f9fafb;
          border-radius: 8px;
          margin-bottom: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: all 200ms;
          cursor: pointer;
        }

        .patient-item:hover {
          background: #f3f4f6;
          transform: translateX(-2px);
        }

        .patient-info {
          flex: 1;
        }

        .patient-name {
          font-weight: 500;
          font-size: 14px;
          color: var(--text);
        }

        .patient-meta {
          font-size: 12px;
          color: var(--muted);
          margin-top: 2px;
        }

        .risk-badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 500;
        }

        .risk-badge.high {
          background: #fee2e2;
          color: #dc2626;
        }

        .risk-badge.warning {
          background: #fef3c7;
          color: #d97706;
        }

        .alert-list {
          list-style: none;
        }

        .alert-item {
          padding: 10px;
          background: #f9fafb;
          border-radius: 8px;
          margin-bottom: 8px;
          border-left: 3px solid transparent;
        }

        .alert-item.warning {
          border-left-color: var(--warning);
          background: #fffbeb;
        }

        .alert-item.info {
          border-left-color: var(--primary);
          background: #eff6ff;
        }

        .alert-time {
          font-size: 11px;
          color: var(--muted);
          margin-bottom: 4px;
        }

        .alert-message {
          font-size: 13px;
          line-height: 1.4;
        }

        .empty-state {
          text-align: center;
          padding: 20px;
          color: var(--muted);
        }

        .empty-icon {
          font-size: 32px;
          opacity: 0.3;
          display: block;
          margin-bottom: 8px;
        }

        .loading {
          text-align: center;
          padding: 20px;
          color: var(--muted);
        }
      `}</style>
    </aside>
  );
};

export default RightPane;
