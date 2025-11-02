import { useNavigate } from "react-router-dom";
import { useLIFF } from "../../../hooks/useLIFF";

const Dashboard = () => {
  const navigate = useNavigate();
  const { profile, isInClient } = useLIFF();

  const menuItems = [
    {
      title: "記錄今日健康數據",
      description: "記錄您今天的健康狀況",
      icon: "❤️",
      color: "#52c41a",
      path: "/liff/daily-metrics",
    },
    {
      title: "紀錄 COPD 量表",
      description: "包含 CAT 健康問卷與 mMRC 呼吸困難評估",
      icon: "📝",
      color: "#1890ff",
      path: "/liff/questionnaire/cat",
    },
    {
      title: "AI 語音助手",
      description: "使用語音與 AI 助手對話",
      icon: "🎙️",
      color: "#722ed1",
      path: "/liff/voice-chat",
    },
  ];

  const quickLinks = [
    { icon: "📱", label: "聯繫醫師" },
    { icon: "📅", label: "預約回診" },
    { icon: "💊", label: "用藥提醒" },
    { icon: "📚", label: "衛教資源" },
  ];

  const handleMenuClick = (path) => {
    navigate(path);
  };

  return (
    <div className="liff-dashboard">
      {/* 用戶資訊區 */}
      <div className="user-section">
        <div className="user-avatar">
          {profile?.pictureUrl ? (
            <img src={profile.pictureUrl} alt="avatar" />
          ) : (
            <div className="avatar-placeholder">👤</div>
          )}
        </div>
        <div className="user-info">
          <h2>{profile?.displayName || "使用者"}</h2>
          <p className="welcome-text">歡迎回來！今天感覺如何？</p>
        </div>
      </div>

      {/* 今日健康狀態 */}
      <div className="health-status">
        <h3>今日健康狀態</h3>
        <div className="status-cards">
          <div className="status-card">
            <span className="status-icon">🌡️</span>
            <span className="status-label">體溫</span>
            <span className="status-value">36.5°C</span>
          </div>
          <div className="status-card">
            <span className="status-icon">💨</span>
            <span className="status-label">血氧</span>
            <span className="status-value">98%</span>
          </div>
          <div className="status-card">
            <span className="status-icon">💊</span>
            <span className="status-label">用藥</span>
            <span className="status-value">已完成</span>
          </div>
        </div>
      </div>

      {/* 功能選單 */}
      <div className="menu-section">
        <h3>健康管理功能</h3>
        <div className="menu-grid">
          {menuItems.map((item, index) => (
            <div
              key={index}
              className="menu-card"
              onClick={() => handleMenuClick(item.path)}
              style={{ borderColor: item.color }}
            >
              <div
                className="menu-icon"
                style={{ backgroundColor: item.color }}
              >
                <span>{item.icon}</span>
              </div>
              <div className="menu-content">
                <h4>{item.title}</h4>
                <p>{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 快速連結 */}
      <div className="quick-links">
        <h3>快速連結</h3>
        <div className="links-grid">
          {quickLinks.map((link, index) => (
            <button key={index} className="quick-link-btn">
              <span className="link-icon">{link.icon}</span>
              <span className="link-label">{link.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* LINE 環境提示 */}
      {isInClient && (
        <div className="line-hint">
          <p>💡 提示：您正在 LINE 應用程式中使用本服務</p>
        </div>
      )}

      <style jsx>{`
        .liff-dashboard {
          padding: 20px;
          max-width: 600px;
          margin: 0 auto;
          background: linear-gradient(135deg, #e9f2ff 0%, #f8f8f8 100%);
          min-height: 100vh;
        }

        .user-section {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          background: white;
          border-radius: 16px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          margin-bottom: 24px;
        }

        .user-avatar {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          overflow: hidden;
          border: 3px solid #7cc6ff;
        }

        .user-avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .avatar-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #e9f2ff;
          font-size: 28px;
        }

        .user-info h2 {
          margin: 0 0 4px 0;
          font-size: 20px;
          color: #2c3e50;
        }

        .welcome-text {
          margin: 0;
          color: #6b7280;
          font-size: 14px;
        }

        .health-status {
          margin-bottom: 24px;
        }

        .health-status h3 {
          font-size: 18px;
          color: #2c3e50;
          margin-bottom: 12px;
        }

        .status-cards {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
        }

        .status-card {
          background: white;
          padding: 12px;
          border-radius: 12px;
          text-align: center;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .status-icon {
          font-size: 24px;
        }

        .status-label {
          font-size: 12px;
          color: #6b7280;
        }

        .status-value {
          font-size: 16px;
          font-weight: 600;
          color: #2c3e50;
        }

        .menu-section {
          margin-bottom: 24px;
        }

        .menu-section h3 {
          font-size: 18px;
          color: #2c3e50;
          margin-bottom: 12px;
        }

        .menu-grid {
          display: grid;
          gap: 16px;
        }

        .menu-card {
          background: white;
          border-radius: 12px;
          padding: 16px;
          border-left: 4px solid;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          cursor: pointer;
          transition: all 200ms;
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .menu-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }

        .menu-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0.9;
          flex-shrink: 0;
        }

        .menu-icon span {
          font-size: 24px;
        }

        .menu-content h4 {
          margin: 0 0 4px 0;
          font-size: 16px;
          color: #2c3e50;
        }

        .menu-content p {
          margin: 0;
          font-size: 12px;
          color: #6b7280;
        }

        .quick-links {
          margin-bottom: 24px;
        }

        .quick-links h3 {
          font-size: 18px;
          color: #2c3e50;
          margin-bottom: 12px;
        }

        .links-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
        }

        .quick-link-btn {
          background: white;
          border: none;
          padding: 12px 8px;
          border-radius: 12px;
          cursor: pointer;
          transition: all 200ms;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }

        .quick-link-btn:hover {
          background: #7cc6ff;
          color: white;
          transform: translateY(-2px);
        }

        .link-icon {
          font-size: 20px;
        }

        .link-label {
          font-size: 12px;
        }

        .line-hint {
          background: #00c300;
          color: white;
          padding: 12px;
          border-radius: 8px;
          text-align: center;
          margin-top: 24px;
        }

        .line-hint p {
          margin: 0;
          font-size: 14px;
        }

        @media (max-width: 480px) {
          .liff-dashboard {
            padding: 16px;
          }

          .status-cards {
            gap: 8px;
          }

          .links-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
