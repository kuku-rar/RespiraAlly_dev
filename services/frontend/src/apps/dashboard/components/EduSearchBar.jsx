const EduSearchBar = ({ value, onChange }) => {
  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          className="search-input"
          placeholder="搜尋問題或答案關鍵字..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        {value && (
          <button className="clear-btn" onClick={() => onChange("")}>
            ✕
          </button>
        )}
      </div>

      <style jsx>{`
        .search-bar {
          margin-bottom: 16px;
        }

        .search-input-wrapper {
          position: relative;
          max-width: 600px;
        }

        .search-icon {
          position: absolute;
          left: 16px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 18px;
        }

        .search-input {
          width: 100%;
          padding: 12px 48px 12px 48px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          font-size: 16px;
          background: white;
          transition: all 200ms;
        }

        .search-input:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(124, 198, 255, 0.1);
        }

        .clear-btn {
          position: absolute;
          right: 16px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: var(--muted);
          font-size: 18px;
          cursor: pointer;
          padding: 4px;
          transition: color 200ms;
        }

        .clear-btn:hover {
          color: var(--text);
        }
      `}</style>
    </div>
  );
};

export default EduSearchBar;
