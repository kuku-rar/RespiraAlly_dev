import React from "react";
import { useNavigate } from "react-router-dom";

// 病患分組列表元件 - 整合現有 HealthOverviewTab 的病患分組功能
const PatientGroupList = ({
  title,
  icon,
  patients,
  emptyMessage = "目前無符合條件的病患",
  className = "",
}) => {
  const navigate = useNavigate();

  const formatLastReportDays = (days) => {
    if (days === 0) return "今天回報";
    if (days === 1) return "昨天回報";
    return `${days}天前回報`;
  };

  return (
    <div className={`patient-group-card ${className}`}>
      {/* 標題區 - 配合現有 HealthOverviewTab 樣式 */}
      <h3 className="group-title">
        {icon && <span className="group-icon">{icon}</span>}
        {title}
      </h3>

      {/* 病患列表 */}
      <div className="patient-list">
        {!patients || patients.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">✅</span>
            <p>{emptyMessage}</p>
          </div>
        ) : (
          patients.map((patient) => (
            <div
              key={patient.id}
              className="patient-item"
              onClick={() => navigate(`/dashboard/cases/${patient.id}`)}
            >
              <div className="patient-info">
                <span className="patient-name">{patient.name}</span>
                <span className="patient-meta">
                  {patient.cat_score !== undefined &&
                  patient.mmrc_score !== undefined
                    ? `CAT: ${patient.cat_score} | mMRC: ${patient.mmrc_score}`
                    : patient.adherence_rate !== undefined
                    ? `依從率: ${Math.round(
                        (patient.adherence_rate || 0) * 100
                      )}%`
                    : null}
                  {patient.last_report_days !== undefined &&
                    ` | ${formatLastReportDays(patient.last_report_days)}`}
                </span>
              </div>
              {/* 根據病患類型顯示不同的標籤 */}
              {patient.cat_score >= 20 || patient.mmrc_score >= 2 ? (
                <span className="risk-badge high">高風險</span>
              ) : patient.adherence_rate < 0.6 ? (
                <span className="risk-badge warning">需關注</span>
              ) : (
                <span className="risk-badge low">正常</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default PatientGroupList;
