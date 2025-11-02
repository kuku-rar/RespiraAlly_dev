"""
Task Mapper

Converts between RabbitMQ task data and domain AITask objects.
"""

from typing import Dict, Any
from ..domain.ai_task import AITask, TaskType


class TaskMapper:
    """Maps between external task data and domain AITask objects"""

    @staticmethod
    def rabbitmq_to_domain(task_data: Dict[str, Any]) -> AITask:
        """Convert RabbitMQ task data to domain AITask"""
        patient_id = str(task_data.get('patient_id'))
        line_user_id = task_data.get('line_user_id')

        # Determine task type based on available data
        if task_data.get('text') and not task_data.get('bucket_name'):
            # Text-only task
            return AITask.create_text_task(
                patient_id=patient_id,
                input_text=task_data['text'],
                line_user_id=line_user_id
            )
        elif task_data.get('bucket_name') and task_data.get('object_name'):
            # Audio task
            return AITask.create_audio_task(
                patient_id=patient_id,
                audio_bucket=task_data['bucket_name'],
                audio_object=task_data['object_name'],
                audio_duration_ms=task_data.get('duration_ms'),
                line_user_id=line_user_id
            )
        else:
            raise ValueError(f"Invalid task data format: {task_data}")

    @staticmethod
    def domain_to_notification(ai_task: AITask) -> Dict[str, Any]:
        """Convert domain AITask to notification payload"""
        return ai_task.create_notification_payload()