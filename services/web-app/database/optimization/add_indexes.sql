-- RespiraAlly Dashboard 索引優化腳本
-- 執行此腳本以新增缺失的索引和物化視圖
-- 執行方式：在容器內執行 psql -U respirally -d respirally -f add_indexes.sql

-- ============================================
-- 1. 為 tasks 表新增索引
-- ============================================

-- 優化治療師查詢任務（根據狀態篩選）
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_status 
ON tasks(assignee_id, status);

-- 優化時間排序查詢
CREATE INDEX IF NOT EXISTS idx_tasks_due_date 
ON tasks(due_date);

-- 優化病患相關任務查詢
CREATE INDEX IF NOT EXISTS idx_tasks_patient 
ON tasks(patient_id) 
WHERE patient_id IS NOT NULL;

-- 優化建立時間排序
CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
ON tasks(created_at DESC);

-- ============================================
-- 2. 為 alert_notifications 表新增索引
-- ============================================

-- 優化未讀通報查詢（部分索引）
CREATE INDEX IF NOT EXISTS idx_alerts_therapist_unread 
ON alert_notifications(therapist_id, is_read) 
WHERE is_read = FALSE;

-- 優化時間排序查詢
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alert_notifications(created_at DESC);

-- 優化警示等級篩選
CREATE INDEX IF NOT EXISTS idx_alerts_level 
ON alert_notifications(level);

-- 優化病患相關通報查詢
CREATE INDEX IF NOT EXISTS idx_alerts_patient_id 
ON alert_notifications(patient_id) 
WHERE patient_id IS NOT NULL;

-- ============================================
-- 3. 為現有表補充索引（根據架構文件建議）
-- ============================================

-- users 表
CREATE INDEX IF NOT EXISTS idx_users_is_staff 
ON users(is_staff);

CREATE INDEX IF NOT EXISTS idx_users_created_at 
ON users(created_at DESC);

-- health_profiles 表
CREATE INDEX IF NOT EXISTS idx_health_profiles_staff_id 
ON health_profiles(staff_id) 
WHERE staff_id IS NOT NULL;

-- daily_metrics 表（個人時序查詢）
CREATE INDEX IF NOT EXISTS idx_daily_metrics_user_date 
ON daily_metrics(user_id, created_at DESC);

-- questionnaire_cat 表
CREATE INDEX IF NOT EXISTS idx_cat_user_date 
ON questionnaire_cat(user_id, record_date DESC);

CREATE INDEX IF NOT EXISTS idx_cat_total_score 
ON questionnaire_cat(total_score);

-- questionnaire_mmrc 表
CREATE INDEX IF NOT EXISTS idx_mmrc_user_date 
ON questionnaire_mmrc(user_id, record_date DESC);

-- ============================================
-- 4. 建立物化視圖 - 病患風險評估
-- ============================================

DROP MATERIALIZED VIEW IF EXISTS v_patient_risk_assessment CASCADE;

CREATE MATERIALIZED VIEW v_patient_risk_assessment AS
WITH latest_scores AS (
    SELECT DISTINCT ON (user_id)
        user_id,
        total_score as cat_score,
        record_date as cat_date
    FROM questionnaire_cat
    ORDER BY user_id, record_date DESC
),
latest_mmrc AS (
    SELECT DISTINCT ON (user_id)
        user_id,
        score as mmrc_score,
        record_date as mmrc_date
    FROM questionnaire_mmrc
    ORDER BY user_id, record_date DESC
),
adherence_stats AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE medication = true) * 100.0 / NULLIF(COUNT(*), 0) as adherence_rate,
        COUNT(*) as report_count,
        MAX(created_at) as last_report
    FROM daily_metrics
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY user_id
)
SELECT
    u.id as patient_id,
    u.first_name,
    u.last_name,
    hp.staff_id,
    ls.cat_score,
    ls.cat_date,
    lm.mmrc_score,
    lm.mmrc_date,
    COALESCE(ads.adherence_rate, 0) as adherence_rate_7d,
    COALESCE(ads.report_count, 0) as report_count_7d,
    ads.last_report,
    CASE
        WHEN ls.cat_score >= 10 OR lm.mmrc_score >= 2 THEN 'high'
        WHEN ads.adherence_rate < 50 THEN 'medium'
        ELSE 'low'
    END as risk_level,
    NOW() as calculated_at
