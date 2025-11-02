import { NavLink } from "react-router-dom";
import { useState } from "react";
import {
  BarChartOutlined,
  HomeOutlined,
  BookOutlined,
  CalendarOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from "@ant-design/icons";

// Import assets
import logoImage from "../../../assets/logo demo2.png";
import backgroundImage from "../../../assets/毛玻璃_BG2.png";

const SidebarNav = ({ collapsed, onToggle }) => {
  const [hoveredItem, setHoveredItem] = useState(null);

  const navItems = [
    {
      path: "/dashboard/overview",
      label: "總  覽",
      icon: <HomeOutlined />,
      description: "整體數據概覽",
    },
    {
      path: "/dashboard/cases",
      label: "個案管理",
      icon: <BarChartOutlined />,
      description: "病患管理與追蹤",
    },
    {
      path: "/dashboard/education",
      label: "衛教知識庫",
      icon: <BookOutlined />,
      description: "COPD 衛教問答",
    },
    {
      path: "/dashboard/tasks",
      label: "日曆排程",
      icon: <CalendarOutlined />,
      description: "任務與排程管理",
    },
    {
      path: "/dashboard/settings",
      label: "設  定",
      icon: <SettingOutlined />,
      description: "系統與個人設定",
    },
  ];


  return (
    <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      {/* Header 區域 */}
      <div className="sidebar-header">
        <div className="logo-container">
          {!collapsed && (
            <div className="logo-section">
              <img
                src={logoImage}
                alt="RespiraAlly Logo"
                className="logo-image"
              />
              <div className="logo-text">RespiraAlly</div>
            </div>
          )}
          {collapsed && (
            <img
              src={logoImage}
              alt="RespiraAlly Logo"
              className="logo-image-collapsed"
            />
          )}
          <button
            className="sidebar-toggle"
            onClick={onToggle}
            aria-label={collapsed ? "展開側邊欄" : "收合側邊欄"}
          >
            {collapsed ? "→" : "←"}
          </button>
        </div>
      </div>

      {/* 導航項目 */}
      <div className="nav-container">
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                onMouseEnter={() => setHoveredItem(item.path)}
                onMouseLeave={() => setHoveredItem(null)}
                style={{ textDecoration: 'none', borderBottom: 'none' }}
              >
                <div className="nav-content">
                  <div className="nav-icon">{item.icon}</div>
                  {!collapsed && (
                    <div className="nav-label">{item.label}</div>
                  )}
                </div>
                {hoveredItem === item.path && collapsed && (
                  <div className="nav-tooltip">{item.description}</div>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>

      {/* 使用者資訊區域 */}
      <div className="sidebar-footer">
        {!collapsed && (
          <div className="user-info">
            <div className="user-avatar">
              <UserOutlined />
            </div>
            <div className="user-details">
              <div className="user-name">Bobo</div>
              <div className="user-role">呼吸治療師</div>
            </div>
          </div>
        )}
        
        {collapsed && (
          <div className="user-avatar-collapsed">
            <UserOutlined />
          </div>
        )}
        
        {/* 登出按鈕 */}
        <div className="logout-section">
          <button className="logout-btn">
            <LogoutOutlined />
            {!collapsed && <span className="logout-text">LOG OUT</span>}
          </button>
        </div>
      </div>

      <style jsx>{`
        .sidebar {
          position: fixed;
          top: 0;
          left: 0;
          width: 240px;
          height: 100vh;
          background: transparent;
          display: flex;
          flex-direction: column;
          transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
          z-index: 100;
          overflow: hidden;
        }

        .sidebar.collapsed {
          width: 70px;
        }

        /* 毛玻璃背景效果 */
        .sidebar::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: url('${backgroundImage}');
          background-color: rgba(255, 255, 255, 0.1);
          background-blend-mode: screen;
          background-size: 1817.51% 246.47%;
          background-position: 4.37% 63.85%;
          background-repeat: no-repeat;
          opacity: 0.56;
          z-index: 1;
        }

        /* Glassmorphism 效果 */
        .sidebar::after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(180deg,
            rgba(189, 244, 237, 0.12) 0%,
            rgba(163, 171, 212, 0.18) 100%
          );
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(20px);
          border-right: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 
            2px 4px 4px 0px rgba(96, 110, 135, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
          z-index: 2;
        }

        /* 內容層 */
        .sidebar > * {
          position: relative;
          z-index: 3;
        }

        .sidebar-header {
          padding: 30px 25px;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100px;
          position: relative;
        }

        .sidebar-toggle {
          position: absolute;
          top: -10px;
          right: -10px;
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid rgba(69, 177, 182, 0.3);
          border-radius: 8px;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
          backdrop-filter: blur(5px);
          color: #45b1b6;
          font-size: 16px;
          z-index: 10;
          box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
        }

        .sidebar-toggle:hover {
          background: #45b1b6;
          color: white;
          transform: scale(1.1);
          box-shadow: 0 4px 4px rgba(69, 177, 182, 0.3);
        }

        .collapsed .sidebar-toggle {
          right: -16px;
        }

        .logo-container {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
        }

        .logo-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }

        .logo-image {
          width: 60px;
          height: 60px;
          object-fit: contain;
          filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15));
        }

        .logo-image-collapsed {
          width: 40px;
          height: 40px;
          object-fit: contain;
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
        }

        .logo-text {
          font-family: 'jf-jinxuan-fresh2.2', 'PingFang TC', sans-serif;
          font-size: 24px;
          font-weight: 400;
          color: #45b1b6;
          letter-spacing: 2.4px;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          text-align: center;
          line-height: 1.2;
        }

        .nav-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: 20px 0;
          overflow-y: auto;
        }

        .nav-list {
          list-style: none;
          margin: 20;
          padding: 20;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .nav-item {
          display: block;
          position: relative;
          margin: 0 4px;
          padding: 4px;
          border-radius: 12px;
          transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
          text-decoration: none;
          border-bottom: none;
        }

        .nav-content {
          display: flex;
          align-items: center;
          padding: 16px 20px;
          position: relative;
          z-index: 2;
          transition: all 300ms ease;
          text-decoration: none;
          border-radius: 12px;
          border: 0 solid rgba(216, 216, 216, 0.00);
        }

        .nav-item.active .nav-content {
          background: radial-gradient(102.17% 215.74% at 12.4% -66.86%, rgba(85, 181, 161, 0.00) 0%, #68AFD3 100%) !important;
          backdrop-filter: blur(20px) !important;
          -webkit-backdrop-filter: blur(20px) !important;
        }

        :global(.nav-item.active) .nav-content {
          background: radial-gradient(102.17% 215.74% at 12.4% -66.86%, rgba(85, 181, 161, 0.00) 0%, #68AFD3 100%) !important;
          backdrop-filter: blur(20px) !important;
          -webkit-backdrop-filter: blur(20px) !important;
        }

        .nav-icon {
          font-size: 24px;
          color: #45b1b6;
          min-width: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 20px;
          transition: all 300ms ease;
          text-decoration: none;
          border: none;
        }

        .collapsed .nav-icon {
          margin-right: 0;
          font-size: 22px;
        }

        .nav-label {
          font-family: 'Inter', 'Noto Sans JP', 'PingFang TC', sans-serif;
          font-weight: 400;
          font-size: 20px;
          color: #45b1b6;
          letter-spacing: 6px;
          white-space: nowrap;
          transition: all 300ms ease;
          text-decoration: none;
          border-bottom: none;
        }

        :global(.nav-item:hover) .nav-content {
          transform: translateX(4px);
        }

        :global(.nav-item.active) .nav-content {
          color: white;
        }

        :global(.nav-item.active) .nav-icon {
          color: white;
        }

        :global(.nav-item.active) .nav-label {
          color: white;
        }


        .active-background {
          display: none;
        }

        @keyframes activeGlow {
          0% {
            opacity: 0;
            transform: scale(0.95);
          }
          100% {
            opacity: 1;
            transform: scale(1);
          }
        }

        .nav-tooltip {
          position: absolute;
          left: calc(100% + 12px);
          top: 50%;
          transform: translateY(-50%);
          background: rgba(0, 0, 0, 0.9);
          color: white;
          padding: 8px 12px;
          border-radius: 8px;
          font-size: 12px;
          white-space: nowrap;
          z-index: 1000;
          pointer-events: none;
          backdrop-filter: blur(10px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .nav-tooltip::before {
          content: '';
          position: absolute;
          left: -6px;
          top: 50%;
          transform: translateY(-50%);
          width: 0;
          height: 0;
          border-top: 6px solid transparent;
          border-bottom: 6px solid transparent;
          border-right: 6px solid rgba(0, 0, 0, 0.9);
        }

        .sidebar-footer {
          padding: 24px 20px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
          padding: 0;
          background: transparent;
          border: none;
          backdrop-filter: none;
        }

        .user-avatar {
          width: 50px;
          height: 50px;
          background: transparent;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: #45b1b6;
          backdrop-filter: none;
          border: none;
          box-shadow: none;
        }

        .user-avatar-collapsed {
          width: 40px;
          height: 40px;
          background: transparent;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: #45b1b6;
          backdrop-filter: none;
          border: none;
          box-shadow: none;
          margin: 0 auto 20px;
        }

        .user-details {
          flex: 1;
        }

        .user-name {
          font-family: 'PingFang TC', sans-serif;
          font-weight: 400;
          font-size: 24px;
          color: #656565;
          letter-spacing: 2.4px;
          margin-bottom: 4px;
          line-height: 1.2;
        }

        .user-role {
          font-family: 'PingFang TC', sans-serif;
          font-weight: 300;
          font-size: 16px;
          color: #7c8788;
          line-height: 1.2;
        }

        .logout-section {
          display: flex;
          justify-content: center;
        }

        .logout-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          background: radial-gradient(
            ellipse at center,
            rgba(189, 244, 237, 0.2) 0%,
            rgba(163, 171, 212, 0.8) 100%
          );
          backdrop-filter: blur(15px);
          -webkit-backdrop-filter: blur(15px);
          border: 1.5px solid rgba(189, 244, 237, 0.6);
          border-radius: 50px;
          padding: 10px 24px;
          color: #515859;
          cursor: pointer;
          transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
          font-family: 'jf-openhuninn-1.0', sans-serif;
          font-size: 10px;
          font-weight: 400;
          letter-spacing: 1px;
          text-transform: uppercase;
          min-height: 36px;
        }

        .logout-btn:hover {
          transform: scale(1.05) translateY(-1px);
          background: radial-gradient(
            ellipse at center,
            rgba(189, 244, 237, 0.4) 0%,
            rgba(163, 171, 212, 1) 100%
          );
          color: white;
          box-shadow: 0 8px 24px rgba(163, 171, 212, 0.4);
          border-color: rgba(189, 244, 237, 0.8);
        }

        .logout-text {
          font-weight: 400;
          line-height: 1;
        }

        .collapsed .nav-content {
          padding: 16px 10px;
          justify-content: center;
        }

        .collapsed .logout-btn {
          padding: 10px;
          border-radius: 50%;
          width: 36px;
          height: 36px;
        }

        .collapsed .logout-text {
          display: none;
        }

        /* 響應式調整 */
        @media (max-height: 900px) {
          .sidebar-header {
            padding: 20px 25px;
            min-height: 80px;
          }
          
          .logo-image {
            width: 50px;
            height: 50px;
          }
          
          .logo-text {
            font-size: 20px;
          }
          
          .nav-content {
            padding: 14px 25px;
          }
          
          .nav-icon {
            font-size: 20px;
          }
          
          .nav-label {
            font-size: 20px;
            letter-spacing: 6px;
          }
        }

        @media (max-height: 700px) {
          .nav-list {
            gap: 8px;
          }
          
          .nav-content {
            padding: 12px 25px;
          }
          
          .sidebar-footer {
            padding: 16px 20px;
          }
        }
      `}</style>
    </nav>
  );
};

export default SidebarNav;
