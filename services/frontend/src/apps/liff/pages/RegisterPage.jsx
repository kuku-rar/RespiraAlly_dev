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
import { useLIFF } from "../../../hooks/useLIFF";
import bgImageUrl from "@assets/毛玻璃_BG2.png";

const { Title, Text, Paragraph } = Typography;

const RegisterPage = () => {
  const navigate = useNavigate();
  const { speak, enableVoice } = useAccessibility();
  const { isLoggedIn, profile, isReady, login } = useLIFF();
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
      // 確保已登入並有 profile 資料
      if (!isLoggedIn || !profile) {
        message.error("請先登入 LINE");
        login();
        return;
      }

      // 準備註冊資料
      const registerData = {
        lineUserId: profile.userId, // 自動從 LIFF profile 抓取 LINE UID
        first_name: values.firstName, // 名
        last_name: values.lastName, // 姓
        gender: values.gender,
        phone: values.phone,
        // 健康資訊 (選填)
        height_cm: values.height_cm,
        weight_kg: values.weight_kg,
        smoke_status: values.smoke_status,
      };

      // 調用註冊 API
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/line/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(registerData),
      });

      const data = await response.json();

      if (!response.ok) {
        // 處理錯誤
        const errorMessage =
          data.error?.message || "註冊失敗，請稍後重試";
        throw new Error(errorMessage);
      }

      // 儲存 token 到 localStorage
      if (data.data?.token) {
        localStorage.setItem("access_token", data.data.token);
        localStorage.setItem("user_id", data.data.user.id);
        localStorage.setItem("line_user_id", data.data.user.line_user_id);
      }

      if (enableVoice) {
        speak("註冊成功！歡迎使用呼吸系統健康管理服務");
      }

      message.success("註冊成功！");

      // 註冊成功後導向首頁
      navigate("/liff");
    } catch (error) {
      console.error("註冊失敗:", error);
      message.error(error.message || "註冊失敗，請稍後重試");
    } finally {
      setLoading(false);
    }
  };

  // 等待 LIFF 初始化
  if (!isReady) {
    return (
      <div className="register-page">
        <style jsx>{`
          .register-page {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
          }
        `}</style>
        <Space direction="vertical" align="center" size="large">
          <LoadingOutlined style={{ fontSize: 48, color: "#fff" }} />
          <Text style={{ color: "#fff", fontSize: 18 }}>載入中...</Text>
        </Space>
      </div>
    );
  }

  // 未登入時顯示登入提示
  if (!isLoggedIn) {
    return (
      <div className="register-page">
        <style jsx>{`
          .register-page {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
          }
        `}</style>
        <Card style={{ maxWidth: 400, textAlign: "center" }}>
          <Space direction="vertical" size="large">
            <Avatar size={64} style={{ background: "#3b82f6" }}>
              <UserOutlined />
            </Avatar>
            <Title level={3}>需要登入 LINE</Title>
            <Text>請先登入 LINE 帳號以繼續註冊流程</Text>
            <Button type="primary" size="large" onClick={login} block>
              登入 LINE
            </Button>
          </Space>
        </Card>
      </div>
    );
  }

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
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="姓氏"
                    name="lastName"
                    rules={[{ required: true, message: "請輸入您的姓氏" }]}
                  >
                    <Input placeholder="例：陳" />
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12}>
                  <Form.Item
                    label="名字"
                    name="firstName"
                    rules={[{ required: true, message: "請輸入您的名字" }]}
                  >
                    <Input placeholder="例：美麗" />
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

              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="身高 (公分)"
                    name="height_cm"
                    rules={[
                      {
                        type: "number",
                        min: 100,
                        max: 250,
                        message: "身高需在 100-250 公分之間",
                      },
                    ]}
                  >
                    <InputNumber
                      style={{ width: "100%" }}
                      placeholder="請輸入身高"
                      min={100}
                      max={250}
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12}>
                  <Form.Item
                    label="體重 (公斤)"
                    name="weight_kg"
                    rules={[
                      {
                        type: "number",
                        min: 30,
                        max: 300,
                        message: "體重需在 30-300 公斤之間",
                      },
                    ]}
                  >
                    <InputNumber
                      style={{ width: "100%" }}
                      placeholder="請輸入體重"
                      min={30}
                      max={300}
                    />
                  </Form.Item>
                </Col>

                <Col span={24}>
                  <Form.Item
                    label="吸菸狀態"
                    name="smoke_status"
                  >
                    <Select placeholder="請選擇吸菸狀態（選填）">
                      <Select.Option value="never">從不吸菸</Select.Option>
                      <Select.Option value="former">已戒菸</Select.Option>
                      <Select.Option value="current">目前吸菸</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
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
