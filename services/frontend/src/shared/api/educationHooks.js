// services/web-app/frontend/src/shared/api/educationHooks.js
/**
 * Education API Hooks
 * 管理衛教資源的 CRUD 操作
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { API_ENDPOINTS } from "../config";

// ==================== 查詢 Hooks ====================

/**
 * 取得衛教資源列表
 * @param {Object} params - 查詢參數
 * @param {string} params.category - 篩選類別
 * @param {string} params.q - 搜尋關鍵字
 * @param {number} params.limit - 返回數量上限
 */
export const useEducationList = (params = {}) => {
  return useQuery({
    queryKey: ["education", params],
    queryFn: async () => {
      const queryString = new URLSearchParams(params).toString();
      const response = await apiClient.get(`/education?${queryString}`);
      return response.data || [];
    },
    staleTime: 5 * 60 * 1000, // 5 分鐘
    cacheTime: 10 * 60 * 1000, // 10 分鐘
  });
};

/**
 * 取得所有衛教資源類別
 */
export const useEducationCategories = () => {
  return useQuery({
    queryKey: ["education-categories"],
    queryFn: async () => {
      const response = await apiClient.get("/education/categories");
      return response.data || [];
    },
    staleTime: 30 * 60 * 1000, // 30 分鐘（類別不常變動）
  });
};

// ==================== Mutation Hooks ====================

/**
 * 新增衛教資源
 */
export const useCreateEducation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => {
      const response = await apiClient.post("/education", data);
      return response.data;
    },
    onSuccess: () => {
      // 清除快取，強制重新載入
      queryClient.invalidateQueries({ queryKey: ["education"] });
      queryClient.invalidateQueries({ queryKey: ["education-categories"] });
    },
    onError: (error) => {
      console.error("Error creating education item:", error);
      throw error;
    },
  });
};

/**
 * 更新衛教資源
 */
export const useUpdateEducation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await apiClient.put(`/education/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      // 清除快取，強制重新載入
      queryClient.invalidateQueries({ queryKey: ["education"] });
    },
    onError: (error) => {
      console.error("Error updating education item:", error);
      throw error;
    },
  });
};

/**
 * 刪除衛教資源
 */
export const useDeleteEducation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const response = await apiClient.delete(`/education/${id}`);
      return response;
    },
    onSuccess: () => {
      // 清除快取，強制重新載入
      queryClient.invalidateQueries({ queryKey: ["education"] });
      queryClient.invalidateQueries({ queryKey: ["education-categories"] });
    },
    onError: (error) => {
      console.error("Error deleting education item:", error);
      throw error;
    },
  });
};

/**
 * 批量匯入衛教資源
 */
export const useBatchImportEducation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file) => {
      // 使用統一的 uploadFile 方法，避免直接拼接 URL
      const formData = new FormData();
      formData.append("file", file);

      // 使用相對路徑，讓 Vite 的 proxy 或部署環境來處理完整 URL
      const token =
        localStorage.getItem("token") || sessionStorage.getItem("token");
      
      const response = await fetch("/api/education/batch", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "批量匯入失敗");
      }

      return response.json();
    },
    onSuccess: () => {
      // 清除快取，強制重新載入
      queryClient.invalidateQueries({ queryKey: ["education"] });
      queryClient.invalidateQueries({ queryKey: ["education-categories"] });
    },
    onError: (error) => {
      console.error("Error batch importing education items:", error);
      throw error;
    },
  });
};

/**
 * 匯出衛教資源為 CSV
 * 注意：這是純前端操作，不需要 API
 */
export const exportEducationToCSV = (data) => {
  // 準備 CSV 內容
  const headers = ["類別", "問題", "回答", "關鍵詞", "注意事項"];
  const rows = data.map((item) => [
    item.category || "",
    item.question || "",
    item.answer || "",
    item.keywords || "",
    item.notes || "",
  ]);

  // 組合 CSV 字串（處理包含逗號的欄位）
  const csvContent = [
    headers.join(","),
    ...rows.map((row) =>
      row
        .map((cell) => {
          // 如果包含逗號、換行或引號，需要用引號包起來
          if (cell.includes(",") || cell.includes("\n") || cell.includes('"')) {
            return `"${cell.replace(/"/g, '""')}"`;
          }
          return cell;
        })
        .join(",")
    ),
  ].join("\n");

  // 加入 BOM 以支援中文
  const BOM = "\uFEFF";
  const blob = new Blob([BOM + csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  // 建立下載連結
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute(
    "download",
    `copd_qa_${new Date().toISOString().split("T")[0]}.csv`
  );
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // 釋放 URL 物件
  URL.revokeObjectURL(url);
};
