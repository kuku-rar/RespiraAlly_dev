# services/ai-worker/worker/llm_app/toolkits/rabbitmq_publisher.py
import pika
import os
import json
import logging

def publish_alert(user_id: str, reason: str):
    """
    發布一個緊急警示訊息到 RabbitMQ 的 alert_queue。

    Args:
        user_id (str): 觸發警示的使用者 ID。
        reason (str): 警示的原因或相關訊息。
    """
    try:
        rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
        alert_queue = os.environ.get("RABBITMQ_ALERT_QUEUE", "alert_queue")

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        # 宣告佇列，確保它存在
        channel.queue_declare(queue=alert_queue, durable=True)

        message = {
            "user_id": user_id,
            "reason": reason
        }

        # 發布訊息
        channel.basic_publish(
            exchange='',
            routing_key=alert_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 讓訊息持久化
            ))
        
        print(f" [x] 已發送警示到 RabbitMQ: {message}")
        connection.close()
        return True
    except Exception as e:
        logging.error(f" [!] 發送警示到 RabbitMQ 失敗: {e}", exc_info=True)
        return False
