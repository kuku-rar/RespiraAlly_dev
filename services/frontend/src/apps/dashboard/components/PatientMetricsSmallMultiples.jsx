import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { CHART_COLORS } from "../../../shared/config";
import dayjs from "dayjs";

const PatientMetricsSmallMultiples = ({ metrics = [] }) => {
  // 準備各指標的資料
  const prepareChartData = (key, label, unit) => {
    return metrics.map((m) => ({
      date: dayjs(m.date).format("MM/DD"),
      value: m[key] || 0,
      label,
      unit,
    }));
  };

  const charts = [
    {
      title: "飲水量",
      data: prepareChartData("water_cc", "飲水量", "cc"),
      color: CHART_COLORS.water,
      domain: [0, 3000],
    },
    {
      title: "用藥",
      data: prepareChartData("medication_taken", "用藥", ""),
      color: CHART_COLORS.medication,
      domain: [0, 1],
      formatter: (v) => (v ? "✓" : "✗"),
    },
    {
      title: "運動時間",
      data: prepareChartData("exercise_minutes", "運動", "分鐘"),
      color: CHART_COLORS.exercise,
      domain: [0, 60],
    },
    {
      title: "抽菸量",
      data: prepareChartData("cigarettes", "抽菸", "支"),
      color: CHART_COLORS.cigarettes,
      domain: [0, 20],
    },
  ];

  return (
    <div className="small-multiples">
      {charts.map((chart) => (
        <div key={chart.title} className="chart-item">
          <h4 className="chart-title">{chart.title}</h4>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart
              data={chart.data}
              margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
              />
              <YAxis
                domain={chart.domain}
                tick={{ fontSize: 10 }}
                tickFormatter={chart.formatter}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #E5E7EB",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                formatter={(value, name) => [
                  chart.formatter ? chart.formatter(value) : value,
                  chart.data[0]?.label,
                ]}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={chart.color}
                strokeWidth={2}
                dot={{ fill: chart.color, r: 2 }}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}

      <style jsx>{`
        .small-multiples {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
        }

        .chart-item {
          background: #f9fafb;
          border-radius: 12px;
          padding: 12px;
        }

        .chart-title {
          font-size: 13px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 8px 0;
        }

        @media (max-width: 768px) {
          .small-multiples {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default PatientMetricsSmallMultiples;
