import { useState } from "react";
import { useNavigate } from "react-router-dom";

const DailyMetrics = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    water: "",
    medication: "",
    exercise: "",
    cigarettes: "",
  });
  const [customInputs, setCustomInputs] = useState({
    water: "",
    exercise: "",
    cigarettes: "",
  });

  const handleOptionSelect = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // 清空對應的自定義輸入
    if (field !== "medication") {
      setCustomInputs((prev) => ({
        ...prev,
        [field]: "",
      }));
    }
  };

  const handleCustomInput = (field, value) => {
    setCustomInputs((prev) => ({
      ...prev,
      [field]: value,
    }));
    // 清空對應的預設選項
    setFormData((prev) => ({
      ...prev,
      [field]: "",
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 驗證所有必填欄位
      const finalData = {
        water: customInputs.water || formData.water,
        medication: formData.medication,
        exercise: customInputs.exercise || formData.exercise,
        cigarettes: customInputs.cigarettes || formData.cigarettes,
      };

      if (
        !finalData.water ||
        !finalData.medication ||
        !finalData.exercise ||
        !finalData.cigarettes
      ) {
        alert("請完成所有問題");
        return;
      }

      // 取得病患 ID
      const patientId =
        localStorage.getItem("patientId") ||
        sessionStorage.getItem("patientId") ||
        getUserId();

      if (!patientId) {
        throw new Error("找不到病患 ID，請重新登入");
      }

      // 轉換資料格式以符合後端 API 期望
      const apiData = {
        water_intake: parseInt(finalData.water),
        medication_taken: finalData.medication === "是" ? true : false,
        exercise_minutes: parseInt(finalData.exercise),
        cigarettes_count: parseInt(finalData.cigarettes),
        mood_score: 3, // 預設中等心情，後續可加入心情選擇
        symptoms: [], // 預設無症狀，後續可加入症狀選擇
      };

      console.log("準備送出的資料:", apiData);

      // 提交到正確的 API 端點
      const response = await fetch(
        `/api/v1/patients/${patientId}/daily_metrics`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(apiData),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 顯示成功訊息
      const messageDiv = document.createElement("div");
      messageDiv.className = "success-message";
      messageDiv.textContent = "健康數據已記錄！";
      messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        background: #52c41a;
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideDown 0.3s ease;
      `;
      document.body.appendChild(messageDiv);
      setTimeout(() => messageDiv.remove(), 3000);

      console.log("Server 回應：", data);

      // 延遲後返回首頁
      setTimeout(() => {
        navigate("/liff");
      }, 1000);
    } catch (error) {
      console.error("Submit error:", error);
      // 顯示錯誤訊息
      const messageDiv = document.createElement("div");
      messageDiv.className = "error-message";
      messageDiv.textContent = "送出失敗，請稍後再試";
      messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        background: #ff4d4f;
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideDown 0.3s ease;
      `;
      document.body.appendChild(messageDiv);
      setTimeout(() => messageDiv.remove(), 3000);
    } finally {
      setLoading(false);
    }
  };

  // 測試用函數 - 實際使用時需要替換為真實的用戶認證
  const getUserId = () => {
    // 測試用：從 localStorage 獲取或使用預設值
    return localStorage.getItem("patient_id") || 1;
  };

  return (
    <div className="daily-metrics-page">
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

        .daily-metrics-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #e9f2ff 0%, #f8f8f8 100%);
          padding: 20px;
        }

        .container {
          max-width: 600px;
          margin: 0 auto;
        }

        .header {
          text-align: center;
          margin-bottom: 32px;
        }

        .title {
          font-size: 28px;
          font-weight: 700;
          color: #2c3e50;
          margin: 0 0 8px 0;
        }

        .subtitle {
          font-size: 14px;
          color: #6b7280;
          margin: 0;
        }

        .form-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          margin-bottom: 20px;
        }

        .section-title {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .section-icon {
          font-size: 20px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: #4b5563;
          margin-bottom: 8px;
        }

        .input-group {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .option-buttons {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          margin-bottom: 16px;
        }

        .option-btn {
          min-height: 44px;
          padding: 12px 16px;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          background: white;
          color: #4b5563;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: all 200ms;
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .option-btn:hover {
          border-color: #7cc6ff;
          background: #f8faff;
          transform: translateY(-1px);
        }

        .option-btn.selected {
          background: #7cc6ff;
          border-color: #5cb8ff;
          color: white;
          box-shadow: 0 4px 12px rgba(124, 198, 255, 0.3);
        }

        .custom-input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          font-size: 16px;
          background: white;
          margin-top: 8px;
        }

        .custom-input:focus {
          outline: none;
          border-color: #7cc6ff;
          box-shadow: 0 0 0 3px rgba(124, 198, 255, 0.1);
        }

        .custom-input.has-value {
          border-color: #7cc6ff;
          background: #f8faff;
        }

        .unit {
          color: #6b7280;
          font-size: 14px;
        }

        .question-text {
          font-size: 20px;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 16px;
          text-align: center;
        }

        .button-group {
          display: flex;
          gap: 12px;
          margin-top: 32px;
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
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .btn-primary {
          background: linear-gradient(135deg, #7cc6ff, #5cb8ff);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(124, 198, 255, 0.3);
        }

        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: white;
          color: #6b7280;
          border: 1px solid #e5e7eb;
        }

        .btn-secondary:hover {
          background: #f9fafb;
        }

        @media (max-width: 480px) {
          .option-buttons {
            grid-template-columns: 1fr;
          }

          .question-text {
            font-size: 18px;
          }
        }
      `}</style>

      <div className="container">
        {/* 頁面標題 */}
        <div className="header">
          <h1 className="title">每日健康記錄</h1>
          <p className="subtitle">記錄您今天的健康狀況</p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Q1: 飲水量 */}
          <div className="form-card">
            <h2 className="question-text">你今天喝多少水（ml）？</h2>
            <div className="option-buttons">
              <button
                type="button"
                className={`option-btn ${
                  formData.water === "500" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("water", "500")}
              >
                500ml
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.water === "1000" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("water", "1000")}
              >
                1000ml
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.water === "1500" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("water", "1500")}
              >
                1500ml
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.water === "2000" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("water", "2000")}
              >
                2000ml
              </button>
            </div>
            <input
              type="number"
              className={`custom-input ${
                customInputs.water ? "has-value" : ""
              }`}
              placeholder="手動輸入 (ml)"
              value={customInputs.water}
              onChange={(e) => handleCustomInput("water", e.target.value)}
              min="0"
              max="5000"
            />
          </div>

          {/* Q2: 服藥 */}
          <div className="form-card">
            <h2 className="question-text">你今天吸藥了嗎？</h2>
            <div className="option-buttons">
              <button
                type="button"
                className={`option-btn ${
                  formData.medication === "是" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("medication", "是")}
              >
                是
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.medication === "否" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("medication", "否")}
              >
                否
              </button>
            </div>
          </div>

          {/* Q3: 運動時間 */}
          <div className="form-card">
            <h2 className="question-text">你今天運動多久？</h2>
            <div className="option-buttons">
              <button
                type="button"
                className={`option-btn ${
                  formData.exercise === "0" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("exercise", "0")}
              >
                0min (休息日)
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.exercise === "10" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("exercise", "10")}
              >
                10min
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.exercise === "20" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("exercise", "20")}
              >
                20min
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.exercise === "30" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("exercise", "30")}
              >
                30min
              </button>
            </div>
            <input
              type="number"
              className={`custom-input ${
                customInputs.exercise ? "has-value" : ""
              }`}
              placeholder="手動輸入 (分鐘)"
              value={customInputs.exercise}
              onChange={(e) => handleCustomInput("exercise", e.target.value)}
              min="0"
              max="300"
            />
          </div>

          {/* Q4: 吸菸量 */}
          <div className="form-card">
            <h2 className="question-text">今天抽了幾支菸？</h2>
            <div className="option-buttons">
              <button
                type="button"
                className={`option-btn ${
                  formData.cigarettes === "0" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("cigarettes", "0")}
              >
                很棒沒抽
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.cigarettes === "5" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("cigarettes", "5")}
              >
                5支
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.cigarettes === "10" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("cigarettes", "10")}
              >
                10支（半包）
              </button>
              <button
                type="button"
                className={`option-btn ${
                  formData.cigarettes === "20" ? "selected" : ""
                }`}
                onClick={() => handleOptionSelect("cigarettes", "20")}
              >
                20支（一包）
              </button>
            </div>
            <input
              type="number"
              className={`custom-input ${
                customInputs.cigarettes ? "has-value" : ""
              }`}
              placeholder="手動輸入 (支)"
              value={customInputs.cigarettes}
              onChange={(e) => handleCustomInput("cigarettes", e.target.value)}
              min="0"
              max="100"
            />
          </div>

          {/* 按鈕區 */}
          <div className="button-group">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate("/liff")}
            >
              取消
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              <span>💾</span>
              {loading ? "提交中..." : "送出紀錄"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DailyMetrics;
