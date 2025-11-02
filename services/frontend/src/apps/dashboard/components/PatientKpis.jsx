const PatientKpis = ({ kpis }) => {
  const kpiItems = [
    {
      label: "最新 CAT",
      value: kpis?.cat_latest || 0,
      unit: "分",
      color: "#7CC6FF",
      icon: "📊",
      status:
        kpis?.cat_latest >= 20
          ? "danger"
          : kpis?.cat_latest >= 10
          ? "warning"
          : "success",
    },
    {
      label: "最新 mMRC",
      value: kpis?.mmrc_latest || 0,
      unit: "級",
      color: "#CBA6FF",
      icon: "🫁",
      status:
        kpis?.mmrc_latest >= 2
          ? "danger"
          : kpis?.mmrc_latest >= 1
          ? "warning"
          : "success",
    },
    {
      label: "7日用藥依從",
      value: Math.round((kpis?.adherence_7d || 0) * 100),
      unit: "%",
      color: "#52C41A",
      icon: "💊",
      status:
        kpis?.adherence_7d >= 0.8
          ? "success"
          : kpis?.adherence_7d >= 0.6
          ? "warning"
          : "danger",
    },
    {
      label: "7日回報率",
      value: Math.round((kpis?.report_rate_7d || 0) * 100),
      unit: "%",
      color: "#5CDBD3",
      icon: "📝",
      status:
        kpis?.report_rate_7d >= 0.8
          ? "success"
          : kpis?.report_rate_7d >= 0.6
          ? "warning"
          : "danger",
    },
    {
      label: "完成度",
      value: Math.round((kpis?.completion_7d || 0) * 100),
      unit: "%",
      color: "#95DE64",
      icon: "✅",
      status:
        kpis?.completion_7d >= 0.8
          ? "success"
          : kpis?.completion_7d >= 0.6
          ? "warning"
          : "danger",
    },
    {
      label: "距最近回報",
      value: kpis?.last_report_days || 0,
      unit: "天",
      color:
        kpis?.last_report_days <= 3
          ? "#52C41A"
          : kpis?.last_report_days <= 7
          ? "#FAAD14"
          : "#E66A6A",
      icon: "📅",
      status:
        kpis?.last_report_days <= 3
          ? "success"
          : kpis?.last_report_days <= 7
          ? "warning"
          : "danger",
    },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case "success":
        return "#52C41A";
      case "warning":
        return "#FAAD14";
      case "danger":
        return "#E66A6A";
      default:
        return "#6B7280";
    }
  };

  return (
    <div className="kpis-card">
      <h3 className="card-title">關鍵指標</h3>
      <div className="kpi-grid">
        {kpiItems.map((item) => (
          <div key={item.label} className="kpi-item">
            <div className="kpi-header">
              <span className="kpi-icon">{item.icon}</span>
              <span className="kpi-label">{item.label}</span>
            </div>
            <div className="kpi-value-row">
              <span
                className="kpi-value"
                style={{ color: getStatusColor(item.status) }}
              >
                {item.value}
              </span>
              <span className="kpi-unit">{item.unit}</span>
            </div>
            <div className="kpi-indicator">
              <div className="indicator-bar">
                <div
                  className="indicator-fill"
                  style={{
                    width: `${Math.min(item.value, 100)}%`,
                    background: getStatusColor(item.status),
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .kpis-card {
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

        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .kpi-item {
          padding: 12px;
          background: #f9fafb;
          border-radius: 12px;
          transition: all 200ms;
        }

        .kpi-item:hover {
          background: #f3f4f6;
          transform: translateY(-1px);
        }

        .kpi-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 8px;
        }

        .kpi-icon {
          font-size: 16px;
        }

        .kpi-label {
          font-size: 12px;
          color: var(--muted);
          font-weight: 500;
        }

        .kpi-value-row {
          display: flex;
          align-items: baseline;
          gap: 4px;
          margin-bottom: 8px;
        }

        .kpi-value {
          font-size: 24px;
          font-weight: 700;
        }

        .kpi-unit {
          font-size: 12px;
          color: var(--muted);
        }

        .kpi-indicator {
          margin-top: 8px;
        }

        .indicator-bar {
          height: 4px;
          background: #e5e7eb;
          border-radius: 2px;
          overflow: hidden;
        }

        .indicator-fill {
          height: 100%;
          transition: width 300ms ease;
        }
      `}</style>
    </div>
  );
};

export default PatientKpis;
