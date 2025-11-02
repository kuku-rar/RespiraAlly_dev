import { useParams, useNavigate } from "react-router-dom";
import {
  usePatientProfile,
  usePatientMetrics,
  useCatHistory,
  useMmrcHistory,
  usePatientKpis,
} from "../../../shared/api/hooks";
import LoadingSpinner from "../../../shared/components/LoadingSpinner";
import PatientProfileCard from "../components/PatientProfileCard";
import PatientKpis from "../components/PatientKpis";
import PatientMetricsSmallMultiples from "../components/PatientMetricsSmallMultiples";
import TrendCatMmrcChart from "../components/TrendCatMmrcChart";
import EvaluationSuggestions from "../components/EvaluationSuggestions";
import PatientGoals from "../components/PatientGoals";
import dayjs from "dayjs";

const PatientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 取得病患資料
  const { data: profile, isLoading: profileLoading } = usePatientProfile(id);
  const { data: kpis, isLoading: kpisLoading } = usePatientKpis(id);
  const { data: metrics = [], isLoading: metricsLoading } = usePatientMetrics(
    id,
    {
      from: dayjs().subtract(30, "day").format("YYYY-MM-DD"),
      to: dayjs().format("YYYY-MM-DD"),
    }
  );
  const { data: catHistory = [], isLoading: catLoading } = useCatHistory(id);
  const { data: mmrcHistory = [], isLoading: mmrcLoading } = useMmrcHistory(id);

  if (
    profileLoading ||
    kpisLoading ||
    metricsLoading ||
    catLoading ||
    mmrcLoading
  ) {
    return <LoadingSpinner fullScreen message="載入病患資料..." />;
  }

  // 準備圖表資料 - 確保資料是陣列
  const safeCatHistory = Array.isArray(catHistory) ? catHistory : [];
  const safeMmrcHistory = Array.isArray(mmrcHistory) ? mmrcHistory : [];
  
  const trendData = safeCatHistory.map((cat, index) => ({
    date: cat.date,
    cat_avg: cat.score,
    mmrc_avg: safeMmrcHistory[index]?.score || 0,
  }));

  return (
    <div className="patient-detail">
      {/* 頁面標題 */}
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← 返回列表
        </button>
        <h2 className="page-title">個案詳情</h2>
      </div>

      {/* 主要內容區 */}
      <div className="detail-grid">
        {/* 左側 - 基本資料與 KPI */}
        <div className="left-column">
          <PatientProfileCard profile={profile} />
          <PatientKpis kpis={kpis} />
        </div>

        {/* 右側 - 圖表與建議 */}
        <div className="right-column">
          {/* 個人化目標追蹤 */}
          <PatientGoals metrics={metrics} />

          {/* 健康追蹤小倍數 */}
          <div className="chart-card">
            <h3 className="chart-title">四大健康追蹤（近30天）</h3>
            <PatientMetricsSmallMultiples metrics={metrics} />
          </div>

          {/* CAT & mMRC 趨勢 */}
          <div className="chart-card">
            <h3 className="chart-title">CAT & mMRC 趨勢</h3>
            <TrendCatMmrcChart data={trendData} />
          </div>

          {/* 智慧建議 */}
          <EvaluationSuggestions kpis={kpis} profile={profile} />
        </div>
      </div>

      <style jsx>{`
        .patient-detail {
          padding: 0;
        }

        .page-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
        }

        .back-btn {
          background: white;
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 8px 16px;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
        }

        .back-btn:hover {
          background: #f9fafb;
          transform: translateX(-2px);
        }

        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .detail-grid {
          display: grid;
          grid-template-columns: 380px 1fr;
          gap: 24px;
        }

        .left-column {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .right-column {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .chart-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .chart-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 16px;
        }

        @media (max-width: 1280px) {
          .detail-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default PatientDetail;
