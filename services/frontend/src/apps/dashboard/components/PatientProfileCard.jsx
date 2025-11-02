import dayjs from "dayjs";

const PatientProfileCard = ({ profile }) => {
  if (!profile) return null;

  const infoItems = [
    { label: "性別", value: profile.gender === "M" ? "男性" : "女性" },
    { label: "年齡", value: `${dayjs().diff(profile.birth_date, "year")}歲` },
    { label: "電話", value: profile.phone || "未提供" },
    { label: "Email", value: profile.email || "未提供" },
    { label: "地址", value: profile.address || "未提供" },
    { label: "緊急聯絡人", value: profile.emergency_contact || "未提供" },
    { label: "緊急電話", value: profile.emergency_phone || "未提供" },
    { label: "病歷號", value: profile.medical_record_number || "未提供" },
  ];

  const medicalInfo = [
    { label: "診斷", value: profile.diagnosis || "未提供" },
    {
      label: "診斷日期",
      value: profile.diagnosis_date
        ? dayjs(profile.diagnosis_date).format("YYYY/MM/DD")
        : "未提供",
    },
    {
      label: "吸菸史",
      value: profile.smoking_history || "未提供",
    },
  ];

  return (
    <div className="profile-card">
      <div className="card-header">
        <div className="avatar">
          <span>{profile.name?.[0] || "?"}</span>
        </div>
        <div className="header-info">
          <h3 className="patient-name">{profile.name}</h3>
          <p className="patient-id">ID: {profile.id}</p>
        </div>
      </div>

      <div className="info-section">
        <h4 className="section-title">基本資料</h4>
        <div className="info-grid">
          {infoItems.map((item) => (
            <div key={item.label} className="info-item">
              <span className="info-label">{item.label}</span>
              <span className="info-value">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <h4 className="section-title">醫療資訊</h4>
        <div className="info-grid">
          {medicalInfo.map((item) => (
            <div key={item.label} className="info-item">
              <span className="info-label">{item.label}</span>
              <span className="info-value">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 用藥資訊 */}
      {profile.medications && profile.medications.length > 0 && (
        <div className="info-section">
          <h4 className="section-title">目前用藥</h4>
          <div className="medication-list">
            {profile.medications.map((med, index) => (
              <div key={index} className="medication-item">
                <span className="med-name">{med.name}</span>
                <span className="med-dosage">
                  {med.dosage} - {med.frequency}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 過敏史 */}
      {profile.allergies && profile.allergies.length > 0 && (
        <div className="info-section">
          <h4 className="section-title">過敏史</h4>
          <div className="allergy-list">
            {profile.allergies.map((allergy, index) => (
              <span key={index} className="allergy-tag">
                {allergy}
              </span>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .profile-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .card-header {
          display: flex;
          align-items: center;
          gap: 16px;
          padding-bottom: 20px;
          border-bottom: 1px solid #f3f4f6;
          margin-bottom: 20px;
        }

        .avatar {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: linear-gradient(135deg, #7cc6ff, #cba6ff);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 24px;
          font-weight: 600;
        }

        .header-info {
          flex: 1;
        }

        .patient-name {
          font-size: 20px;
          font-weight: 600;
          color: var(--text);
          margin: 0 0 4px 0;
        }

        .patient-id {
          font-size: 14px;
          color: var(--muted);
          margin: 0;
        }

        .info-section {
          margin-bottom: 20px;
        }

        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .info-grid {
          display: grid;
          gap: 12px;
        }

        .info-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #f9fafb;
        }

        .info-label {
          font-size: 13px;
          color: var(--muted);
        }

        .info-value {
          font-size: 13px;
          color: var(--text);
          font-weight: 500;
          text-align: right;
        }

        .medication-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .medication-item {
          padding: 8px 12px;
          background: #f9fafb;
          border-radius: 8px;
        }

        .med-name {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: var(--text);
        }

        .med-dosage {
          display: block;
          font-size: 12px;
          color: var(--muted);
          margin-top: 2px;
        }

        .allergy-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .allergy-tag {
          padding: 4px 12px;
          background: #fee2e2;
          color: #dc2626;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default PatientProfileCard;
