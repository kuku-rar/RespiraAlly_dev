import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAccessibility } from "../../../shared/contexts/AccessibilityContext";
import bgImageUrl from "@assets/毛玻璃_BG2.png";

// mMRC 呼吸困難量表題目
const MMRC_OPTIONS = [
  {
    grade: 0,
    emoji: "😊",
    title: "Grade 0 - 無呼吸困難",
    description: "只有在劇烈運動時才會感到呼吸困難",
    examples: [
      "跑步、打球等劇烈運動才會喘",
      "日常活動完全正常",
      "爬山、游泳可以正常進行",
    ],
    color: "#52c41a",
  },
  {
    grade: 1,
    emoji: "😐",
    title: "Grade 1 - 輕度呼吸困難",
    description: "在平地快走或走上小斜坡時會感到呼吸困難",
    examples: ["快走會有點喘", "爬緩坡會需要調整呼吸", "但正常速度走路沒問題"],
    color: "#73d13d",
  },
  {
    grade: 2,
    emoji: "😕",
    title: "Grade 2 - 中度呼吸困難",
    description: "平地走路比同齡人慢，或需要停下來休息",
    examples: [
      "走路速度明顯比別人慢",
      "走一段路就要停下來喘氣",
      "無法跟上同齡朋友的步伐",
    ],
    color: "#faad14",
  },
  {
    grade: 3,
    emoji: "😟",
    title: "Grade 3 - 重度呼吸困難",
    description: "平地走約100公尺或幾分鐘後就需要停下來喘氣",
    examples: ["走100公尺就要休息", "走到巷口就會很喘", "日常外出變得困難"],
    color: "#ff7a45",
  },
  {
    grade: 4,
    emoji: "😰",
    title: "Grade 4 - 極重度呼吸困難",
    description: "因呼吸困難無法離開家門，或穿脫衣服時也會喘",
    examples: ["幾乎無法外出", "穿衣服、洗澡都會喘", "日常生活需要他人協助"],
    color: "#ff4d4f",
  },
];

