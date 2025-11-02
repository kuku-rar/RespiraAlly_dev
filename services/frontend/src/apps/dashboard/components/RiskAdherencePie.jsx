import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { CHART_COLORS } from "../../../shared/config";

const RiskAdherencePie = ({ kpis }) => {
  const riskData = [
    {
      name: "高風險",
      value: Math.round((kpis?.high_risk_pct || 0) * 100),
      color: CHART_COLORS.highRisk,
    },
    {
      name: "中低風險",
      value: Math.round((1 - (kpis?.high_risk_pct || 0)) * 100),
      color: "#52C41A",
    },
  ];

  const adherenceData = [
    {
      name: "低依從性",
      value: Math.round((kpis?.low_adherence_pct || 0) * 100),
      color: CHART_COLORS.lowAdherence,
    },
    {
      name: "正常依從",
      value: Math.round((1 - (kpis?.low_adherence_pct || 0)) * 100),
      color: "#52C41A",
    },
  ];

  const CustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize="14"
        fontWeight="600"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div style={{ display: "flex", justifyContent: "space-around" }}>
      {/* 風險分布 */}
      <div style={{ flex: 1 }}>
        <h4
          style={{
            textAlign: "center",
            fontSize: "14px",
            color: "#6B7280",
            marginBottom: "12px",
          }}
        >
          風險等級分布
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={riskData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={CustomLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {riskData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`} />
          </PieChart>
        </ResponsiveContainer>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "16px",
            marginTop: "8px",
          }}
        >
          {riskData.map((item) => (
            <div
              key={item.name}
              style={{ display: "flex", alignItems: "center", gap: "4px" }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  backgroundColor: item.color,
                  borderRadius: "2px",
                }}
              />
              <span style={{ fontSize: "12px", color: "#6B7280" }}>
                {item.name}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 依從性分布 */}
      <div style={{ flex: 1 }}>
        <h4
          style={{
            textAlign: "center",
            fontSize: "14px",
            color: "#6B7280",
            marginBottom: "12px",
          }}
        >
          依從性分布
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={adherenceData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={CustomLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {adherenceData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`} />
          </PieChart>
        </ResponsiveContainer>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "16px",
            marginTop: "8px",
          }}
        >
          {adherenceData.map((item) => (
            <div
              key={item.name}
              style={{ display: "flex", alignItems: "center", gap: "4px" }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  backgroundColor: item.color,
                  borderRadius: "2px",
                }}
              />
              <span style={{ fontSize: "12px", color: "#6B7280" }}>
                {item.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskAdherencePie;
