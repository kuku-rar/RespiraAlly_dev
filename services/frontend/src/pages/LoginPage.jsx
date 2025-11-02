import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../shared/contexts/AuthContext";
import logoImageUrl from "../assets/logo demo3.png";
import bgImageUrl from "../assets/毛玻璃_BG2.png";

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    account: "",
    password: "",
    remember: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const from = location.state?.from?.pathname || "/dashboard";

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.account || !formData.password) {
      setError("請輸入帳號和密碼");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await login({
        account: formData.account,
        password: formData.password,
        remember: formData.remember,
      });

      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.error || "登入失敗，請檢查帳號密碼");
      }
    } catch {
      setError("登入失敗，請稍後再試");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = (role) => {
    if (role === "therapist") {
      setFormData({
        account: "therapist_01",
        password: "password",
        remember: false,
      });
    } else {
      // Admin 沒有分配病患，改用 therapist_01 作為主要示範帳號
      setFormData({
        account: "therapist_01",
        password: "password",
        remember: false,
      });
    }
  };

  return (
    <div
      className="login-page"
      style={{
        backgroundImage: `url(${bgImageUrl})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        minHeight: "100vh",
      }}
    >
      {/* 背景毛玻璃覆層 */}
      <div className="backdrop" />

      {/* 登入容器 */}
      <div className="login-container">
        <div className="login-card">
          {/* Logo 區域 */}
          <div className="logo-section">
            <img src={logoImageUrl} alt="RespiraAlly" className="logo" />
            <h1 className="app-name">RespiraAlly</h1>
            <p className="app-subtitle">COPD 智慧照護管理系統</p>
          </div>

          {/* 登入表單 */}
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label className="form-label">帳號</label>
              <input
                type="text"
                name="account"
                className="form-input"
                placeholder="請輸入帳號"
                value={formData.account}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">密碼</label>
              <input
                type="password"
                name="password"
                className="form-input"
                placeholder="請輸入密碼"
                value={formData.password}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="remember"
                  checked={formData.remember}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <span>記住我</span>
              </label>
              <a href="#" className="forgot-link">
                忘記密碼？
              </a>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? "登入中..." : "登入"}
            </button>
          </form>

          {/* 示範帳號 */}
          <div className="demo-section">
            <p className="demo-title">示範帳號</p>
            <div className="demo-buttons">
              <button
                type="button"
                className="demo-btn"
                onClick={() => handleDemoLogin("therapist")}
                disabled={isLoading}
              >
                治療師帳號
              </button>
              <button
                type="button"
                className="demo-btn"
                onClick={() => handleDemoLogin("admin")}
                disabled={isLoading}
              >
                管理員帳號
              </button>
            </div>
          </div>

          {/* 其他登入方式 */}
          <div className="divider">
            <span>或</span>
          </div>

          <button
            type="button"
            className="line-login-btn"
            onClick={() => navigate("/liff")}
          >
            <span className="line-icon">📱</span>
            使用 LINE 登入（病患端）
          </button>
        </div>
      </div>

      <style jsx>{`
        .login-page {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .backdrop {
          position: fixed;
          inset: 0;
          background: rgba(255, 255, 255, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
        }

        .login-container {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 420px;
        }

        .login-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          border-radius: 24px;
          padding: 40px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }

        .logo-section {
          text-align: center;
          margin-bottom: 32px;
        }

        .logo {
          width: 80px;
          height: auto;
          margin-bottom: 16px;
        }

        .app-name {
          font-size: 28px;
          font-weight: 700;
          color: var(--primary);
          margin: 0 0 8px 0;
        }

        .app-subtitle {
          font-size: 14px;
          color: var(--muted);
          margin: 0;
        }

        .login-form {
          margin-bottom: 24px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text);
          margin-bottom: 8px;
        }

        .form-input {
          width: 100%;
          padding: 12px 16px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          font-size: 16px;
          transition: all 200ms;
          background: white;
        }

        .form-input:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(124, 198, 255, 0.1);
        }

        .form-input:disabled {
          background: #f9fafb;
          cursor: not-allowed;
        }

        .form-options {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
        }

        .checkbox-label input {
          width: 16px;
          height: 16px;
          cursor: pointer;
        }

        .forgot-link {
          font-size: 14px;
          color: var(--primary);
          text-decoration: none;
        }

        .forgot-link:hover {
          text-decoration: underline;
        }

        .error-message {
          background: #fee2e2;
          color: #dc2626;
          padding: 10px 12px;
          border-radius: 8px;
          font-size: 14px;
          margin-bottom: 16px;
        }

        .submit-btn {
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #7cc6ff, #5cb8ff);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 200ms;
        }

        .submit-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(124, 198, 255, 0.3);
        }

        .submit-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .demo-section {
          margin-bottom: 24px;
        }

        .demo-title {
          font-size: 12px;
          color: var(--muted);
          text-align: center;
          margin-bottom: 12px;
        }

        .demo-buttons {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .demo-btn {
          padding: 10px;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
        }

        .demo-btn:hover {
          background: white;
          border-color: var(--primary);
          color: var(--primary);
        }

        .demo-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .divider {
          text-align: center;
          margin: 24px 0;
          position: relative;
        }

        .divider::before {
          content: "";
          position: absolute;
          left: 0;
          right: 0;
          top: 50%;
          height: 1px;
          background: #e5e7eb;
        }

        .divider span {
          position: relative;
          background: rgba(255, 255, 255, 0.95);
          padding: 0 16px;
          font-size: 14px;
          color: var(--muted);
        }

        .line-login-btn {
          width: 100%;
          padding: 14px;
          background: #00c300;
          color: white;
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

        .line-login-btn:hover {
          background: #00b300;
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(0, 195, 0, 0.3);
        }

        .line-icon {
          font-size: 20px;
        }

        @media (max-width: 480px) {
          .login-card {
            padding: 30px 20px;
          }

          .demo-buttons {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default LoginPage;
