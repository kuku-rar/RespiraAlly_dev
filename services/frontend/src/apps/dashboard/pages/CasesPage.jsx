import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePatients } from "../../../shared/api/hooks";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";
import PatientListPane from "../components/PatientListPane";
import dayjs from "dayjs";

const CasesPage = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [sortBy, setSortBy] = useState("name");

  // 取得病患列表
  const { data: patients = [], isLoading } = usePatients({
    q: searchTerm,
    risk: riskFilter,
  });

  // 排序病患
  const sortedPatients = [...patients].sort((a, b) => {
    switch (sortBy) {
      case "name":
        return a.name?.localeCompare(b.name);
      case "risk":
        return b.cat_score - a.cat_score;
      case "adherence":
        return a.adherence_rate - b.adherence_rate;
      case "lastVisit":
        return dayjs(b.last_visit).diff(dayjs(a.last_visit));
      default:
        return 0;
    }
  });

  const handlePatientClick = (patientId) => {
    navigate(`/dashboard/cases/${patientId}`);
  };

  if (isLoading) {
    return <LoadingSpinner fullScreen message="載入病患列表..." />;
  }

  return (
    <div className="cases-page">
      {/* 頁面標題與操作 */}
      <div className="page-header">
        <div className="header-left">
          <h2 className="page-title">病患個案管理</h2>
          <p className="page-subtitle">共 {patients.length} 位病患</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-primary">
            <span>➕</span> 新增病患
          </button>
        </div>
      </div>

      {/* 篩選工具列 */}
      <div className="filter-bar">
        <div className="search-box">
          <input
            type="text"
            className="input"
            placeholder="搜尋病患姓名、病歷號..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <select
            className="select"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="">所有風險等級</option>
            <option value="high">高風險</option>
            <option value="medium">中風險</option>
            <option value="low">低風險</option>
          </select>

          <select
            className="select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">按姓名排序</option>
            <option value="risk">按風險等級排序</option>
            <option value="adherence">按依從性排序</option>
            <option value="lastVisit">按最近就診排序</option>
          </select>
        </div>
      </div>

      {/* 病患列表 */}
      <div className="patient-grid">
        {sortedPatients.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">👥</span>
            <h3>沒有找到病患</h3>
            <p>請調整搜尋條件或新增病患</p>
          </div>
        ) : (
          sortedPatients.map((patient) => (
            <PatientListPane
              key={patient.id}
              patient={patient}
              onClick={() => handlePatientClick(patient.id)}
            />
          ))
        )}
      </div>

      <style jsx>{`
        .cases-page {
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

        .filter-bar {
          display: flex;
          gap: 16px;
          margin-bottom: 24px;
          padding: 16px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .search-box {
          flex: 1;
        }

        .search-box .input {
          width: 100%;
        }

        .filter-group {
          display: flex;
          gap: 12px;
        }

        .patient-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 20px;
        }

        .empty-state {
          grid-column: 1 / -1;
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

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }

          .filter-bar {
            flex-direction: column;
          }

          .filter-group {
            flex-direction: column;
          }

          .patient-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default CasesPage;
