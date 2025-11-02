import dayjs from "dayjs";
import { RISK_LEVELS } from "../../../shared/config";

const PatientListPane = ({ patient, onClick }) => {
  // 判斷風險等級
  const getRiskLevel = (cat, mmrc) => {
    if (cat >= 20 || mmrc >= 2) return "high";
    if (cat >= 10 || mmrc >= 1) return "medium";
    return "low";
  };

  const riskLevel = getRiskLevel(patient.cat_score, patient.mmrc_score);
  const riskConfig = {
    high: { label: "高風險", color: "#E66A6A", bg: "#FEE2E2" },
    medium: { label: "中風險", color: "#FAAD14", bg: "#FEF3C7" },
    low: { label: "低風險", color: "#52C41A", bg: "#F0FDF4" },
  };

  const risk = riskConfig[riskLevel];

  // 判斷依從性
  const getAdherenceStatus = (rate) => {
    if (rate >= 0.8) return { label: "良好", color: "#52C41A" };
    if (rate >= 0.6) return { label: "尚可", color: "#FAAD14" };
    return { label: "不佳", color: "#E66A6A" };
  };

  const adherence = getAdherenceStatus(patient.adherence_rate || 0);

  return (
    <div className="patient-card" onClick={onClick}>
      {/* 頭部資訊 */}
      <div className="card-header">
        <div className="patient-info">
          <h3 className="patient-name">{patient.name}</h3>
          <div className="patient-meta">
            <span>{patient.age}歲</span>
            <span>•</span>
            <span>{patient.gender === "M" ? "男" : "女"}</span>
            <span>•</span>
            <span>{patient.phone}</span>
          </div>
        </div>
        <div
          className="risk-badge"
          style={{ background: risk.bg, color: risk.color }}
        >
          {risk.label}
        </div>
      </div>

      {/* 指標區 */}
      <div className="metrics-row">
        <div className="metric">
          <span className="metric-label">CAT</span>
          <span className="metric-value">{patient.cat_score}</span>
        </div>
        <div className="metric">
          <span className="metric-label">mMRC</span>
          <span className="metric-value">{patient.mmrc_score}</span>
        </div>
        <div className="metric">
          <span className="metric-label">依從率</span>
          <span className="metric-value" style={{ color: adherence.color }}>
            {Math.round((patient.adherence_rate || 0) * 100)}%
          </span>
        </div>
      </div>

      {/* 底部資訊 */}
      <div className="card-footer">
        <div className="footer-item">
          <span className="footer-label">最近就診</span>
          <span className="footer-value">
            {patient.last_visit
              ? dayjs(patient.last_visit).format("MM/DD")
              : "無紀錄"}
          </span>
        </div>
        <div className="footer-item">
          <span className="footer-label">建檔時間</span>
          <span className="footer-value">
            {dayjs(patient.created_at).format("YYYY/MM/DD")}
          </span>
        </div>
      </div>

      <style jsx>{`
        .patient-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          transition: all 200ms;
          cursor: pointer;
        }

        .patient-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
        }

        .patient-info {
          flex: 1;
        }

        .patient-name {
          font-size: 18px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 4px 0;
        }

        .patient-meta {
          display: flex;
          gap: 8px;
          font-size: 14px;
          color: var(--muted);
        }

        .risk-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
        }

        .metrics-row {
          display: flex;
          justify-content: space-around;
          padding: 16px 0;
          border-top: 1px solid #f3f4f6;
          border-bottom: 1px solid #f3f4f6;
          margin: 16px 0;
        }

        .metric {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .metric-label {
          font-size: 12px;
          color: var(--muted);
          text-transform: uppercase;
        }

        .metric-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--text);
        }

        .card-footer {
          display: flex;
          justify-content: space-between;
        }

        .footer-item {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .footer-label {
          font-size: 11px;
          color: var(--muted);
        }

        .footer-value {
          font-size: 13px;
          color: var(--text);
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default PatientListPane;
