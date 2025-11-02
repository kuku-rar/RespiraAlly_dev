import os
import pika
import json
import time
import logging
from llm_app.llm_service import LLMService, llm_service_instance
from llm_app.ProactiveCare.scheduler import scheduler, initialize_scheduler
from stt_app.stt_service import STTService
from tts_app.tts_service import TTSService

logging.getLogger('apscheduler').setLevel(logging.WARNING)

def initialize_database():
    """
    確保所有必要的資料庫和表格都已建立。
    這個函式可安全地重複執行。
    """
    print("--- 開始進行資料庫初始化檢查 ---", flush=True)
    try:
        from llm_app.models.chat_profile import create_profile_table_if_not_exists
        # 呼叫 SQLAlchemy 的 create_all()，它會自動檢查表格是否存在
        create_profile_table_if_not_exists()
        print("--- 資料庫初始化檢查完成 ---", flush=True)
    except ImportError as e:
        print(f"[!] 初始化錯誤：無法導入模組。請確認路徑設定。 {e}", flush=True)
    except Exception as e:
        print(f"[!] 資料庫初始化失敗: {e}", flush=True)
        print("[!] 可能是資料庫服務尚未完全就緒，稍後重試...", flush=True)
        raise

def publish_notification(message: dict, patient_id: int):
    """將訊息發佈到通知佇列。"""
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    notification_queue = os.environ.get("RABBITMQ_NOTIFICATION_QUEUE", "notifications_queue")
    try:
        message_with_id = message.copy()
        message_with_id['patient_id'] = patient_id
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=notification_queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=notification_queue,
            body=json.dumps(message_with_id),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"已發送通知: {message_with_id}", flush=True)
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"連線到 RabbitMQ 以發送通知時出錯: {e}", flush=True)
        raise


def process_text_task(task_data={}):
    """透過 llm-app 來處理文字訊息。"""
    print("建立 LLM 服務...", flush=True)
    response = llm_service_instance.generate_response(task_data=task_data)
    print(f"成功呼叫 LLM 服務。回應: {response}", flush=True)
    return response


def process_audio_task(patient_id: int, audio_duration_ms=60000, task_data={}):
    """
    透過 STT -> LLM -> TTS 管道處理音訊檔案任務。
    """
    try:
        # 步驟 1: STT - 語音轉文字
        print(f"--- 開始 STT 處理: {task_data['object_name']} ---", flush=True)
        user_transcript = STTService().transcribe_audio(task_data['bucket_name'], task_data['object_name'])
        if not user_transcript:
            raise ValueError("STT 服務未返回有效的轉錄文字")
        task_data['text'] = user_transcript  # 將轉錄文字加入 task_data
        print(f"STT 結果: {user_transcript}", flush=True)


        # 步驟 2: LLM - 產生 AI 回應
        print(f"--- 開始 LLM 處理 ---", flush=True)
        ai_response = llm_service_instance.generate_response(task_data=task_data)
        if not ai_response:
            raise ValueError("LLM 服務未返回有效的 AI 回應")
        print(f"LLM 結果: {ai_response}", flush=True)


        # 步驟 3: TTS - 文字轉語音
        print(f"--- 開始 TTS 處理 ---", flush=True)
        response_audio_url, duration_ms = TTSService().synthesize_text(ai_response)
        if not response_audio_url:
            raise ValueError("TTS 服務未返回有效的音訊物件名稱")
        print(f"TTS 結果: {response_audio_url}", flush=True)

        # 步驟 4: 發送成功通知
        notification_message = {
            "status": "completed",
            "original_file": task_data['object_name'],
            "user_transcript": user_transcript,
            "ai_response": ai_response,
            "response_audio_url": response_audio_url,
            "audio_duration_ms": duration_ms
        }
        publish_notification(notification_message, patient_id)

    except Exception as e:
        print(f"音訊處理管道中發生錯誤: {e}", flush=True)
        error_notification = {
            "status": "error",
            "original_file": task_data['object_name'],
            "error_message": str(e)
        }
        publish_notification(error_notification, patient_id)
        raise

if __name__ == '__main__':

    # 帶有重試機制的啟動檢查，確保在 postgres 容器完全就緒後再繼續
    max_retries = 5
    retry_delay = 5
    for i in range(max_retries):
        try:
            initialize_database()
            break # 初始化成功，跳出循環
        except Exception as e:
            if i < max_retries - 1:
                print(f"初始化失敗，將在 {retry_delay} 秒後重試 ({i+1}/{max_retries})...", flush=True)
                time.sleep(retry_delay)
            else:
                print("達到最大重試次數，初始化失敗，程式即將退出。", flush=True)
                exit(1) # 重試全部失敗後，退出程式
    
    # 在背景執行緒中啟動 APScheduler
    try:
        # 1. 呼叫初始化函式，將任務新增到排程器中
        initialize_scheduler()
        # 2. 啟動排程器
        scheduler.start()
        print('✅ [AI Worker] 排程服務已成功啟動。', flush=True)
    except Exception as e:
        print(f"❌ [AI Worker] 啟動排程服務失敗: {e}", flush=True)

    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    task_queue = os.environ.get("RABBITMQ_QUEUE", "task_queue")

    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue=task_queue, durable=True)
            print(' [*] AI Worker 正在等待訊息。按 CTRL+C 離開', flush=True)

            def callback(ch, method, properties, body):
                task_data = json.loads(body)
                print(f"\n [x] 收到任務: {task_data}", flush=True)
                try:
                    patient_id = task_data.get('patient_id')
                    if not patient_id:
                        raise ValueError("任務資料缺少 'patient_id'")

                    if 'text' in task_data:
                        print(f" [*] 開始為病患 {patient_id} 處理文字任務...", flush=True)
                        llm_response = process_text_task(task_data=task_data)
                        notification = {
                            "status": "completed",
                            "user_transcript": task_data['text'],
                            "ai_response": llm_response
                        }
                        publish_notification(notification, patient_id)
                    elif 'bucket_name' in task_data and 'object_name' in task_data:
                        audio_duration_ms = task_data.get('duration_ms')
                        print(f" [*] 開始為病患 {patient_id} 處理音訊任務...", flush=True)
                        process_audio_task(patient_id, audio_duration_ms, task_data=task_data)
                    else:
                        print(f" [!] 未知的任務格式: {task_data}", flush=True)
                    print(f" [✔] 任務成功完成。", flush=True)
                except Exception as e:
                    print(f" [!] 處理任務時出錯: {e}", flush=True)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=task_queue, on_message_callback=callback)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"與 RabbitMQ 的連線失敗: {e}。5 秒後重試...", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"發生未預期的錯誤: {e}。正在重啟消費者...", flush=True)
            time.sleep(5)
