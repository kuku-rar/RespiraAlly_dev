import { useState, useRef } from "react";
import { useAccessibility } from "../../../shared/contexts/AccessibilityContext";
import bgImageUrl from "@assets/毛玻璃_BG2.png";
import logoImageUrl from "@assets/logo demo3.png";

const PLACEHOLDER = "今天想跟艾莉分享什麼呢？";

const VoiceChat = () => {
  const { speak, enableVoice } = useAccessibility();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [overlayText, setOverlayText] = useState("");
  const [messages, setMessages] = useState([]);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // 打字機效果
  const typeText = (text) => {
    let i = 0;
    setOverlayText("");
    const step = () => {
      setOverlayText(
        (prev) =>
          prev + text.slice(i, i + Math.max(2, Math.floor(Math.random() * 4)))
      );
      i += Math.max(2, Math.floor(Math.random() * 4));
      if (i < text.length) {
        setTimeout(step, 35);
      }
    };
    step();
  };

  // 顯示訊息
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

  // 開始錄音
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        await processAudio(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      typeText("我正在聆聽...");
    } catch (error) {
      showMessage("error", "無法存取麥克風");
    }
  };

  // 停止錄音
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream
        .getTracks()
        .forEach((track) => track.stop());
      setIsRecording(false);
    }
  };

  // 處理音訊
  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    typeText("正在處理語音...");

    try {
      // 語音轉文字
      const formData = new FormData();
      formData.append("audio", audioBlob, "audio.wav");

      const transcribeResponse = await fetch("/api/v1/voice/transcribe", {
        method: "POST",
        body: formData,
      });

      if (!transcribeResponse.ok) {
        throw new Error("語音識別失敗");
      }

      const transcribeData = await transcribeResponse.json();
      const userText = transcribeData.data?.text || transcribeData.text || "";

      if (!userText) {
        throw new Error("無法識別語音內容");
      }

      typeText("正在思考回應...");

      // 發送聊天請求
      const chatResponse = await fetch("/api/v1/voice/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: userText,
          patient_id:
            localStorage.getItem("patientId") ||
            sessionStorage.getItem("patientId"),
        }),
      });

      if (!chatResponse.ok) {
        throw new Error("AI 回應失敗");
      }

      const chatData = await chatResponse.json();
      const aiResponse =
        chatData.data?.response || chatData.response || "抱歉，我無法回應。";

      // 添加到訊息列表
      setMessages((prev) => [
        ...prev,
        { type: "user", content: userText },
        { type: "ai", content: aiResponse },
      ]);

      typeText(aiResponse);

      if (enableVoice) {
        speak(aiResponse);
      }

      setIsProcessing(false);
    } catch (error) {
      console.error("語音處理錯誤:", error);
      const errorMessage = "語音處理失敗，請重試";

      setMessages((prev) => [
        ...prev,
        { type: "user", content: "(語音訊息)" },
        { type: "ai", content: errorMessage },
      ]);

      typeText(errorMessage);
      setIsProcessing(false);
    }
  };

  const handleRecordToggle = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div
      className="voice-chat-container"
      style={{
        backgroundImage: `url(${bgImageUrl})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        minHeight: "100vh",
        position: "relative",
      }}
    >
      {/* 毛玻璃效果 */}
      <div className="glass-overlay" />

      {/* 主要內容 */}
      <div className="content">
        {/* Logo 區域 */}
        <div className="logo-section">
          <img src={logoImageUrl} alt="RespiraAlly" className="logo" />
          <h1 className="title">AI 語音助手</h1>
          <p className="subtitle">艾莉正在聆聽您的需求</p>
        </div>

        {/* 對話顯示區 */}
        <div className="chat-display">
          {messages.length > 0 ? (
            <div className="messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message-item ${msg.type}`}>
                  <span className="message-icon">
                    {msg.type === "user" ? "👤" : "🤖"}
                  </span>
                  <span className="message-content">{msg.content}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="placeholder-text">{PLACEHOLDER}</div>
          )}
        </div>

        {/* 文字疊加層 */}
        {overlayText && (
          <div className="overlay-text">
            <p>{overlayText}</p>
          </div>
        )}

        {/* 控制按鈕 */}
        <div className="controls">
          <button
            className={`record-btn ${isRecording ? "recording" : ""}`}
            onClick={handleRecordToggle}
            disabled={isProcessing}
          >
            <span className="icon">{isRecording ? "⏸️" : "🎙️"}</span>
            <span className="label">
              {isRecording ? "停止錄音" : "開始對話"}
            </span>
          </button>
        </div>

        {/* 底部導航 */}
        <footer className="footer">
          <button className="nav-btn" onClick={() => window.history.back()}>
            <span>⬅️</span>
            <span>返回</span>
          </button>

          <div className="status">
            {isProcessing ? "處理中..." : isRecording ? "錄音中..." : "就緒"}
          </div>

          <button className="nav-btn">
            <span>設定</span>
            <span>➡️</span>
          </button>
        </footer>
      </div>

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

        .voice-chat-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .glass-overlay {
          position: fixed;
          inset: 0;
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
        }

        .content {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 600px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 30px;
        }

        .logo-section {
          text-align: center;
        }

        .logo {
          width: 80px;
          height: 80px;
          margin-bottom: 16px;
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

        .chat-display {
          width: 100%;
          min-height: 200px;
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .messages {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .message-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          border-radius: 12px;
          animation: slideDown 0.3s ease;
        }

        .message-item.user {
          background: #e9f2ff;
          align-self: flex-end;
        }

        .message-item.ai {
          background: #f0f0f0;
          align-self: flex-start;
        }

        .message-icon {
          font-size: 20px;
        }

        .message-content {
          flex: 1;
          font-size: 14px;
          line-height: 1.6;
        }

        .placeholder-text {
          text-align: center;
          color: #9ca3af;
          font-size: 16px;
        }

        .overlay-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background: rgba(255, 255, 255, 0.95);
          padding: 30px;
          border-radius: 16px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
          max-width: 500px;
          z-index: 10;
        }

        .overlay-text p {
          font-size: 18px;
          line-height: 1.8;
          color: #2c3e50;
          margin: 0;
        }

        .controls {
          display: flex;
          justify-content: center;
        }

        .record-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 32px;
          background: linear-gradient(135deg, #7cc6ff, #5cb8ff);
          color: white;
          border: none;
          border-radius: 50px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 300ms;
          box-shadow: 0 8px 24px rgba(124, 198, 255, 0.3);
        }

        .record-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 12px 32px rgba(124, 198, 255, 0.4);
        }

        .record-btn.recording {
          background: linear-gradient(135deg, #ff6b6b, #ff5252);
          animation: pulse 1.5s infinite;
        }

        .record-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        @keyframes pulse {
          0%,
          100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }

        .record-btn .icon {
          font-size: 24px;
        }

        .footer {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(0, 0, 0, 0.06);
        }

        .nav-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: transparent;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          color: #6b7280;
          font-size: 14px;
          cursor: pointer;
          transition: all 200ms;
        }

        .nav-btn:hover {
          background: #f9fafb;
          color: #2c3e50;
        }

        .status {
          font-size: 14px;
          color: #6b7280;
        }

        @media (max-width: 480px) {
          .content {
            padding: 16px;
          }

          .title {
            font-size: 24px;
          }

          .record-btn {
            padding: 14px 24px;
          }
        }
      `}</style>
    </div>
  );
};

export default VoiceChat;
