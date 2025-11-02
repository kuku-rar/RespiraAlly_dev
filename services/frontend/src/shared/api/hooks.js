import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { API_ENDPOINTS, FLAGS, ENABLE_MOCK } from "../config";
import {
  mockPatients,
  mockKpis,
  mockTrends,
  mockAdherence,
} from "../utils/mock";

// ==================== 病患相關 ====================

// 取得治療師的病患列表
export const usePatients = (params = {}) => {
  return useQuery({
    queryKey: ["patients", params],
    queryFn: async () => {
      if (ENABLE_MOCK) return Promise.resolve(mockPatients);

      // 過濾掉 undefined 和空字符串的參數
      const filteredParams = Object.fromEntries(
        Object.entries(params).filter(
          ([, value]) => value !== undefined && value !== null && value !== ""
        )
      );

      const queryString = new URLSearchParams(filteredParams).toString();
      const response = await apiClient.get(
        `${API_ENDPOINTS.THERAPIST_PATIENTS}?${queryString}`
      );

      // 確保回應格式正確並包含數據陣列
      if (!response || typeof response !== 'object') {
        console.warn('⚠️ API回應格式異常:', response);
        return [];
      }

      // 從回應中提取患者陣列，支援多種可能的回應格式
      let patients = [];
      if (Array.isArray(response.data)) {
        patients = response.data;
      } else if (Array.isArray(response)) {
        patients = response;
      } else {
        console.warn('⚠️ 患者資料不是陣列格式:', response);
        return [];
      }

      // 確保每個患者都有正確的ID欄位，統一使用user_id
      const processedPatients = patients.map(patient => {
        if (!patient || typeof patient !== 'object') {
          console.warn('⚠️ 發現無效的患者資料:', patient);
          return null;
        }
        return {
          ...patient,
          id: patient.user_id || patient.id, // 統一使用user_id，避免ID為undefined
          name: patient.first_name && patient.last_name
            ? `${patient.first_name} ${patient.last_name}`
            : patient.name || '未知',
        };
      }).filter(Boolean); // 過濾掉null值

      return processedPatients;
    },
    staleTime: 5 * 60 * 1000,
  });
};

// 取得病患檔案
export const usePatientProfile = (id) => {
  return useQuery({
    queryKey: ["patient-profile", id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.PATIENT_PROFILE(id));
      return response?.data || {};
    },
    enabled: !!id,
  });
};

// 取得病患每日健康指標 - 增強版（支援日期範圍、分頁）
export const usePatientMetrics = (id, params = {}) => {
  return useQuery({
    queryKey: ["patient-metrics", id, params],
    queryFn: async () => {
      if (!id || id === 'undefined') {
        console.error('❌ Patient ID is invalid for metrics:', id);
        return { data: [], pagination: {} };
      }

      try {
        // 清理並處理參數
        const cleanParams = {};
        if (params.start_date) cleanParams.start_date = params.start_date;
        if (params.end_date) cleanParams.end_date = params.end_date;
        if (params.page) cleanParams.page = params.page;
        if (params.per_page) cleanParams.per_page = params.per_page;

        const queryString = new URLSearchParams(cleanParams).toString();
        const response = await apiClient.get(
          `${API_ENDPOINTS.PATIENT_DAILY_METRICS(id)}?${queryString}`
        );
        
        console.log('📊 每日記錄API回應:', response);
        
        // 統一回應格式：{ data: [], pagination: {} }
        const responseData = Array.isArray(response?.data) ? response.data : [];
        return {
          data: responseData,
          pagination: response?.pagination || {}
        };
      } catch (error) {
        console.warn('⚠️ 每日指標API錯誤:', error.message);
        return { data: [], pagination: {} };
      }
    },
    enabled: !!id && id !== 'undefined',
    retry: 1,
    staleTime: 30000, // 30秒快取
  });
};

