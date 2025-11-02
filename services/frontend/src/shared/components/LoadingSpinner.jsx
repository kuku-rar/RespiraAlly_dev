const LoadingSpinner = ({
  fullScreen = false,
  size = "medium",
  message = "載入中...",
}) => {
  const sizeClasses = {
    small: "spinner-small",
    medium: "spinner-medium",
    large: "spinner-large",
  };

  if (fullScreen) {
    return (
      <div className="spinner-overlay">
        <div className="spinner-container">
          <div className={`spinner ${sizeClasses[size]}`} />
          {message && <p className="spinner-message">{message}</p>}
        </div>
        <style jsx>{`
          .spinner-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
          }

          .spinner-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
          }

          .spinner {
            border: 3px solid rgba(124, 198, 255, 0.2);
            border-top-color: #7cc6ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
          }

          .spinner-small {
            width: 20px;
            height: 20px;
            border-width: 2px;
          }

          .spinner-medium {
            width: 40px;
            height: 40px;
          }

          .spinner-large {
            width: 60px;
            height: 60px;
            border-width: 4px;
          }

          .spinner-message {
            color: #6b7280;
            font-size: 14px;
            margin: 0;
          }

          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="spinner-wrapper">
      <div className={`spinner ${sizeClasses[size]}`} />
      {message && <p className="spinner-message">{message}</p>}
      <style jsx>{`
        .spinner-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .spinner {
          border: 3px solid rgba(124, 198, 255, 0.2);
          border-top-color: #7cc6ff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        .spinner-small {
          width: 20px;
          height: 20px;
          border-width: 2px;
        }

        .spinner-medium {
          width: 40px;
          height: 40px;
        }

        .spinner-large {
          width: 60px;
          height: 60px;
          border-width: 4px;
        }

        .spinner-message {
          color: #6b7280;
          font-size: 14px;
          margin-top: 12px;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
