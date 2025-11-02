# ===============================================
# 建置 React 前端
# ===============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# 複製前端相關檔案
COPY . .

# 安裝所有依賴（包括 devDependencies，因為 vite 是開發依賴）
RUN npm install

# 設定建置時的環境變數（使用 ARG 傳入）
ARG LIFF_CHANNEL_ID
ARG LINE_CHANNEL_SECRET
ARG LINE_CHANNEL_ACCESS_TOKEN
ARG VITE_API_BASE_URL

# 建置前端，環境變數會自動被 Vite 讀取
ENV LIFF_CHANNEL_ID=${LIFF_CHANNEL_ID}
ENV LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
ENV LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

CMD ["npm", "run", "dev"]
