import { API_BASE_URL } from "../config";

// 取得 Token
const getToken = () => {
  return localStorage.getItem("token") || sessionStorage.getItem("token");
};

// 設定 Token
export const setToken = (token, remember = false) => {
  if (remember) {
    localStorage.setItem("token", token);
  } else {
    sessionStorage.setItem("token", token);
  }
};

// 清除 Token
export const clearToken = () => {
  localStorage.removeItem("token");
  sessionStorage.removeItem("token");
};

// API 客戶端
export const api = async (path, options = {}) => {
  const url = `${API_BASE_URL}${path}`;
  const token = getToken();

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    // 處理 204 No Content
    if (response.status === 204) {
      return null;
    }

    // 處理非 2xx 回應
    if (!response.ok) {
      // 401 未授權
      if (response.status === 401) {
        clearToken();
        window.location.href = "/login";
        throw new Error("未授權，請重新登入");
      }

      // 嘗試解析錯誤訊息
      let errorMessage = `請求失敗 (${response.status})`;
      try {
        const errorData = await response.json();
        errorMessage =
          errorData.message || errorData.error?.message || errorMessage;
      } catch {
        // 無法解析 JSON，使用預設錯誤訊息
      }

      throw new Error(errorMessage);
    }

    // 解析成功回應
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    }

    return response;
  } catch (error) {
    // 網路錯誤或其他錯誤
    if (error.message === "Failed to fetch") {
      throw new Error("網路連線失敗，請檢查網路狀態");
    }
    throw error;
  }
};

// 便利方法
export const apiClient = {
  get: (path, options = {}) => api(path, { method: "GET", ...options }),

  post: (path, data, options = {}) =>
    api(path, {
      method: "POST",
      body: JSON.stringify(data),
      ...options,
    }),

  put: (path, data, options = {}) =>
    api(path, {
      method: "PUT",
      body: JSON.stringify(data),
      ...options,
    }),

  patch: (path, data, options = {}) =>
    api(path, {
      method: "PATCH",
      body: JSON.stringify(data),
      ...options,
    }),

  delete: (path, options = {}) => api(path, { method: "DELETE", ...options }),
};

// 檔案上傳
export const uploadFile = async (path, file, onProgress) => {
  const url = `${API_BASE_URL}${path}`;
  const token = getToken();

  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // 進度監聽
    if (onProgress) {
      xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(percentComplete);
        }
      });
    }

    // 完成處理
    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch {
          resolve(xhr.responseText);
        }
      } else {
        reject(new Error(`上傳失敗 (${xhr.status})`));
      }
    });

    // 錯誤處理
    xhr.addEventListener("error", () => {
      reject(new Error("上傳失敗"));
    });

    // 設定請求
    xhr.open("POST", url);
    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }

    // 發送請求
    xhr.send(formData);
  });
};
