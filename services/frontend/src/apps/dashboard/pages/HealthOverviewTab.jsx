import { useState, useEffect } from "react";
import {
  useOverviewKpis,
  useOverviewTrends,
  useOverviewAdherence,
  usePatientMetrics,
  usePatients,
} from "../../../shared/api/hooks";
import { useGlobalFilters } from "../contexts/GlobalFiltersContext";
import KpiRow from "../components/KpiRow";
import TrendCatMmrcChart from "../components/TrendCatMmrcChart";
import RiskAdherencePie from "../components/RiskAdherencePie";
import BehaviorAdherenceTrend from "../components/BehaviorAdherenceTrend";
import BehaviorOverviewTrends from "../components/BehaviorOverviewTrends";
import PatientListPane from "../components/PatientListPane";
import PatientGroupList from "../components/PatientGroupList";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";
import dayjs from "dayjs";
import quarterOfYear from "dayjs/plugin/quarterOfYear";

// 啟用季度插件
dayjs.extend(quarterOfYear);

const HealthOverviewTab = () => {
  const { globalFilters } = useGlobalFilters();
  const [localTimeRange, setLocalTimeRange] = useState({
    from: dayjs().startOf("month").format("YYYY-MM-DD"),
    to: dayjs().endOf("month").format("YYYY-MM-DD"),
    range: "month",
  });

  // 當全域時間範圍改變時，同步本地時間範圍
  useEffect(() => {
    const getTimeRangeFromGlobal = (range) => {
      switch (range) {
        case "week":
          return {
            from: dayjs().startOf("week").format("YYYY-MM-DD"),
            to: dayjs().endOf("week").format("YYYY-MM-DD"),
            range: "week",
          };
        case "quarter":
          return {
            from: dayjs().startOf("quarter").format("YYYY-MM-DD"),
            to: dayjs().endOf("quarter").format("YYYY-MM-DD"),
            range: "quarter",
          };
        case "last30days":
          return {
            from: dayjs().subtract(30, "day").format("YYYY-MM-DD"),
            to: dayjs().format("YYYY-MM-DD"),
            range: "custom",
          };
        default: // month
          return {
            from: dayjs().startOf("month").format("YYYY-MM-DD"),
            to: dayjs().endOf("month").format("YYYY-MM-DD"),
            range: "month",
          };
      }
    };

    setLocalTimeRange(getTimeRangeFromGlobal(globalFilters.quickTimeRange));
  }, [globalFilters.quickTimeRange]);

  // 取得總覽資料
  const { data: kpis, isLoading: kpisLoading } = useOverviewKpis();
  const { data: trends, isLoading: trendsLoading } = useOverviewTrends();
  const { data: adherence, isLoading: adherenceLoading } =
    useOverviewAdherence();

  // 取得健康指標數據
  const { data: metricsData = [], isLoading: metricsLoading } =
    usePatientMetrics(null, {
      from: localTimeRange.from,
      to: localTimeRange.to,
      ...(globalFilters.riskFilter && { risk: globalFilters.riskFilter }),
    });

  // 取得病患列表（用於高風險和低依從性列表）
  const { data: allPatients = [], isLoading: patientsLoading } = usePatients({
    ...(globalFilters.riskFilter && { risk: globalFilters.riskFilter }),
  });

  // 確保資料是陣列格式，然後篩選高風險病患和低依從性病患
  const safeAllPatients = Array.isArray(allPatients) ? allPatients : [];
  const safeMetricsData = Array.isArray(metricsData) ? metricsData : [];
  
  const highRiskPatients = safeAllPatients
    .filter((p) => p && (p.cat_score >= 20 || p.mmrc_score >= 2))
    .slice(0, 8);

  const lowAdherencePatients = safeAllPatients
    .filter((p) => p && (p.adherence_rate || 0) <= 0.6)
    .slice(0, 8);

  if (
    kpisLoading ||
    trendsLoading ||
    adherenceLoading ||
    metricsLoading ||
    patientsLoading
  ) {
    return <LoadingSpinner fullScreen message="載入健康數據..." />;
  }

  return (
    <div className="health-overview-tab">
      {/* KPI 卡片區 */}
      <section className="section">
        <KpiRow kpis={kpis} />
      </section>

      {/* 健康指標達標率分析 */}
      <section className="section">
        <div className="section-header">
          <h3 className="section-title">患者健康指標達標率分析</h3>
          <div className="section-subtitle">
            目前顯示：
            {globalFilters.riskFilter
              ? `${
                  globalFilters.riskFilter === "high"
                    ? "高風險"
                    : globalFilters.riskFilter === "medium"
                    ? "中風險"
                    : "低風險"
                }病患`
              : "所有病患"}
          </div>
        </div>
        <BehaviorOverviewTrends
          data={safeMetricsData}
          range={localTimeRange.range}
        />
      </section>

      {/* 圖表區 - 第一排 */}
      <section className="charts-grid">
        <div className="chart-card">
          <h3 className="chart-title">CAT & mMRC 月平均趨勢</h3>
          <TrendCatMmrcChart data={trends} />
        </div>

        <div className="chart-card">
          <h3 className="chart-title">風險與依從性分布</h3>
          <RiskAdherencePie kpis={kpis} />
        </div>
      </section>

      {/* 圖表區 - 第二排：整體依從性趨勢 */}
      <section className="section">
        <div className="chart-card full-width">
          <h3 className="chart-title">四大健康追蹤依從性趨勢（整體）</h3>
          <BehaviorAdherenceTrend
            data={adherence}
            range={localTimeRange.range}
          />
        </div>
      </section>

      {/* 病患族群分析 - 使用新的 PatientGroupList 元件 */}
      <section className="patient-groups-grid">
        <PatientGroupList
          title="高風險族群 (Top 8)"
          icon="⚠️"
          patients={highRiskPatients}
          emptyMessage="目前無高風險病患"
        />

        <PatientGroupList
          title="低依從性族群 (≤60%)"
          icon="📉"
          patients={lowAdherencePatients}
          emptyMessage="目前無低依從性病患"
        />
      </section>

      <style jsx>{`
        .health-overview-tab {
          padding: 0;
        }

        .section {
          margin-bottom: 24px;
        }

        .section-header {
          margin-bottom: 16px;
        }

        .section-title {
          font-size: 20px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 4px;
        }

        .section-subtitle {
          font-size: 14px;
          color: var(--muted);
          font-weight: 500;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          margin-bottom: 24px;
        }

        .chart-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .chart-card.full-width {
          grid-column: 1 / -1;
        }

        .chart-title {
          font-size: 18px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 16px;
        }

        .patient-groups-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
        }

        .patient-group-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .group-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 16px;
        }

        .group-icon {
          font-size: 20px;
        }

        .patient-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .patient-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: #f9fafb;
          border-radius: 8px;
          transition: all 200ms;
        }

        .patient-item:hover {
          background: #f3f4f6;
          transform: translateX(-2px);
        }

        .patient-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .patient-name {
          font-weight: 500;
          font-size: 14px;
          color: var(--text);
        }

        .patient-meta {
          font-size: 12px;
          color: var(--muted);
        }

        .risk-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 500;
        }

        .risk-badge.high {
          background: #fee2e2;
          color: #dc2626;
        }

        .risk-badge.warning {
          background: #fef3c7;
          color: #d97706;
        }

        .empty-state {
          text-align: center;
          padding: 32px 16px;
          color: var(--muted);
        }

        .empty-icon {
          font-size: 32px;
          display: block;
          margin-bottom: 8px;
          opacity: 0.3;
        }

        .empty-state p {
          font-size: 14px;
          margin: 0;
        }

        @media (max-width: 1024px) {
          .charts-grid,
          .patient-groups-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default HealthOverviewTab;
