# Voice App - AI Worker 語音處理模組

這個模組提供完整的語音處理功能，包括語音轉文字(STT)、文字轉語音(TTS)和完整的語音聊天流程。

## 檔案結構

```
voice_app/
├── __init__.py                 # 模組初始化檔案
├── voice_worker.py            # RabbitMQ 語音任務處理器
├── voice_flask_app.py         # Flask API 服務
├── run_voice_services.py      # 服務啟動腳本
└── README.md                  # 說明文件
```

## 功能特色

### 1. VoiceWorker (voice_worker.py)

- **RabbitMQ 消費者**：處理語音任務隊列
- **STT 任務處理**：語音轉文字
- **TTS 任務處理**：文字轉語音
- **語音聊天任務**：完整的 STT→LLM→TTS 流程
- **支援隊列回應**：任務完成後發送結果到指定隊列

### 2. Voice Flask API (voice_flask_app.py)

- **Flask RESTful API**：提供 HTTP 端點
- **直接服務調用**：不依賴 RabbitMQ，直接調用服務
- **CORS 支援**：支援跨域請求
- **健康檢查**：服務狀態監控

### 3. 服務啟動器 (run_voice_services.py)

- **多種啟動模式**：Worker、API、或兩者同時
- **Gunicorn 支援**：生產環境使用 Gunicorn
- **命令列參數**：靈活配置主機和端口

## API 端點

### Flask API 端點 (預設端口: 8001)

#### 1. 健康檢查

```
GET /health
```

#### 2. 語音轉文字

```
POST /voice/stt
Content-Type: application/json

{
  "bucket_name": "audio-bucket",
  "object_name": "audio_file.wav",
  "patient_id": "patient_123"
}
```

#### 3. 文字轉語音

```
POST /voice/tts
Content-Type: application/json

{
  "text": "要合成的文字內容",
  "patient_id": "patient_123"
}
```

#### 4. 語音聊天

```
POST /voice/chat
Content-Type: application/json

{
  "bucket_name": "audio-bucket",
  "object_name": "user_voice.wav",
  "patient_id": "patient_123",
  "conversation_id": "conv_123"
}
```

## 使用方式

### 1. 基本啟動

```bash
# 進入voice_app目錄
cd services/ai-worker/worker/voice_app

# 啟動所有服務 (Worker + Flask API)
python run_voice_services.py --service both --host 0.0.0.0 --port 8001

# 僅啟動Worker
python run_voice_services.py --service worker

# 僅啟動Flask API
python run_voice_services.py --service api
```

### 2. 環境變數配置

```bash
# RabbitMQ設定
export RABBITMQ_HOST=rabbitmq

# 語音隊列名稱
export VOICE_STT_QUEUE=voice_stt_queue
export VOICE_TTS_QUEUE=voice_tts_queue
export VOICE_CHAT_QUEUE=voice_chat_queue

# Flask API設定
export VOICE_FLASK_HOST=0.0.0.0
export VOICE_FLASK_PORT=8001
export FLASK_DEBUG=False
```

### 3. Docker 部署

```dockerfile
# 在 AI Worker Dockerfile 中添加
EXPOSE 8001
CMD ["python", "voice_app/run_voice_services.py", "--service", "both"]
```

## 與 Web-App 整合

Web-App 的語音 API (`/api/v1/voice/*`) 會調用這個模組提供的 Flask API：

```python
# Web-App 配置
AI_WORKER_VOICE_URL = 'http://ai-worker:8001'
```

Web-App API 流程：

1. 接收前端語音文件
2. 上傳到 MinIO
3. 調用 AI Worker Voice API
4. 返回處理結果給前端

## 依賴服務

- **MinIO**：音頻文件存儲
- **RabbitMQ**：任務隊列（Worker 模式）
- **STT Service**：語音轉文字服務
- **TTS Service**：文字轉語音服務
- **LLM Service**：語言模型服務

## 錯誤處理

### 1. 服務不可用

- 提供降級回應
- 記錄錯誤日誌
- 返回友善錯誤訊息

### 2. 任務處理失敗

- 拒絕 RabbitMQ 消息（不重新入隊）
- 發送錯誤回應到回應隊列
- 記錄詳細錯誤信息

## 監控與日誌

### 1. 健康檢查

```bash
curl http://localhost:8001/health
```

### 2. 日誌格式

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 3. 關鍵指標

- API 回應時間
- 任務處理成功率
- RabbitMQ 連接狀態
- 服務可用性

## 開發注意事項

1. **Import 路徑**：使用相對路徑導入其他 app 服務
2. **錯誤處理**：所有 API 都有完整的異常處理
3. **日誌記錄**：使用結構化日誌格式
4. **資源管理**：適當關閉連接和清理資源
5. **併發處理**：Flask 使用 threaded 模式，Worker 使用 QoS 控制

## 擴展建議

1. **任務持久化**：將任務狀態存儲到數據庫
2. **結果緩存**：緩存處理結果提升性能
3. **負載均衡**：多個 Worker 實例處理任務
4. **監控告警**：整合監控系統
5. **API 版本控制**：支持多版本 API
