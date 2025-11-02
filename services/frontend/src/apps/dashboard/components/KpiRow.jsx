const KpiRow = ({ kpis }) => {
  const kpiItems = [
    {
      label: '患者總數',
      value: kpis?.patients_total || 0,
      format: 'number',
      icon: '👥',
      color: 'primary'
    },
    {
      label: '高風險比例',
      value: kpis?.high_risk_pct || 0,
      format: 'percent',
      icon: '⚠️',
      color: 'danger'
    },
    {
      label: '低依從性比例',
      value: kpis?.low_adherence_pct || 0,
      format: 'percent',
      icon: '📉',
      color: 'warning'
    },
    {
      label: 'CAT 平均分數',
      value: kpis?.cat_avg || 0,
      format: 'decimal',
      icon: '📊',
      color: 'info'
    },
    {
      label: 'mMRC 平均分數',
      value: kpis?.mmrc_avg || 0,
      format: 'decimal',
      icon: '🫁',
      color: 'purple'
    }
  ]

  const formatValue = (value, format) => {
    switch (format) {
      case 'percent':
        return `${(value * 100).toFixed(1)}%`
      case 'decimal':
        return value.toFixed(1)
      default:
        return value.toString()
    }
  }

  const getColorClass = (color) => {
    const colors = {
      primary: '#7CC6FF',
      danger: '#E66A6A',
      warning: '#FAAD14',
      info: '#5CDBD3',
      purple: '#CBA6FF'
    }
    return colors[color] || colors.primary
  }

  return (
    <div className="kpi-row">
      {kpiItems.map((item, index) => (
        <div key={index} className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-icon">{item.icon}</span>
            <span className="kpi-label">{item.label}</span>
          </div>
          <div 
            className="kpi-value"
            style={{ color: getColorClass(item.color) }}
          >
            {formatValue(item.value, item.format)}
          </div>
        </div>
      ))}

      <style jsx>{`
        .kpi-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .kpi-card {
          background: white;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
          transition: all 200ms;
        }

        .kpi-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .kpi-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .kpi-icon {
          font-size: 20px;
        }

        .kpi-label {
          font-size: 14px;
          color: var(--muted);
          font-weight: 500;
        }

        .kpi-value {
          font-size: 28px;
          font-weight: 700;
          line-height: 1.2;
        }

        @media (max-width: 768px) {
          .kpi-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}

export default KpiRow