FROM users u
LEFT JOIN health_profiles hp ON u.id = hp.user_id
LEFT JOIN latest_scores ls ON u.id = ls.user_id
LEFT JOIN latest_mmrc lm ON u.id = lm.user_id
LEFT JOIN adherence_stats ads ON u.id = ads.user_id
WHERE u.is_staff = FALSE;

-- 建立物化視圖的索引
CREATE INDEX idx_mv_risk_assessment_staff 
ON v_patient_risk_assessment(staff_id);

CREATE INDEX idx_mv_risk_assessment_risk 
ON v_patient_risk_assessment(risk_level);

CREATE INDEX idx_mv_risk_assessment_patient 
ON v_patient_risk_assessment(patient_id);

-- ============================================
-- 5. 建立系統 KPI 物化視圖
-- ============================================

DROP MATERIALIZED VIEW IF EXISTS v_system_kpis CASCADE;

CREATE MATERIALIZED VIEW v_system_kpis AS
SELECT
    COUNT(DISTINCT u.id) as total_patients,
    COUNT(DISTINCT CASE WHEN pr.risk_level = 'high' THEN u.id END) as high_risk_count,
    COUNT(DISTINCT CASE WHEN pr.adherence_rate_7d < 50 THEN u.id END) as low_adherence_count,
    AVG(pr.cat_score)::NUMERIC(5,2) as avg_cat_score,
    AVG(pr.mmrc_score)::NUMERIC(5,2) as avg_mmrc_score,
    COUNT(DISTINCT CASE WHEN pr.risk_level = 'high' THEN u.id END) * 100.0 / NULLIF(COUNT(DISTINCT u.id), 0) as high_risk_pct,
    COUNT(DISTINCT CASE WHEN pr.adherence_rate_7d < 50 THEN u.id END) * 100.0 / NULLIF(COUNT(DISTINCT u.id), 0) as low_adherence_pct,
    NOW() as calculated_at
FROM users u
LEFT JOIN v_patient_risk_assessment pr ON u.id = pr.patient_id
WHERE u.is_staff = FALSE;

-- ============================================
-- 6. 建立資料庫觸發器以支援快取失效
-- ============================================

-- 建立通知函數
CREATE OR REPLACE FUNCTION notify_cache_invalidation()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'cache_invalidation',
        json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'id', COALESCE(NEW.id, OLD.id),
            'timestamp', NOW()
        )::text
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 為各表建立觸發器
CREATE TRIGGER invalidate_tasks_cache
AFTER INSERT OR UPDATE OR DELETE ON tasks
FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidation();

CREATE TRIGGER invalidate_alerts_cache
AFTER INSERT OR UPDATE OR DELETE ON alert_notifications
FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidation();

CREATE TRIGGER invalidate_daily_metrics_cache
AFTER INSERT OR UPDATE OR DELETE ON daily_metrics
FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidation();

CREATE TRIGGER invalidate_questionnaire_cat_cache
AFTER INSERT OR UPDATE OR DELETE ON questionnaire_cat
FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidation();

CREATE TRIGGER invalidate_questionnaire_mmrc_cache
AFTER INSERT OR UPDATE OR DELETE ON questionnaire_mmrc
FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidation();

-- ============================================
-- 7. 建立物化視圖自動更新函數
-- ============================================

CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY v_patient_risk_assessment;
    REFRESH MATERIALIZED VIEW CONCURRENTLY v_system_kpis;
END;
$$ LANGUAGE plpgsql;

-- 注意：需要在應用程式中設定定時任務來執行此函數
-- 建議使用 APScheduler 或 cron 每 30 分鐘執行一次：
-- SELECT refresh_materialized_views();

-- ============================================
-- 驗證索引建立狀態
-- ============================================

-- 執行此查詢來確認所有索引都已建立
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('users', 'tasks', 'alert_notifications', 'daily_metrics', 'questionnaire_cat', 'questionnaire_mmrc', 'health_profiles')
ORDER BY tablename, indexname;

-- 查看物化視圖狀態
SELECT 
    schemaname,
    matviewname,
    hasindexes,
    ispopulated,
    definition
FROM pg_matviews
WHERE schemaname = 'public';

-- ============================================
-- 完成訊息
-- ============================================
SELECT '索引和物化視圖建立完成！' as message;