// 取得 CAT 歷史記錄
export const useCatHistory = (id, params = {}) => {
  return useQuery({
    queryKey: ["cat", id, params],
    queryFn: async () => {
      try {
        const queryString = new URLSearchParams(params).toString();
        const response = await apiClient.get(
          `${API_ENDPOINTS.PATIENT_CAT(id)}?${queryString}`
        );
        
        // 確保返回的是陣列
        const data = response?.data;
        if (Array.isArray(data)) {
          return data;
        } else {
          console.warn('⚠️ CAT API 回應不是陣列格式:', response);
          return [];
        }
      } catch (error) {
        console.warn('⚠️ CAT API 錯誤:', error.message);
        return [];
      }
    },
    enabled: !!id,
    retry: 1,
  });
};

// 取得 mMRC 歷史記錄
export const useMmrcHistory = (id, params = {}) => {
  return useQuery({
    queryKey: ["mmrc", id, params],
    queryFn: async () => {
      try {
        const queryString = new URLSearchParams(params).toString();
        const response = await apiClient.get(
          `${API_ENDPOINTS.PATIENT_MMRC(id)}?${queryString}`
        );
        
        // 確保返回的是陣列
        const data = response?.data;
        if (Array.isArray(data)) {
          return data;
        } else {
          console.warn('⚠️ MMRC API 回應不是陣列格式:', response);
          return [];
        }
      } catch (error) {
        console.warn('⚠️ MMRC API 錯誤:', error.message);
        return [];
      }
    },
    enabled: !!id,
    retry: 1,
  });
};

// ==================== 總覽相關（缺項，使用 Mock） ====================

// 總覽 KPI
export const useOverviewKpis = (params = {}) => {
  return useQuery({
    queryKey: ["overview-kpis", params],
    queryFn: async () => {
      if (!FLAGS.OVERVIEW_READY || ENABLE_MOCK) {
        return Promise.resolve(mockKpis);
      }
      const queryString = new URLSearchParams(params).toString();
      const response = await apiClient.get(
        `${API_ENDPOINTS.OVERVIEW_KPIS}?${queryString}`
      );
      return response?.data || {};
    },
  });
};

// 總覽趨勢
export const useOverviewTrends = (params = {}) => {
  return useQuery({
    queryKey: ["overview-trends", params],
    queryFn: async () => {
      if (!FLAGS.OVERVIEW_READY || ENABLE_MOCK) {
        return Promise.resolve(mockTrends);
      }
      const queryString = new URLSearchParams(params).toString();
      const response = await apiClient.get(
        `${API_ENDPOINTS.OVERVIEW_TRENDS}?${queryString}`
      );
      return response?.data || {};
    },
  });
};

// 總覽依從性
export const useOverviewAdherence = (params = {}) => {
  return useQuery({
    queryKey: ["overview-adherence", params],
    queryFn: async () => {
      if (!FLAGS.OVERVIEW_READY || ENABLE_MOCK) {
        return Promise.resolve(mockAdherence);
      }
      const queryString = new URLSearchParams(params).toString();
      const response = await apiClient.get(
        `${API_ENDPOINTS.OVERVIEW_ADHERENCE}?${queryString}`
      );
      return response?.data || {};
    },
  });
};

