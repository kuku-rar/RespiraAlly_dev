import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { API_ENDPOINTS, ENABLE_MOCK } from "../config";
import { mockTasks } from "../utils/mockTasks";

// 取得任務列表
export const useTasks = (params = {}) => {
  return useQuery({
    queryKey: ["tasks", params],
    queryFn: async () => {
      if (ENABLE_MOCK) return mockTasks;
      const queryString = new URLSearchParams(params).toString();
      const response = await apiClient.get(`${API_ENDPOINTS.TASKS}?${queryString}`);
      // 確保回傳的是陣列資料，而非整個回應物件
      return response?.data || [];
    },
    staleTime: 5 * 60 * 1000,
  });
};

// 建立任務
export const useCreateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => {
      if (ENABLE_MOCK) {
        const newTask = {
          id: `task_${Date.now()}`,
          ...data,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        mockTasks.push(newTask);
        return newTask;
      }
      const response = await apiClient.post(API_ENDPOINTS.TASKS, data);
      return response?.data || {};
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
};

// 更新任務
export const useUpdateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, patch }) => {
      if (ENABLE_MOCK) {
        const index = mockTasks.findIndex((t) => t.id === id);
        if (index !== -1) {
          mockTasks[index] = { ...mockTasks[index], ...patch };
          return mockTasks[index];
        }
        throw new Error("Task not found");
      }
      const response = await apiClient.put(API_ENDPOINTS.TASK_DETAIL(id), patch);
      return response?.data || {};
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
};

// 刪除任務
export const useDeleteTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      if (ENABLE_MOCK) {
        const index = mockTasks.findIndex((t) => t.id === id);
        if (index !== -1) {
          mockTasks.splice(index, 1);
          return true;
        }
        throw new Error("Task not found");
      }
      const response = await apiClient.delete(API_ENDPOINTS.TASK_DETAIL(id));
      return response?.data || {};
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
};
