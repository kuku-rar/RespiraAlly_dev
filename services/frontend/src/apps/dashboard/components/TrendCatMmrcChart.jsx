import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { CHART_COLORS } from "../../../shared/config";
import dayjs from "dayjs";

const TrendCatMmrcChart = ({ data = {}, height = 300 }) => {
  // 從 API 回應中提取實際的趨勢數據
  const catTrends = data?.cat_trends || [];
  const mmrcTrends = data?.mmrc_trends || [];
  
  // 合併 CAT 和 mMRC 趨勢數據
  const mergedData = catTrends.map((catItem, index) => {
    const mmrcItem = mmrcTrends[index] || {};
    return {
      date: catItem.date || mmrcItem.date,
      month: dayjs(catItem.date || mmrcItem.date).format("MM月"),
      cat_avg: Number((catItem.avg_score || 0).toFixed(1)),
      mmrc_avg: Number((mmrcItem.avg_score || 0).toFixed(1)),
    };
  });

  // 格式化資料
  const formattedData = mergedData;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={formattedData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#6B7280" />
        <YAxis
          yAxisId="cat"
          orientation="left"
          domain={[0, 40]}
          label={{
            value: "CAT 分數",
            angle: -90,
            position: "insideLeft",
            style: { fontSize: 12 },
          }}
          tick={{ fontSize: 12 }}
          stroke={CHART_COLORS.cat}
        />
        <YAxis
          yAxisId="mmrc"
          orientation="right"
          domain={[0, 4]}
          label={{
            value: "mMRC 分數",
            angle: 90,
            position: "insideRight",
            style: { fontSize: 12 },
          }}
          tick={{ fontSize: 12 }}
          stroke={CHART_COLORS.mmrc}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "white",
            border: "1px solid #E5E7EB",
            borderRadius: "8px",
          }}
          formatter={(value, name) => [
            value,
            name === "cat_avg" ? "CAT 平均" : "mMRC 平均",
          ]}
        />
        <Legend
          wrapperStyle={{ paddingTop: "10px" }}
          iconType="line"
          formatter={(value) =>
            value === "cat_avg" ? "CAT 平均分數" : "mMRC 平均分數"
          }
        />
        <Line
          yAxisId="cat"
          type="monotone"
          dataKey="cat_avg"
          stroke={CHART_COLORS.cat}
          strokeWidth={2}
          dot={{ fill: CHART_COLORS.cat, r: 4 }}
          activeDot={{ r: 6 }}
        />
        <Line
          yAxisId="mmrc"
          type="monotone"
          dataKey="mmrc_avg"
          stroke={CHART_COLORS.mmrc}
          strokeWidth={2}
          dot={{ fill: CHART_COLORS.mmrc, r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendCatMmrcChart;
