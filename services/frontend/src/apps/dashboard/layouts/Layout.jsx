import { Outlet } from "react-router-dom";
import { useState } from "react";
import SidebarNav from "./SidebarNav";
import Header from "./Header";
import RightPane from "./RightPane";
import { GlobalFiltersContext } from "../contexts/GlobalFiltersContext";

const Layout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPaneVisible, setRightPaneVisible] = useState(true);
  const [rightPaneCollapsed, setRightPaneCollapsed] = useState(false);
  const [globalFilters, setGlobalFilters] = useState({
    quickTimeRange: "month",
    riskFilter: "",
  });

  return (
    <GlobalFiltersContext.Provider value={{ globalFilters, setGlobalFilters }}>
      <div className="app-layout">
        {/* 側邊導航 - 固定位置 */}
        <SidebarNav
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* 主要內容區 */}
        <div
          className={`main-content ${
            sidebarCollapsed ? "sidebar-collapsed" : ""
          } ${
            rightPaneVisible
              ? rightPaneCollapsed
                ? "rightpane-collapsed"
                : "rightpane-visible"
              : ""
          }`}
        >
          {/* 頂部標題列 - 固定位置 */}
          <Header
            onToggleRightPane={() => setRightPaneVisible(!rightPaneVisible)}
            onFiltersChange={setGlobalFilters}
            rightPaneVisible={rightPaneVisible}
          />

          {/* 內容區域 - 可滾動 */}
          <main className="content">
            <Outlet />
          </main>
        </div>

        {/* 右側輔助欄 - 固定位置 */}
        {rightPaneVisible && (
          <RightPane
            collapsed={rightPaneCollapsed}
            onToggle={() => setRightPaneCollapsed(!rightPaneCollapsed)}
          />
        )}
      </div>

      <style jsx>{`
        .app-layout {
          display: flex;
          height: 100vh;
          overflow: hidden;
          position: relative;
        }

        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          margin-left: 240px; /* SidebarNav 寬度 */
          margin-right: 280px; /* RightPane 寬度 */
          transition: margin 200ms ease;
        }

        .main-content.sidebar-collapsed {
          margin-left: 60px;
        }

        .main-content.rightpane-visible {
          margin-right: 280px;
        }

        .main-content.rightpane-collapsed {
          margin-right: 60px;
        }

        .main-content:not(.rightpane-visible):not(.rightpane-collapsed) {
          margin-right: 0;
        }

        .content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
          background: #f8fafc;
        }

        @media (max-width: 1024px) {
          .main-content {
            margin-left: 60px;
            margin-right: 0;
          }
        }

        @media (max-width: 768px) {
          .main-content {
            margin-left: 0;
            margin-right: 0;
          }
        }
      `}</style>
    </GlobalFiltersContext.Provider>
  );
};

export default Layout;
