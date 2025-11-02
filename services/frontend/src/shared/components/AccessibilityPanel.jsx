import { useState } from "react";
import {
  FloatButton,
  Drawer,
  Switch,
  Space,
  Typography,
  Divider,
  Slider,
} from "antd";
import {
  SettingOutlined,
  EyeOutlined,
  FontSizeOutlined,
  SoundOutlined,
  BgColorsOutlined,
} from "@ant-design/icons";
import { useAccessibility } from "../contexts/AccessibilityContext";

const { Title, Text } = Typography;

const AccessibilityPanel = () => {
  const [open, setOpen] = useState(false);
  const {
    isHighContrast,
    isLargeText,
    enableVoice,
    toggleHighContrast,
    toggleLargeText,
    toggleVoice,
  } = useAccessibility();

  return (
    <>
      {/* 浮動按鈕 - 無障礙設定入口 */}
      <FloatButton.Group
        trigger="hover"
        type="primary"
        style={{ right: 24, bottom: 24 }}
        icon={<SettingOutlined />}
      >
        <FloatButton
          icon={<EyeOutlined />}
          tooltip="無障礙設定"
          onClick={() => setOpen(true)}
        />
      </FloatButton.Group>

      {/* 設定抽屜 */}
      <Drawer
        title={
          <Title level={3} style={{ margin: 0 }}>
            <EyeOutlined style={{ marginRight: 8 }} />
            無障礙設定
          </Title>
        }
        placement="right"
        onClose={() => setOpen(false)}
        open={open}
        width={400}
        style={{ fontFamily: "Noto Sans TC" }}
      >
        <Space direction="vertical" style={{ width: "100%" }} size="large">
          {/* 高對比度模式 */}
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 8,
              }}
            >
              <div>
                <Text strong style={{ fontSize: 20 }}>
                  <BgColorsOutlined style={{ marginRight: 8 }} />
                  高對比度模式
                </Text>
                <br />
                <Text type="secondary" style={{ fontSize: 16 }}>
                  增強文字與背景的對比度
                </Text>
              </div>
              <Switch
                checked={isHighContrast}
                onChange={toggleHighContrast}
                size="large"
              />
            </div>
          </div>

          <Divider />

          {/* 大字體模式 */}
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 8,
              }}
            >
              <div>
                <Text strong style={{ fontSize: 20 }}>
                  <FontSizeOutlined style={{ marginRight: 8 }} />
                  大字體模式
                </Text>
                <br />
                <Text type="secondary" style={{ fontSize: 16 }}>
                  放大所有文字大小
                </Text>
              </div>
              <Switch
                checked={isLargeText}
                onChange={toggleLargeText}
                size="large"
              />
            </div>
          </div>

          <Divider />

          {/* 語音播報 */}
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 8,
              }}
            >
              <div>
                <Text strong style={{ fontSize: 20 }}>
                  <SoundOutlined style={{ marginRight: 8 }} />
                  語音播報
                </Text>
                <br />
                <Text type="secondary" style={{ fontSize: 16 }}>
                  自動朗讀問題和選項
                </Text>
              </div>
              <Switch
                checked={enableVoice}
                onChange={toggleVoice}
                size="large"
              />
            </div>
          </div>

          <Divider />

          {/* 使用提示 */}
          <div
            style={{
              padding: 16,
              backgroundColor: "#F0F9FF",
              borderRadius: 12,
              border: "1px solid #BAE6FD",
            }}
          >
            <Title level={5} style={{ marginTop: 0, color: "#0369A1" }}>
              使用提示
            </Title>
            <Space direction="vertical" style={{ fontSize: 16 }}>
              <Text>• 您可以隨時調整這些設定</Text>
              <Text>• 設定會自動保存</Text>
              <Text>• 下次使用時會記住您的偏好</Text>
            </Space>
          </div>

          {/* 快捷鍵說明 */}
          <div
            style={{
              padding: 16,
              backgroundColor: "#FEF3C7",
              borderRadius: 12,
              border: "1px solid #FCD34D",
            }}
          >
            <Title level={5} style={{ marginTop: 0, color: "#92400E" }}>
              鍵盤快捷鍵
            </Title>
            <Space direction="vertical" style={{ fontSize: 16 }}>
              <Text>• Tab：切換選項</Text>
              <Text>• Enter：確認選擇</Text>
              <Text>• Esc：關閉視窗</Text>
            </Space>
          </div>
        </Space>
      </Drawer>
    </>
  );
};

export default AccessibilityPanel;