// 個案 KPI - 使用專用 API 端點
export const usePatientKpis = (id, params = {}) => {
  return useQuery({
    queryKey: ["patient-kpis", id, params],
    queryFn: async () => {
      if (!id || id === 'undefined') {
        console.error('❌ Patient ID is invalid:', id);
        return {
          cat_latest: 0,
          mmrc_latest: 0,
          adherence_7d: 0,
          report_rate_7d: 0,
          completion_7d: 0,
          last_report_days: 999,
          risk_level: 'low',
          metrics_summary: {}
        };
      }

      try {
        console.log('📊 使用專用KPI API，ID:', id);
        
        // 使用專用的 KPI API 端點
        if (FLAGS.PATIENT_KPIS_READY) {
          const days = params.days || 7;
          const queryString = new URLSearchParams({ days }).toString();
          const response = await apiClient.get(
            `${API_ENDPOINTS.PATIENT_KPIS(id)}?${queryString}`
          );
          
          console.log('✅ 專用KPI API回應:', response?.data || {});
          return response?.data || {};
        }
        
        // 如果專用 API 未就緒，回退到計算模式（舊邏輯保留作為備案）
        console.log('⚠️ 專用KPI API未就緒，使用計算模式');
        
        // 嘗試從患者檔案獲取基本資訊
        const profileResponse = await apiClient.get(API_ENDPOINTS.PATIENT_PROFILE(id));
        console.log('📋 患者檔案:', profileResponse ? '✅' : '❌');

        // 從其他API獲取數據進行計算
        const apiCalls = await Promise.allSettled([
          apiClient.get(API_ENDPOINTS.PATIENT_CAT(id)),
          apiClient.get(API_ENDPOINTS.PATIENT_MMRC(id)),
          apiClient.get(API_ENDPOINTS.PATIENT_DAILY_METRICS(id)),
        ]);

        // 安全地提取資料，確保都是陣列
        const catData = apiCalls[0].status === 'fulfilled'
          ? Array.isArray(apiCalls[0].value?.data) ? apiCalls[0].value.data : []
          : [];
        const mmrcData = apiCalls[1].status === 'fulfilled'
          ? Array.isArray(apiCalls[1].value?.data) ? apiCalls[1].value.data : []
          : [];
        const metricsData = apiCalls[2].status === 'fulfilled'
          ? Array.isArray(apiCalls[2].value?.data) ? apiCalls[2].value.data : []
          : [];

        const latestCat = catData?.[0]?.total_score || 0;
        const latestMmrc = mmrcData?.[0]?.score || 0;

        const last7Days = metricsData?.slice(0, 7) || [];
        const adherence7d = last7Days.length > 0
          ? last7Days.filter((d) => d.medication).length / last7Days.length
          : 0;

        const kpiResult = {
          cat_latest: latestCat,
          mmrc_latest: latestMmrc,
          adherence_7d: adherence7d,
          report_rate_7d: last7Days.length / 7,
          completion_7d: 0.75, // 臨時值
          last_report_days: last7Days.length > 0 ? 0 : 999,
          risk_level: 'low', // 臨時值
          metrics_summary: {
            total_records: last7Days.length,
            medication_taken_days: last7Days.filter((d) => d.medication).length
          }
        };

        console.log('✅ 計算完成的KPI:', kpiResult);
        return kpiResult;

      } catch (error) {
        console.error('❌ KPI獲取失敗:', error);
        return {
          cat_latest: 0,
          mmrc_latest: 0,
          adherence_7d: 0,
          report_rate_7d: 0,
          completion_7d: 0,
          last_report_days: 999,
          risk_level: 'low',
          metrics_summary: {}
        };
      }
    },
    enabled: !!id && id !== 'undefined',
    retry: 1,
    staleTime: 60000, // 1分鐘快取
  });
};

// ==================== 問卷相關 ====================

// 提交 CAT 問卷
export const useSubmitCat = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, data }) =>
      apiClient.post(API_ENDPOINTS.PATIENT_CAT(patientId), data),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({ queryKey: ["cat", patientId] });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// 提交 mMRC 問卷
export const useSubmitMmrc = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, data }) =>
      apiClient.post(API_ENDPOINTS.PATIENT_MMRC(patientId), data),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({ queryKey: ["mmrc", patientId] });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// 更新指定月份的 CAT 問卷
export const useUpdateCat = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, year, month, data }) =>
      apiClient.put(`${API_ENDPOINTS.PATIENT_CAT(patientId)}/${year}/${month}`, data),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({ queryKey: ["cat", patientId] });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// 更新指定月份的 mMRC 問卷
export const useUpdateMmrc = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, year, month, data }) =>
      apiClient.put(`${API_ENDPOINTS.PATIENT_MMRC(patientId)}/${year}/${month}`, data),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({ queryKey: ["mmrc", patientId] });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// ==================== 每日健康記錄 ====================

