import { useState } from "react";
import { useAuth } from "../../../shared/contexts/AuthContext";
import { useTheme } from "../../../shared/contexts/ThemeContext";

const SettingsPage = () => {
  const { user, logout } = useAuth();
  const { theme, fontSize, toggleTheme, changeFontSize } = useTheme();

  const [activeTab, setActiveTab] = useState("display");

  const fontSizeOptions = [
    { value: "small", label: "小", size: "14px" },
    { value: "normal", label: "標準", size: "16px" },
    { value: "large", label: "大", size: "18px" },
    { value: "xlarge", label: "特大", size: "20px" },
  ];

  const handleLogout = () => {
    if (window.confirm("確定要登出嗎？")) {
      logout();
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h2 className="page-title">系統設定</h2>
        <p className="page-subtitle">管理您的個人偏好與帳戶設定</p>
      </div>

      {/* 設定分頁 */}
      <div className="settings-tabs">
        <button
          className={`tab-btn ${activeTab === "display" ? "active" : ""}`}
          onClick={() => setActiveTab("display")}
        >
          <span className="tab-icon">🎨</span>
          顯示設定
        </button>
        <button
          className={`tab-btn ${activeTab === "account" ? "active" : ""}`}
          onClick={() => setActiveTab("account")}
        >
          <span className="tab-icon">👤</span>
          帳戶管理
        </button>
        <button
          className={`tab-btn ${activeTab === "notification" ? "active" : ""}`}
          onClick={() => setActiveTab("notification")}
        >
          <span className="tab-icon">🔔</span>
          通知設定
        </button>
      </div>

      {/* 顯示設定 */}
      {activeTab === "display" && (
        <div className="settings-content">
          <div className="settings-section">
            <h3>介面主題</h3>
            <div className="theme-selector">
              <div
                className={`theme-option ${theme === "light" ? "active" : ""}`}
                onClick={() => theme === "dark" && toggleTheme()}
              >
                <div className="theme-preview light-preview">
                  <div className="preview-header"></div>
                  <div className="preview-content"></div>
                </div>
                <span>淺色模式</span>
              </div>
              <div
                className={`theme-option ${theme === "dark" ? "active" : ""}`}
                onClick={() => theme === "light" && toggleTheme()}
              >
                <div className="theme-preview dark-preview">
                  <div className="preview-header"></div>
                  <div className="preview-content"></div>
                </div>
                <span>深色模式</span>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>字級大小</h3>
            <div className="font-size-selector">
              {fontSizeOptions.map((option) => (
                <button
                  key={option.value}
                  className={`font-size-btn ${
                    fontSize === option.value ? "active" : ""
                  }`}
                  onClick={() => changeFontSize(option.value)}
                  style={{ fontSize: option.size }}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <div
              className="preview-text"
              style={{
                fontSize: fontSizeOptions.find((o) => o.value === fontSize)
                  ?.size,
              }}
            >
              預覽文字：這是範例文字，用來展示不同字級大小的效果。
            </div>
          </div>

          <div className="settings-section">
            <h3>介面密度</h3>
            <div className="density-options">
              <label className="radio-option">
                <input type="radio" name="density" value="compact" />
                <span>緊湊</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  name="density"
                  value="normal"
                  defaultChecked
                />
                <span>標準</span>
              </label>
              <label className="radio-option">
                <input type="radio" name="density" value="comfortable" />
                <span>寬鬆</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* 帳戶管理 */}
      {activeTab === "account" && (
        <div className="settings-content">
          <div className="settings-section">
            <h3>個人資訊</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>帳號</label>
                <div className="info-value">
                  {user?.account || "therapist_01"}
                </div>
              </div>
              <div className="info-item">
                <label>姓名</label>
                <div className="info-value">
                  {user?.first_name} {user?.last_name}
                </div>
              </div>
              <div className="info-item">
                <label>角色</label>
                <div className="info-value">
                  {user?.is_staff ? "治療師" : "一般使用者"}
                </div>
              </div>
              <div className="info-item">
                <label>加入日期</label>
                <div className="info-value">2024-01-15</div>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>密碼設定</h3>
            <button className="btn btn-secondary">
              <span>🔐</span> 修改密碼
            </button>
          </div>

          <div className="settings-section">
            <h3>雙重驗證</h3>
            <div className="two-factor">
              <p>增加額外的安全層，保護您的帳戶</p>
              <button className="btn btn-secondary">
                <span>🔒</span> 啟用雙重驗證
              </button>
            </div>
          </div>

          <div className="settings-section danger-zone">
            <h3>危險區域</h3>
            <button className="btn btn-danger" onClick={handleLogout}>
              <span>🚪</span> 登出帳戶
            </button>
          </div>
        </div>
      )}

      {/* 通知設定 */}
      {activeTab === "notification" && (
        <div className="settings-content">
          <div className="settings-section">
            <h3>通知偏好</h3>
            <div className="notification-options">
              <label className="switch-option">
                <input type="checkbox" defaultChecked />
                <span className="switch-label">高風險病患警示</span>
                <span className="switch-desc">
                  當病患健康數據出現異常時通知
                </span>
              </label>
              <label className="switch-option">
                <input type="checkbox" defaultChecked />
                <span className="switch-label">任務提醒</span>
                <span className="switch-desc">即將到期的任務提醒</span>
              </label>
              <label className="switch-option">
                <input type="checkbox" />
                <span className="switch-label">系統更新</span>
                <span className="switch-desc">系統功能更新與維護通知</span>
              </label>
              <label className="switch-option">
                <input type="checkbox" defaultChecked />
                <span className="switch-label">病患訊息</span>
                <span className="switch-desc">來自病患的訊息與回饋</span>
              </label>
            </div>
          </div>

          <div className="settings-section">
            <h3>通知頻道</h3>
            <div className="channel-options">
              <label className="checkbox-option">
                <input type="checkbox" defaultChecked />
                <span>系統內通知</span>
              </label>
              <label className="checkbox-option">
                <input type="checkbox" />
                <span>Email 通知</span>
              </label>
              <label className="checkbox-option">
                <input type="checkbox" />
                <span>LINE 通知</span>
              </label>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .settings-page {
          padding: 0;
        }

        .page-header {
          margin-bottom: 24px;
        }

        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 8px 0;
        }

        .page-subtitle {
          font-size: 14px;
          color: var(--muted);
          margin: 0;
        }

        .settings-tabs {
          display: flex;
          gap: 16px;
          margin-bottom: 24px;
          border-bottom: 1px solid var(--border);
        }

        .tab-btn {
          background: none;
          border: none;
          padding: 12px 16px;
          cursor: pointer;
          color: var(--muted);
          font-size: 14px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          border-bottom: 2px solid transparent;
          transition: all 200ms;
        }

        .tab-btn:hover {
          color: var(--text);
        }

        .tab-btn.active {
          color: var(--primary);
          border-bottom-color: var(--primary);
        }

        .tab-icon {
          font-size: 18px;
        }

        .settings-content {
          max-width: 800px;
        }

        .settings-section {
          background: white;
          padding: 24px;
          border-radius: 12px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .settings-section h3 {
          font-size: 18px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 16px 0;
        }

        /* 主題選擇器 */
        .theme-selector {
          display: flex;
          gap: 20px;
        }

        .theme-option {
          cursor: pointer;
          text-align: center;
          transition: all 200ms;
        }

        .theme-option.active {
          transform: scale(1.05);
        }

        .theme-preview {
          width: 120px;
          height: 80px;
          border-radius: 8px;
          border: 2px solid transparent;
          overflow: hidden;
          margin-bottom: 8px;
        }

        .theme-option.active .theme-preview {
          border-color: var(--primary);
        }

        .light-preview {
          background: white;
          border: 1px solid #e5e7eb;
        }

        .dark-preview {
          background: #1f2937;
          border: 1px solid #374151;
        }

        .preview-header {
          height: 20px;
          background: currentColor;
          opacity: 0.1;
        }

        .preview-content {
          margin: 8px;
          height: 40px;
          background: currentColor;
          opacity: 0.05;
          border-radius: 4px;
        }

        /* 字級選擇器 */
        .font-size-selector {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .font-size-btn {
          padding: 8px 16px;
          background: white;
          border: 1px solid var(--border);
          border-radius: 8px;
          cursor: pointer;
          transition: all 200ms;
        }

        .font-size-btn:hover {
          border-color: var(--primary);
        }

        .font-size-btn.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .preview-text {
          padding: 12px;
          background: var(--bg-secondary);
          border-radius: 8px;
          color: var(--text);
        }

        /* 選項樣式 */
        .radio-option,
        .checkbox-option {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          cursor: pointer;
        }

        .switch-option {
          display: block;
          padding: 12px 0;
          border-bottom: 1px solid var(--border);
          cursor: pointer;
        }

        .switch-option:last-child {
          border-bottom: none;
        }

        .switch-label {
          font-weight: 500;
          display: block;
          margin-bottom: 4px;
        }

        .switch-desc {
          font-size: 12px;
          color: var(--muted);
        }

        /* 資訊網格 */
        .info-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
        }

        .info-item label {
          display: block;
          font-size: 12px;
          color: var(--muted);
          margin-bottom: 4px;
        }

        .info-value {
          font-size: 16px;
          font-weight: 500;
          color: var(--text);
        }

        /* 按鈕樣式 */
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 200ms;
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .btn-secondary {
          background: var(--bg-secondary);
          color: var(--text);
        }

        .btn-secondary:hover {
          background: var(--border);
        }

        .btn-danger {
          background: #fee2e2;
          color: #dc2626;
        }

        .btn-danger:hover {
          background: #fecaca;
        }

        .danger-zone {
          border: 1px solid #fecaca;
          background: #fef2f2;
        }

        .danger-zone h3 {
          color: #dc2626;
        }

        .density-options,
        .channel-options {
          display: flex;
          gap: 20px;
        }

        .notification-options {
          display: flex;
          flex-direction: column;
        }

        @media (max-width: 768px) {
          .settings-tabs {
            overflow-x: auto;
          }

          .info-grid {
            grid-template-columns: 1fr;
          }

          .theme-selector {
            flex-direction: column;
          }

          .density-options,
          .channel-options {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default SettingsPage;
