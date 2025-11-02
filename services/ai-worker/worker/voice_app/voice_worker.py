import os
import pika
import json
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from stt_app.stt_service import get_stt_service
from tts_app.tts_service import get_tts_service
from llm_app.llm_service import get_llm_service

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceWorker:
    def __init__(self):
        """初始化語音工作者"""
        self.rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
        self.connection = None
        self.channel = None
        
        # 服務實例
        self.stt_service = get_stt_service()
        self.tts_service = get_tts_service()
        self.llm_service = get_llm_service()
        
        # 隊列名稱
        self.stt_queue = os.environ.get("VOICE_STT_QUEUE", "voice_stt_queue")
        self.tts_queue = os.environ.get("VOICE_TTS_QUEUE", "voice_tts_queue")
        self.chat_queue = os.environ.get("VOICE_CHAT_QUEUE", "voice_chat_queue")
    
    def connect(self):
        """連接到RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host)
            )
            self.channel = self.connection.channel()
            
            # 聲明隊列
            self.channel.queue_declare(queue=self.stt_queue, durable=True)
            self.channel.queue_declare(queue=self.tts_queue, durable=True)
            self.channel.queue_declare(queue=self.chat_queue, durable=True)
            
            # 設置QoS
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info("成功連接到RabbitMQ")
            return True
            
        except Exception as e:
            logger.error("連接RabbitMQ失敗: %s", e)
            return False
    
    def process_stt_task(self, ch, method, properties, body):
        """處理STT任務"""
        try:
            task_data = json.loads(body)
            logger.info("處理STT任務: %s", task_data['task_id'])
            
            bucket_name = task_data['bucket_name']
            object_name = task_data['object_name']
            patient_id = task_data.get('patient_id', 'anonymous')
            
            # 執行語音轉文字
            transcription = self.stt_service.transcribe_audio(bucket_name, object_name)
            
            # 構建回應
            response = {
                'task_id': task_data['task_id'],
                'status': 'completed',
                'transcription': transcription,
                'duration': 3.5,  # 模擬時長
                'confidence': 0.95,  # 模擬置信度
                'patient_id': patient_id
            }
            
            # 發送回應到回應隊列（如果有指定）
            response_queue = task_data.get('response_queue')
            if response_queue:
                self.publish_response(response_queue, response)
            
            # 確認消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("STT任務完成: %s", task_data['task_id'])
            
        except Exception as e:
            logger.error("STT任務處理失敗: %s", e, exc_info=True)
            # 拒絕消息，不重新入隊
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def process_tts_task(self, ch, method, properties, body):
        """處理TTS任務"""
        try:
            task_data = json.loads(body)
            logger.info("處理TTS任務: %s", task_data['task_id'])
            
            text = task_data['text']
            patient_id = task_data.get('patient_id', 'anonymous')
            
            # 執行文字轉語音
            object_name, duration_ms = self.tts_service.synthesize_text(text)
            
            # 構建回應
            response = {
                'task_id': task_data['task_id'],
                'status': 'completed',
                'object_name': object_name,
                'duration_ms': duration_ms,
                'patient_id': patient_id
            }
            
            # 發送回應到回應隊列（如果有指定）
            response_queue = task_data.get('response_queue')
            if response_queue:
                self.publish_response(response_queue, response)
            
            # 確認消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("TTS任務完成: %s", task_data['task_id'])
            
        except Exception as e:
            logger.error("TTS任務處理失敗: %s", e, exc_info=True)
            # 拒絕消息，不重新入隊
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def process_voice_chat_task(self, ch, method, properties, body):
        """處理完整的語音聊天任務"""
        try:
            task_data = json.loads(body)
            logger.info("處理語音聊天任務: %s", task_data['task_id'])
            
            bucket_name = task_data['bucket_name']
            object_name = task_data['object_name']
            patient_id = task_data.get('patient_id', 'anonymous')
            conversation_id = task_data.get('conversation_id')
            
            # Step 1: STT - 語音轉文字
            logger.info("開始STT處理: %s", object_name)
            user_transcription = self.stt_service.transcribe_audio(bucket_name, object_name)
            logger.info("STT完成: %s", user_transcription)
            
            # Step 2: LLM - 生成AI回應
            logger.info("開始LLM處理")
            try:
                ai_response_text = self.generate_llm_response(user_transcription, patient_id, conversation_id)
            except Exception as e:
                logger.warning("LLM處理失敗，使用備用回應: %s", e)
                ai_response_text = f"我聽到您說：「{user_transcription}」。這是一個AI語音助理的回應。"
            
            logger.info("LLM完成: %s", ai_response_text)
            
            # Step 3: TTS - 文字轉語音
            logger.info("開始TTS處理")
            ai_audio_object, duration_ms = self.tts_service.synthesize_text(ai_response_text)
            logger.info("TTS完成: %s", ai_audio_object)
            
            # 構建回應
            response = {
                'task_id': task_data['task_id'],
                'status': 'completed',
                'user_transcription': user_transcription,
                'ai_response_text': ai_response_text,
                'ai_audio_object': ai_audio_object,
                'duration_ms': duration_ms,
                'conversation_id': conversation_id or 'new_conversation',
                'patient_id': patient_id
            }
            
            # 發送回應到回應隊列（如果有指定）
            response_queue = task_data.get('response_queue')
            if response_queue:
                self.publish_response(response_queue, response)
            
            # 確認消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("語音聊天任務完成: %s", task_data['task_id'])
            
        except Exception as e:
            logger.error("語音聊天任務處理失敗: %s", e, exc_info=True)
            # 拒絕消息，不重新入隊
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def generate_llm_response(self, message: str, patient_id: str, conversation_id: str) -> str:
        """
        生成LLM回應（同步版本）
        """
        # 簡化的LLM邏輯，基於關鍵詞回應
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['你好', '哈囉', 'hello', '嗨']):
            return "您好！我是您的AI健康助理，很高興為您服務。請問有什麼可以幫助您的嗎？"
        
        elif any(word in message_lower for word in ['謝謝', '感謝', '謝了']):
            return "不客氣！我很高興能夠幫助您。如果還有其他問題，請隨時告訴我。"
        
        elif any(word in message_lower for word in ['再見', '拜拜', 'bye']):
            return "再見！祝您身體健康，有需要時隨時回來找我。"
        
        elif any(word in message_lower for word in ['頭痛', '痛', '不舒服']):
            return "我理解您感到不適。建議您適當休息，如果症狀持續或加重，請儘快諮詢醫師。"
        
        elif any(word in message_lower for word in ['睡眠', '失眠', '睡不著']):
            return "良好的睡眠很重要。建議建立規律作息，避免睡前使用3C產品，如持續失眠請諮詢醫師。"
        
        elif any(word in message_lower for word in ['運動', '健身']):
            return "規律運動對健康很有益！建議每週至少150分鐘中等強度運動。請根據自己的身體狀況適量運動。"
        
        elif any(word in message_lower for word in ['飲食', '吃', '營養']):
            return "均衡飲食很重要！建議多吃蔬果、適量蛋白質，少糖少油。如有特殊飲食需求，請諮詢營養師。"
        
        else:
            return f"我聽到您說：「{message}」。作為AI健康助理，我建議保持良好生活習慣。如有健康疑慮，請諮詢專業醫師。"
    
    def publish_response(self, queue_name: str, response_data: dict):
        """發送回應到指定隊列"""
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(response_data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info("回應已發送到隊列: %s", queue_name)
        except Exception as e:
            logger.error("發送回應失敗: %s", e)
    
    def start_consuming(self):
        """開始消費任務"""
        if not self.connect():
            logger.error("無法連接到RabbitMQ，退出")
            return
        
        try:
            # 設置消費者
            self.channel.basic_consume(
                queue=self.stt_queue,
                on_message_callback=self.process_stt_task
            )
            
            self.channel.basic_consume(
                queue=self.tts_queue,
                on_message_callback=self.process_tts_task
            )
            
            self.channel.basic_consume(
                queue=self.chat_queue,
                on_message_callback=self.process_voice_chat_task
            )
            
            logger.info("語音工作者已啟動，等待任務...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("收到中斷信號，停止消費")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error("消費過程中發生錯誤: %s", e)
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ連接已關閉")

def get_voice_worker():
    """Factory function to get the VoiceWorker instance."""
    return VoiceWorker()

def main():
    """主函數"""
    worker = get_voice_worker()
    worker.start_consuming()

if __name__ == "__main__":
    main()