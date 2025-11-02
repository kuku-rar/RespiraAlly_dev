import { useState, useEffect } from "react";
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  Space,
  message,
  Avatar,
  Alert,
  Select,
  InputNumber,
  Row,
  Col,
  Divider,
} from "antd";
import {
  UserOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  PhoneOutlined,
  HeartOutlined,
  FireOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

import { useAccessibility } from "../../../shared/contexts/AccessibilityContext";
import bgImageUrl from "@assets/毛玻璃_BG2.png";

const { Title, Text, Paragraph } = Typography;

const RegisterPage = () => {
  const navigate = useNavigate();
  const { speak, enableVoice } = useAccessibility();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (enableVoice) {
      speak("歡迎註冊呼吸系統健康管理平台，請填寫您的基本資料");
    }
  }, [enableVoice, speak]);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      // TODO: 實際的註冊 API 調用
      await new Promise((resolve) => setTimeout(resolve, 2000)); // 模擬 API 調用

      if (enableVoice) {
        speak("註冊成功！歡迎使用呼吸系統健康管理服務");
      }

      message.success("註冊成功！");
      navigate("/liff/questionnaire/thankyou");
    } catch (error) {
      console.error("註冊失敗:", error);
      message.error("註冊失敗，請稍後重試");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <style jsx>{`
        .register-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            "PingFang TC", "Microsoft YaHei", sans-serif;
          position: relative;
        }

        .register-page::before {
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
          padding: 20px;
          text-align: center;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        .form-container {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
        }

        .form-card {
          background: rgba(255, 255, 255, 0.95) !important;
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border-radius: 16px !important;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
          border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }

        .info-card {
          background: rgba(235, 245, 255, 0.8) !important;
          border: 1px solid rgba(59, 130, 246, 0.2) !important;
          border-radius: 12px !important;
          margin-bottom: 20px;
        }

        .submit-section {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          padding: 20px;
          border-top: 1px solid rgba(226, 232, 240, 0.5);
          box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
        }

        .ant-btn {
          height: 50px !important;
          font-size: 18px !important;
          border-radius: 12px !important;
        }

        .ant-btn-primary {
          background: #3b82f6 !important;
          border-color: #3b82f6 !important;
        }

        .ant-btn-primary:hover {
          background: #2563eb !important;
          border-color: #2563eb !important;
        }

        .ant-form-item-label > label {
          font-weight: 500 !important;
          color: #374151 !important;
        }

        .ant-input,
        .ant-select-selector,
        .ant-input-number {
          border-radius: 8px !important;
          border: 2px solid #e5e7eb !important;
          height: 45px !important;
          font-size: 16px !important;
        }

        .ant-input:focus,
        .ant-select-focused .ant-select-selector,
        .ant-input-number:focus {
          border-color: #3b82f6 !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }

        @media (max-width: 480px) {
          .form-card {
            padding: 20px;
          }
        }
      `}</style>

      <div className="container">
        <div className="header">
          <Avatar size={64} style={{ background: "#3b82f6", marginBottom: 16 }}>
            <UserOutlined />
          </Avatar>
          <Title level={2} style={{ margin: 0, color: "#1a365d" }}>
            註冊健康管理帳號
          </Title>
          <Text style={{ fontSize: 16, color: "#64748b" }}>
            請填寫您的基本資料，以便提供個人化的健康管理服務
          </Text>
        </div>

        <div className="form-container">
          <Card className="info-card">
            <Space>
              <span style={{ fontSize: 24 }}>🔐</span>
              <div>
                <Title level={5} style={{ margin: 0, color: "#1e40af" }}>
                  隱私保護
                </Title>
                <Text style={{ fontSize: 14, color: "#475569" }}>
                  您的個人資料將受到嚴格保護，僅用於提供醫療健康服務
                </Text>
              </div>
            </Space>
          </Card>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            size="large"
            scrollToFirstError
          >
            <Card className="form-card">
              <Title
                level={4}
                style={{ display: "flex", alignItems: "center", gap: 8 }}
              >
                <UserOutlined />
                基本資料
              </Title>

              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item
                    label="姓名"
                    name="name"
                    rules={[{ required: true, message: "請輸入您的姓名" }]}
                  >
                    <Input placeholder="請輸入您的姓名" />
                  </Form.Item>
                </Col>

                <Col span={24}>
                  <Form.Item
                    label="手機號碼"
                    name="phone"
                    rules={[
                      { required: true, message: "請輸入手機號碼" },
                      {
                        pattern: /^09\d{8}$/,
                        message: "請輸入正確的手機號碼格式",
                      },
                    ]}
                  >
                    <Input
                      prefix={<PhoneOutlined />}
                      placeholder="請輸入手機號碼 (例：0912345678)"
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12}>
                  <Form.Item
                    label="年齡"
                    name="age"
                    rules={[
                      { required: true, message: "請輸入年齡" },
                      {
                        type: "number",
                        min: 18,
                        max: 120,
                        message: "年齡需在 18-120 之間",
                      },
                    ]}
                  >
                    <InputNumber
                      style={{ width: "100%" }}
                      placeholder="請輸入年齡"
                      min={18}
                      max={120}
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12}>
                  <Form.Item
                    label="性別"
                    name="gender"
                    rules={[{ required: true, message: "請選擇性別" }]}
                  >
                    <Select placeholder="請選擇性別">
                      <Select.Option value="male">男性</Select.Option>
                      <Select.Option value="female">女性</Select.Option>
                      <Select.Option value="other">其他</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Card className="form-card">
              <Title
                level={4}
                style={{ display: "flex", alignItems: "center", gap: 8 }}
              >
                <HeartOutlined />
                健康資訊
              </Title>

              <Form.Item label="病史或慢性疾病" name="medicalHistory">
                <Input.TextArea
                  rows={3}
                  placeholder="請簡述您的重要病史、慢性疾病或正在服用的藥物（選填）"
                />
              </Form.Item>

              <Form.Item label="緊急聯絡人" name="emergencyContact">
                <Input placeholder="緊急聯絡人姓名和電話（選填）" />
              </Form.Item>
            </Card>
          </Form>
        </div>

        <div className="submit-section">
          <Row gutter={12}>
            <Col span={12}>
              <Button
                size="large"
                block
                onClick={() => navigate("/liff")}
                disabled={loading}
              >
                返回首頁
              </Button>
            </Col>
            <Col span={12}>
              <Button
                type="primary"
                size="large"
                block
                loading={loading}
                onClick={() => form.submit()}
                icon={loading ? <LoadingOutlined /> : <CheckCircleOutlined />}
              >
                {loading ? "註冊中..." : "完成註冊"}
              </Button>
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
