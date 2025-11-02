import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAccessibility } from "../../../shared/contexts/AccessibilityContext";
import bgImageUrl from "@assets/毛玻璃_BG2.png";

// CAT 問卷題目
const CAT_QUESTIONS = [
  {
    key: "cough_score",
    question: "請問您最近咳嗽的情形？",
    leftText: "完全沒咳嗽",
    rightText: "一直咳不停",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全沒咳嗽\n（整天都沒有）" },
      { value: 1, emoji: "😊", text: "偶爾咳一下\n（一天1~2次）" },
      { value: 2, emoji: "😐", text: "有時會咳\n（不太影響）" },
      { value: 3, emoji: "🙁", text: "常常咳嗽\n（有點困擾）" },
      { value: 4, emoji: "🤢", text: "幾乎每天咳\n（很不舒服）" },
      { value: 5, emoji: "🥵", text: "一直咳不停\n（非常難受）" },
    ],
  },
  {
    key: "phlegm_score",
    question: "您覺得肺裡面有痰卡住嗎？",
    leftText: "完全沒痰",
    rightText: "痰多到呼吸困難",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全沒痰\n（肺部清爽）" },
      { value: 1, emoji: "😊", text: "偶爾卡痰\n（但能排出）" },
      { value: 2, emoji: "😐", text: "有點痰\n（偶爾咳出）" },
      { value: 3, emoji: "🙁", text: "常有痰\n（不舒服）" },
      { value: 4, emoji: "🤢", text: "經常很多痰\n（影響說話）" },
      { value: 5, emoji: "🥵", text: "痰多到呼吸困難" },
    ],
  },
  {
    key: "chest_score",
    question: "您有覺得胸口會悶、會緊嗎？",
    leftText: "完全不悶不緊",
    rightText: "胸悶難受到坐不住",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全不悶不緊\n（呼吸順暢）" },
      { value: 1, emoji: "😊", text: "偶爾輕微悶\n（很快就好）" },
      { value: 2, emoji: "😐", text: "有時會胸悶\n（但還好）" },
      { value: 3, emoji: "🙁", text: "經常胸悶\n（不太舒服）" },
      { value: 4, emoji: "🤢", text: "胸口很緊\n（呼吸費力）" },
      { value: 5, emoji: "🥵", text: "胸悶難受到坐不住" },
    ],
  },
  {
    key: "breathless_score",
    question: "走上坡或爬一層樓梯會喘嗎？",
    leftText: "完全不會喘",
    rightText: "喘到快昏倒",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全不會喘\n（輕鬆自如）" },
      { value: 1, emoji: "😊", text: "輕微喘氣\n（休息就好）" },
      { value: 2, emoji: "😐", text: "有點喘\n（要停一下）" },
      { value: 3, emoji: "🙁", text: "蠻喘的\n（需要休息）" },
      { value: 4, emoji: "🤢", text: "非常喘\n（走不動）" },
      { value: 5, emoji: "🥵", text: "喘到快昏倒" },
    ],
  },
  {
    key: "activities_score",
    question: "肺部狀況有影響您的日常活動嗎？",
    leftText: "完全不影響",
    rightText: "什麼都做不了",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全不影響\n（正常生活）" },
      { value: 1, emoji: "😊", text: "稍微影響\n（但還OK）" },
      { value: 2, emoji: "😐", text: "有些影響\n（要調整）" },
      { value: 3, emoji: "🙁", text: "影響很多\n（很多限制）" },
      { value: 4, emoji: "🤢", text: "嚴重影響\n（做事困難）" },
      { value: 5, emoji: "🥵", text: "什麼都做不了" },
    ],
  },
  {
    key: "confidence_score",
    question: "您會擔心肺部狀況而不敢外出嗎？",
    leftText: "完全不擔心",
    rightText: "根本不敢出門",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "完全不擔心\n（放心外出）" },
      { value: 1, emoji: "😊", text: "偶爾擔心\n（但還是出門）" },
      { value: 2, emoji: "😐", text: "有點擔心\n（會考慮）" },
      { value: 3, emoji: "🙁", text: "蠻擔心的\n（減少外出）" },
      { value: 4, emoji: "🤢", text: "很擔心\n（很少出門）" },
      { value: 5, emoji: "🥵", text: "根本不敢出門" },
    ],
  },
  {
    key: "sleep_score",
    question: "您的睡眠品質如何？",
    leftText: "睡得很好",
    rightText: "完全睡不著",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "睡得很好\n（一覺到天亮）" },
      { value: 1, emoji: "😊", text: "偶爾醒來\n（但能再睡）" },
      { value: 2, emoji: "😐", text: "有時睡不好\n（會醒幾次）" },
      { value: 3, emoji: "🙁", text: "常常睡不好\n（很難入睡）" },
      { value: 4, emoji: "🤢", text: "睡眠很差\n（整夜難眠）" },
      { value: 5, emoji: "🥵", text: "完全睡不著" },
    ],
  },
  {
    key: "energy_score",
    question: "您覺得有精神、有活力嗎？",
    leftText: "精神飽滿",
    rightText: "完全沒力氣",
    leftEmoji: "✅",
    rightEmoji: "🥵",
    options: [
      { value: 0, emoji: "✅", text: "精神飽滿\n（活力充沛）" },
      { value: 1, emoji: "😊", text: "精神還好\n（正常狀態）" },
      { value: 2, emoji: "😐", text: "有點疲倦\n（需要休息）" },
      { value: 3, emoji: "🙁", text: "蠻累的\n（沒什麼力）" },
      { value: 4, emoji: "🤢", text: "非常疲累\n（提不起勁）" },
      { value: 5, emoji: "🥵", text: "完全沒力氣" },
    ],
  },
];