const MMRCForm = () => {
  const navigate = useNavigate();
  const { speak, enableVoice } = useAccessibility();
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const handleSelect = (grade) => {
    setSelectedGrade(grade);
    if (enableVoice) {
      const option = MMRC_OPTIONS[grade];
      speak(`您選擇了 ${option.title}，${option.description}`);
    }
  };

  const handleSubmit = async () => {
    if (selectedGrade === null) {
      showMessage("error", "請選擇一個選項");
      return;
    }

    setIsSubmitting(true);
    try {
      // 取得病患 ID
      const patientId =
        localStorage.getItem("patientId") ||
        sessionStorage.getItem("patientId");

      if (!patientId) {
        throw new Error("找不到病患 ID，請重新登入");
      }

      // 準備 mMRC 問卷資料
      const mmrcData = {
        mmrc_score: selectedGrade,
      };

      // 提交到 API
      const response = await fetch(
        `/api/v1/patients/${patientId}/questionnaires/mmrc`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(mmrcData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "提交失敗");
      }

      showMessage("success", "問卷已提交成功！");

      // 延遲後跳轉
      setTimeout(() => {
        navigate("/liff/questionnaire/thankyou");
      }, 1500);
    } catch (error) {
      console.error("Submit error:", error);
      showMessage("error", error.message || "提交失敗，請重試");
    } finally {
      setIsSubmitting(false);
    }
  };

  const showMessage = (type, content) => {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = content;
    messageDiv.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 12px 24px;
      background: ${type === "error" ? "#ff4d4f" : "#52c41a"};
      color: white;
      border-radius: 8px;
      z-index: 1000;
      animation: slideDown 0.3s ease;
    `;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
  };

  return (
    <div className="mmrc-form-page">
      <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translate(-50%, -20px);
          }
          to {
            opacity: 1;
            transform: translate(-50%, 0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .mmrc-form-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            "PingFang TC", "Microsoft YaHei", sans-serif;
          position: relative;
        }

        .mmrc-form-page::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url(${bgImageUrl}) center/cover;
          opacity: 0.3;
          z-index: 0;
        }

        .container {
          max-width: 100%;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          position: relative;
          z-index: 1;
        }

        .header {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          padding: 16px 20px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
          border-bottom: 1px solid rgba(255, 255, 255, 0.3);
          margin-bottom: 2px;
        }

        .title {
          font-size: 22px;
          font-weight: 700;
          color: #1a365d;
          margin: 0 0 4px 0;
          letter-spacing: -0.5px;
        }

        .subtitle {
          font-size: 14px;
          color: #64748b;
          margin: 0;
          font-weight: 400;
        }

        .instruction-card {
          background: rgba(235, 245, 255, 0.85);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          padding: 12px 20px;
          margin: 16px 20px;
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .instruction-title {
          font-size: 16px;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .instruction-text {
          font-size: 14px;
          color: #475569;
          line-height: 1.5;
        }

        .options-container {
          flex: 1;
          padding: 16px 20px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          overflow-y: auto;
        }

        .option-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          border: 1px solid rgba(226, 232, 240, 0.6);
          border-radius: 12px;
          padding: 16px;
          cursor: pointer;
          transition: all 200ms;
          animation: fadeIn 0.3s ease;
        }

        .option-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
          border-color: #94a3b8;
          background: rgba(255, 255, 255, 0.95);
        }

        .option-card.selected {
          border-color: #3b82f6;
          border-width: 2px;
          background: rgba(235, 245, 255, 0.95);
          box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
        }

        .option-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .option-emoji {
          font-size: 36px;
          min-width: 36px;
        }

        .option-content {
          flex: 1;
        }

        .option-title {
          font-size: 18px;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 4px;
        }

        .option-description {
          font-size: 15px;
          color: #475569;
          line-height: 1.5;
          font-weight: 500;
        }

        .option-badge {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: 700;
          color: white;
          flex-shrink: 0;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          transition: all 200ms;
        }

        .option-card:hover .option-badge {
          transform: scale(1.05);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .option-card.selected .option-badge {
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        .examples-section {
          margin-top: 12px;
          padding: 12px;
          background: rgba(248, 250, 252, 0.6);
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
          border-radius: 6px;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .examples-title {
          font-size: 12px;
          font-weight: 600;
          color: #64748b;
          margin-bottom: 8px;
        }

        .examples-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .example-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          font-size: 13px;
          color: #64748b;
          line-height: 1.4;
        }

        .example-bullet {
          color: #3b82f6;
          font-size: 18px;
          margin-top: -2px;
        }

        /* 確認對話框樣式 */
        .confirm-dialog {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .confirm-content {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 20px;
          padding: 32px;
          max-width: 400px;
          width: 100%;
          text-align: center;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .confirm-title {
          font-size: 24px;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 24px;
        }

        .confirm-grade {
          font-size: 64px;
          margin: 24px 0;
        }

        .confirm-grade-badge {
          display: inline-block;
          width: 80px;
          height: 80px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36px;
          font-weight: 700;
          color: white;
          margin: 0 auto 24px;
        }

        .confirm-description {
          font-size: 18px;
          color: #475569;
          line-height: 1.6;
          margin-bottom: 32px;
        }

        .confirm-buttons {
          display: flex;
          gap: 12px;
        }

        .confirm-btn {
          flex: 1;
          padding: 16px;
          border-radius: 12px;
          font-size: 18px;
          font-weight: 600;
          border: none;
          cursor: pointer;
          transition: all 200ms;
        }

        .confirm-btn.cancel {
          background: #f1f5f9;
          color: #64748b;
        }

        .confirm-btn.submit {
          background: #3b82f6;
          color: white;
        }

        .confirm-btn:hover {
          transform: scale(1.02);
        }

        .button-group {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          padding: 16px 20px;
          border-top: 1px solid rgba(226, 232, 240, 0.5);
          display: flex;
          gap: 12px;
          box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
        }

        .btn {
          flex: 1;
          padding: 14px;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 200ms;
        }

        .btn-secondary {
          background: white;
          color: #64748b;
          border: 2px solid #e2e8f0;
        }

        .btn-secondary:hover {
          background: #f8fafc;
          border-color: #3b82f6;
          color: #3b82f6;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #2563eb;
          transform: scale(1.02);
        }

        .btn-primary:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .voice-btn {
          position: fixed;
          bottom: 80px;
          right: 20px;
          width: 56px;
          height: 56px;
          border-radius: 50%;
          background: white;
          border: none;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          transition: all 200ms;
        }

        .voice-btn:hover {
          transform: scale(1.1);
        }

        @media (max-width: 480px) {
          .option-emoji {
            font-size: 40px;
          }

          .option-title {
            font-size: 20px;
          }

          .option-badge {
            width: 48px;
            height: 48px;
            font-size: 20px;
          }
        }
      `}</style>

      <div className="container">
        {/* 頁面標題 */}
        <div className="header">
          <h1 className="title">呼吸困難評估</h1>
          <p className="subtitle">請選擇最符合您目前狀況的描述</p>
        </div>

        {/* 說明卡片 */}
        <div className="instruction-card">
          <h3 className="instruction-title">
            <span>📋</span>
            <span>評估說明</span>
          </h3>
          <p className="instruction-text">
            請根據您最近一週的感受，選擇最符合的項目。這將幫助我們了解您的呼吸狀況。
          </p>
        </div>

        {/* 選項列表 */}
        <div className="options-container">
          {MMRC_OPTIONS.map((option) => (
            <div
              key={option.grade}
              className={`option-card ${
                selectedGrade === option.grade ? "selected" : ""
              }`}
              onClick={() => handleSelect(option.grade)}
            >
              <div className="option-header">
                <span className="option-emoji">{option.emoji}</span>
                <div className="option-content">
                  <h3 className="option-title">{option.title}</h3>
                  <p className="option-description">{option.description}</p>
                </div>
                <div
                  className="option-badge"
                  style={{ background: option.color }}
                >
                  {option.grade}
                </div>
              </div>

              <div className="examples-section">
                <div className="examples-title">例如：</div>
                <div className="examples-list">
                  {option.examples.map((example, index) => (
                    <div key={index} className="example-item">
                      <span className="example-bullet">•</span>
                      <span>{example}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 按鈕區 */}
        <div className="button-group">
          <button
            className="btn btn-secondary"
            onClick={() => navigate("/liff")}
          >
            返回首頁
          </button>
          <button
            className="btn btn-primary"
            onClick={() => {
              if (selectedGrade !== null) {
                setShowConfirmDialog(true);
              } else {
                showMessage("error", "請選擇一個選項");
              }
            }}
            disabled={selectedGrade === null || isSubmitting}
          >
            {isSubmitting ? "提交中..." : "確認提交"}
          </button>
        </div>
      </div>

      {/* 確認對話框 */}
      {showConfirmDialog && selectedGrade !== null && (
        <div className="confirm-dialog">
          <div className="confirm-content">
            <h2 className="confirm-title">確認您的選擇</h2>
            <div className="confirm-grade">
              {MMRC_OPTIONS[selectedGrade].emoji}
            </div>
            <div
              className="confirm-grade-badge"
              style={{ background: MMRC_OPTIONS[selectedGrade].color }}
            >
              {selectedGrade}
            </div>
            <p className="confirm-description">
              <strong>{MMRC_OPTIONS[selectedGrade].title}</strong>
              <br />
              {MMRC_OPTIONS[selectedGrade].description}
            </p>
            <div className="confirm-buttons">
              <button
                className="confirm-btn cancel"
                onClick={() => setShowConfirmDialog(false)}
              >
                返回修改
              </button>
              <button
                className="confirm-btn submit"
                onClick={() => {
                  setShowConfirmDialog(false);
                  handleSubmit();
                }}
                disabled={isSubmitting}
              >
                {isSubmitting ? "提交中..." : "確認提交"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 語音按鈕 */}
      {enableVoice && (
        <button
          className="voice-btn"
          onClick={() => speak("請選擇最符合您呼吸狀況的選項")}
          aria-label="播放說明"
        >
          🔊
        </button>
      )}
    </div>
  );
};

export default MMRCForm;
