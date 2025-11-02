const EduCategoryFilter = ({ categories, selected, onChange }) => {
  return (
    <div className="category-filter">
      <button
        className={`filter-tag ${!selected ? "active" : ""}`}
        onClick={() => onChange("")}
      >
        全部類別
      </button>
      {categories.map((category) => (
        <button
          key={category}
          className={`filter-tag ${selected === category ? "active" : ""}`}
          onClick={() => onChange(category)}
        >
          {category}
        </button>
      ))}

      <style jsx>{`
        .category-filter {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          padding: 16px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .filter-tag {
          padding: 8px 16px;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          background: white;
          font-size: 14px;
          color: var(--text);
          cursor: pointer;
          transition: all 200ms;
          white-space: nowrap;
        }

        .filter-tag:hover {
          background: #f9fafb;
          border-color: var(--primary);
        }

        .filter-tag.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }
      `}</style>
    </div>
  );
};

export default EduCategoryFilter;
