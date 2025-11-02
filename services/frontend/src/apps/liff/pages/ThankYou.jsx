import { Result, Button, Card, Typography, Space } from "antd";
import {
  CheckCircleOutlined,
  HomeOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useAccessibility } from "../../../shared/contexts/AccessibilityContext";
import bgImageUrl from "@assets/毛玻璃_BG2.png";

const { Title, Text } = Typography;

const ThankYou = () => {
  const navigate = useNavigate();
  const { speak, enableVoice } = useAccessibility();

  useEffect(() => {
    if (enableVoice) {
      speak(
        "感謝您完成 COPD 健康評估！您的 CAT 與 mMRC 評估結果已經成功記錄。"
      );
    }
  }, [enableVoice, speak]);

  return (
    <div className="thankyou-page">
      <style jsx>{`
        .thankyou-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            "PingFang TC", "Microsoft YaHei", sans-serif;
          position: relative;
        }

        .thankyou-page::before {
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
          max-width: 600px;
          margin: 0 auto;
          position: relative;
          z-index: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: 100vh;
        }

        .main-card {
          border-radius: 20px !important;
          background: rgba(255, 255, 255, 0.95) !important;
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
          border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }

        .success-icon {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 24px;
          box-shadow: 0 8px 24px rgba(82, 196, 26, 0.3);
        }

        .ant-result-title {
          color: #2c3e50 !important;
          font-size: 32px !important;
          font-weight: 700 !important;
        }

        .ant-result-subtitle {
          color: #6b7280 !important;
          font-size: 20px !important;
          margin-bottom: 32px !important;
        }

        .info-card {
          background: linear-gradient(
            135deg,
            #f0fdf4 0%,
            #dcfce7 100%
          ) !important;
          border: 1px solid #86efac !important;
          border-radius: 12px !important;
          margin-bottom: 20px !important;
        }

        .next-steps {
          background: linear-gradient(
            135deg,
            #eff6ff 0%,
            #f0f9ff 100%
          ) !important;
          border: 1px solid #bfdbfe !important;
          border-radius: 12px !important;
          margin-bottom: 24px !important;
        }

        .reminder-card {
          background: linear-gradient(
            135deg,
            #fef3c7 0%,
            #fed7aa 100%
          ) !important;
          border: 1px solid #fcd34d !important;
          border-radius: 12px !important;
          margin-top: 24px !important;
        }

        .ant-btn-primary {
          background: linear-gradient(
            135deg,
            #7cc6ff 0%,
            #5ba4e0 100%
          ) !important;
          border: none !important;
          border-radius: 12px !important;
          height: 56px !important;
          font-size: 20px !important;
          min-width: 160px !important;
          box-shadow: 0 4px 12px rgba(124, 198, 255, 0.3) !important;
        }

        .ant-btn {
          border-radius: 12px !important;
          height: 56px !important;
          font-size: 20px !important;
          min-width: 160px !important;
        }

        @media (max-width: 480px) {
          .ant-result-title {
            font-size: 28px !important;
          }

          .ant-result-subtitle {
            font-size: 18px !important;
          }

          .container {
            padding: 20px;
          }
        }
      `}</style>

      <div className="container">
        <Card className="main-card">
          <Result
            icon={
              <div className="success-icon">
                <CheckCircleOutlined style={{ fontSize: 60, color: "white" }} />
              </div>
            }
            title="感謝您的配合！"
            subTitle="您的 COPD 健康評估已完成"
            extra={
              <Space
                direction="vertical"
                size="large"
                style={{ width: "100%" }}
              >
                <Card className="info-card">
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Text strong style={{ fontSize: 18, color: "#166534" }}>
                      ✅ CAT 與 mMRC 評估已完成
                    </Text>
                    <Text style={{ fontSize: 16 }}>
                      您的評估結果將幫助醫療團隊更好地了解您的 COPD 症狀嚴重程度
                    </Text>
                  </Space>
                </Card>

                <Card className="next-steps">
                  <Title level={5} style={{ color: "#1E40AF", marginTop: 0 }}>
                    接下來您可以：
                  </Title>
                  <Space
                    direction="vertical"
                    style={{ fontSize: 16, width: "100%" }}
                  >
                    <Text>• 返回首頁查看其他功能</Text>
                    <Text>• 記錄今日的健康數據</Text>
                    <Text>• 使用語音助理諮詢健康問題</Text>
                    <Text>• 查看您的健康趨勢報告</Text>
                  </Space>
                </Card>

                <Space size="large" style={{ marginTop: 32, width: "100%" }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<HomeOutlined />}
                    onClick={() => navigate("/liff")}
                    block
                  >
                    返回首頁
                  </Button>
                </Space>

                <Card className="reminder-card">
                  <Space>
                    <span style={{ fontSize: 28 }}>💡</span>
                    <div>
                      <Text strong style={{ fontSize: 18, color: "#92400E" }}>
                        溫馨提醒
                      </Text>
                      <br />
                      <Text style={{ fontSize: 16 }}>
                        建議您定期填寫健康問卷，這有助於追蹤您的健康狀況變化
                      </Text>
                    </div>
                  </Space>
                </Card>
              </Space>
            }
          />
        </Card>
      </div>
    </div>
  );
};

export default ThankYou;