const CATForm = () => {
  const navigate = useNavigate();
  const { speak, enableVoice } = useAccessibility();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const totalScore = Object.values(answers).reduce((sum, val) => sum + val, 0);
  const progress = (Object.keys(answers).length / CAT_QUESTIONS.length) * 100;

  useEffect(() => {
    // 語音播報當前題目
    if (enableVoice && CAT_QUESTIONS[currentQuestion]) {
      const question = CAT_QUESTIONS[currentQuestion];
      // Speak full question with scale context
      const fullText = `第 ${currentQuestion + 1} 題，${question.question}，從 ${question.leftText} 到 ${question.rightText}。`;
      speak(fullText);
    }
  }, [currentQuestion, enableVoice, speak]);

  const handleAnswer = (value) => {
    setAnswers({
      ...answers,
      [CAT_QUESTIONS[currentQuestion].key]: value,
    });

    // 自動進入下一題
    if (currentQuestion < CAT_QUESTIONS.length - 1) {
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1);
      }, 300);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleNext = () => {
    if (currentQuestion < CAT_QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length < CAT_QUESTIONS.length) {
      showMessage("error", "請完成所有題目");
      return;
    }

    setIsSubmitting(true);
    try {
      // 取得病患 ID（從 LIFF 或 localStorage）
      const patientId =
        localStorage.getItem("patientId") ||
        sessionStorage.getItem("patientId");

      if (!patientId) {
        throw new Error("找不到病患 ID，請重新登入");
      }

      // 準備 CAT 問卷資料
      const catData = {
        cough_score: answers.cough_score || 0,
        phlegm_score: answers.phlegm_score || 0,
        chest_score: answers.chest_score || 0,
        breathless_score: answers.breathless_score || 0,
        activities_score: answers.activities_score || 0,
        confidence_score: answers.confidence_score || 0,
        sleep_score: answers.sleep_score || 0,
        energy_score: answers.energy_score || 0,
        total_score: totalScore,
      };

      // 提交到 API
      const response = await fetch(
        `/api/v1/patients/${patientId}/questionnaires/cat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(catData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "提交失敗");
      }

      showMessage("success", "問卷已提交成功！");

      // 延遲後跳轉到 mMRC 問卷
      setTimeout(() => {
        navigate("/liff/questionnaire/mmrc");
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

  const getSeverityLevel = (score) => {
    if (score <= 10) return { text: "輕微", color: "#52c41a", emoji: "😊" };
    if (score <= 20) return { text: "中度", color: "#faad14", emoji: "😐" };
    if (score <= 30) return { text: "嚴重", color: "#ff7a45", emoji: "😟" };
    return { text: "非常嚴重", color: "#ff4d4f", emoji: "😰" };
  };

  const severity = getSeverityLevel(totalScore);
  const question = CAT_QUESTIONS[currentQuestion];

  return (
    <div className="cat-form-page">
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

        .cat-form-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            "PingFang TC", "Microsoft YaHei", sans-serif;
          position: relative;
        }

        .cat-form-page::before {
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
          padding: 24px 20px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          border-bottom: 1px solid rgba(255, 255, 255, 0.3);
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

        .progress-section {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          padding: 12px 20px;
          margin-bottom: 2px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .progress-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }

        .progress-text {
          font-size: 14px;
          color: #64748b;
          font-weight: 500;
        }

        .score-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 14px;
          font-weight: 600;
          background: ${severity.color}15;
          color: ${severity.color};
        }

        .progress-bar {
          width: 100%;
          height: 6px;
          background: #e2e8f0;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #2563eb);
          border-radius: 6px;
          transition: width 300ms ease;
        }

        .question-card {
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          padding: 16px 20px;
          flex: 1;
          display: flex;
          flex-direction: column;
          animation: fadeIn 0.3s ease;
          overflow-y: auto;
        }

        .question-header {
          margin-bottom: 16px;
        }

        .question-number {
          display: inline-block;
          background: #ebf5ff;
          color: #3b82f6;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .question-text {
          font-size: 22px;
          font-weight: 600;
          color: #1e293b;
          line-height: 1.4;
        }

        .scale-labels {
          display: flex;
          justify-content: space-between;
          margin-bottom: 24px;
          padding: 12px;
          background: rgba(248, 250, 252, 0.8);
          backdrop-filter: blur(6px);
          -webkit-backdrop-filter: blur(6px);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.5);
        }

        .scale-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          color: #64748b;
          font-weight: 500;
        }

        .scale-emoji {
          font-size: 24px;
        }

        .options-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          flex: 1;
          overflow-y: auto;
          padding-bottom: 16px;
        }

        .option-button {
          padding: 16px;
          border: 1px solid rgba(226, 232, 240, 0.6);
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          cursor: pointer;
          transition: all 200ms;
          display: flex;
          align-items: center;
          gap: 12px;
          min-height: auto;
        }

        .option-button:hover {
          background: rgba(240, 247, 255, 0.98);
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .option-button.selected {
          background: rgba(219, 234, 254, 0.98);
          border-color: #3b82f6;
          border-width: 2px;
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }

        .option-score {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background: #e8f4f8;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: 700;
          color: #3b82f6;
          flex-shrink: 0;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .option-button.selected .option-score {
          background: #3b82f6;
          color: white;
          box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
        }

        .option-button:hover .option-score {
          background: #dbeafe;
          transform: scale(1.05);
        }

        .option-button.selected:hover .option-score {
          background: #2563eb;
        }

        .option-content {
          flex: 1;
          padding-left: 12px;
        }

        .option-description {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }

        .option-emoji {
          font-size: 28px;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .option-text {
          font-size: 16px;
          color: #1e293b;
          line-height: 1.4;
          font-weight: 500;
          flex: 1;
        }

        .option-button:hover .option-text {
          color: #0f172a;
        }

        .navigation {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          padding: 16px 20px;
          border-top: 1px solid rgba(226, 232, 240, 0.5);
          display: flex;
          gap: 12px;
          box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
        }

        .nav-btn {
          flex: 1;
          padding: 14px;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          background: white;
          color: #64748b;
          font-size: 18px;
          font-weight: 600;
          cursor: pointer;
          transition: all 200ms;
        }

        .nav-btn:hover:not(:disabled) {
          background: #f8fafc;
          border-color: #3b82f6;
          color: #3b82f6;
        }

        .nav-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .nav-btn.primary {
          background: #3b82f6;
          color: white;
          border: none;
        }

        .nav-btn.primary:hover:not(:disabled) {
          background: #2563eb;
          transform: scale(1.02);
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
          margin-bottom: 16px;
        }

        .confirm-score {
          font-size: 48px;
          font-weight: 700;
          color: ${severity.color};
          margin: 24px 0;
        }

        .confirm-level {
          font-size: 20px;
          color: #64748b;
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
      `}</style>

      <div className="container">
        {/* 頁面標題 */}
        <div className="header">
          <h1 className="title">COPD 評估測試</h1>
          <p className="subtitle">請根據您最近一週的感受作答</p>
        </div>

        {/* 進度條 */}
        <div className="progress-section">
          <div className="progress-info">
            <span className="progress-text">
              {Object.keys(answers).length} / {CAT_QUESTIONS.length} 題
            </span>
            <div className="score-badge">
              <span>{severity.emoji}</span>
              <span>目前 {totalScore} 分</span>
            </div>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* 問題卡片 */}
        {question && (
          <div className="question-card" key={currentQuestion}>
            <div className="question-header">
              <span className="question-number">
                第 {currentQuestion + 1} / {CAT_QUESTIONS.length} 題
              </span>
              <h2 className="question-text">{question.question}</h2>
            </div>

            <div className="scale-labels">
              <div className="scale-label">
                <span className="scale-emoji">{question.leftEmoji}</span>
                <span>{question.leftText}</span>
              </div>
              <div className="scale-label">
                <span>{question.rightText}</span>
                <span className="scale-emoji">{question.rightEmoji}</span>
              </div>
            </div>

            <div className="options-list">
              {question.options.map((option) => (
                <button
                  key={option.value}
                  className={`option-button ${
                    answers[question.key] === option.value ? "selected" : ""
                  }`}
                  onClick={() => handleAnswer(option.value)}
                >
                  <div className="option-score">{option.value}</div>
                  <div className="option-content">
                    <div className="option-description">
                      <span className="option-emoji">{option.emoji}</span>
                      <div className="option-text">{option.text}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 導航按鈕 */}
        <div className="navigation">
          <button
            className="nav-btn"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            上一題
          </button>

          {currentQuestion === CAT_QUESTIONS.length - 1 ? (
            <button
              className="nav-btn primary"
              onClick={() => {
                if (Object.keys(answers).length === CAT_QUESTIONS.length) {
                  setShowConfirmDialog(true);
                } else {
                  showMessage("error", "請完成所有題目");
                }
              }}
              disabled={
                Object.keys(answers).length < CAT_QUESTIONS.length ||
                isSubmitting
              }
            >
              {isSubmitting ? "提交中..." : "完成"}
            </button>
          ) : (
            <button
              className="nav-btn primary"
              onClick={handleNext}
              disabled={!answers[question?.key]}
            >
              下一題
            </button>
          )}
        </div>
      </div>

      {/* 確認對話框 */}
      {showConfirmDialog && (
        <div className="confirm-dialog">
          <div className="confirm-content">
            <h2 className="confirm-title">確認提交評估結果</h2>
            <div className="confirm-score">{totalScore} 分</div>
            <div className="confirm-level">
              {severity.emoji} {severity.text}症狀
            </div>
            <div className="confirm-buttons">
              <button
                className="confirm-btn cancel"
                onClick={() => setShowConfirmDialog(false)}
              >
                返回檢查
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
          onClick={() => speak(question?.question)}
          aria-label="重複播放題目"
        >
          🔊
        </button>
      )}
    </div>
  );
};

export default CATForm;