// 新增每日健康記錄
export const useCreateDailyMetric = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, data }) =>
      apiClient.post(API_ENDPOINTS.PATIENT_DAILY_METRICS(patientId), data),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({
        queryKey: ["patient-metrics", patientId],
      });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// 更新指定日期的每日健康記錄 - 使用正確的 API 路徑
export const useUpdateDailyMetric = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ patientId, logDate, data }) =>
      apiClient.put(
        `${API_ENDPOINTS.PATIENT_DAILY_METRICS(patientId)}/${logDate}`,
        data
      ),
    onSuccess: (_, { patientId }) => {
      queryClient.invalidateQueries({
        queryKey: ["patient-metrics", patientId],
      });
      queryClient.invalidateQueries({ queryKey: ["patient-kpis", patientId] });
    },
  });
};

// 獲取指定日期範圍的每日記錄（便利函數）
export const usePatientMetricsRange = (id, startDate, endDate) => {
  return usePatientMetrics(id, {
    start_date: startDate,
    end_date: endDate,
    per_page: 100 // 取得範圍內所有記錄
  });
};

// 獲取最近 N 天的每日記錄（便利函數）
export const usePatientMetricsRecent = (id, days = 7) => {
  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - (days - 1) * 24 * 60 * 60 * 1000)
    .toISOString().split('T')[0];
  
  return usePatientMetricsRange(id, startDate, endDate);
};

// ==================== 通報相關 ====================

// AI 通報列表 - 使用真實 API
export const useAlerts = (params = {}) => {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: async () => {
      if (!FLAGS.AI_ALERTS_READY) {
        // Mock 通報
        return {
          data: [
            {
              id: "a1",
              created_at: new Date().toISOString(),
              level: "warning",
              category: "adherence",
              message: "病患王小明近7日用藥遵從率下降 >20%",
              is_read: false,
              patient_id: 63
            },
            {
              id: "a2",
              created_at: new Date().toISOString(),
              level: "info",
              category: "health",
              message: "病患李大華 CAT 分數改善顯著",
              is_read: false,
              patient_id: 65
            },
          ],
          pagination: { total_items: 2 },
          summary: { unread_count: 2 }
        };
      }

      try {
        // 清理參數
        const cleanParams = {};
        if (params.level) cleanParams.level = params.level;
        if (params.category) cleanParams.category = params.category;
        if (params.unread_only) cleanParams.unread_only = params.unread_only;
        if (params.since) cleanParams.since = params.since;
        if (params.page) cleanParams.page = params.page;
        if (params.per_page) cleanParams.per_page = params.per_page;

        const queryString = new URLSearchParams(cleanParams).toString();
        const response = await apiClient.get(
          `${API_ENDPOINTS.ALERTS}?${queryString}`
        );
        
        console.log('🚨 通報API回應:', response);
        
        // 確保回應格式正確
        if (!response || typeof response !== 'object') {
          console.warn('⚠️ 通報API回應格式異常:', response);
          return { data: [], pagination: {}, summary: {} };
        }

        // 確保 data 是陣列
        const alertData = Array.isArray(response.data) ? response.data : [];
        
        return {
          data: alertData,
          pagination: response.pagination || {},
          summary: response.summary || {}
        };
        
      } catch (error) {
        console.warn('⚠️ 通報API錯誤:', error.message);
        return { data: [], pagination: {}, summary: {} };
      }
    },
    refetchInterval: FLAGS.AI_ALERTS_READY ? 30000 : false, // 30 秒輪詢
    staleTime: 10000, // 10秒快取
  });
};

// 標記通報為已讀
export const useMarkAlertRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId) =>
      apiClient.put(API_ENDPOINTS.ALERT_READ(alertId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

// 批量標記通報為已讀
export const useBatchMarkAlertsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertIds) =>
      apiClient.put(API_ENDPOINTS.ALERTS_BATCH_READ, { alert_ids: alertIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

// 只取得未讀通報（便利函數）
export const useUnreadAlerts = () => {
  return useAlerts({ unread_only: true });
};

// 取得指定等級的通報（便利函數）
export const useAlertsByLevel = (level) => {
  return useAlerts({ level });
};
